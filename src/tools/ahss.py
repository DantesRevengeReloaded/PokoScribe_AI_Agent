import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus
from tqdm import tqdm
from abc import ABC, abstractmethod

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from db_ai.ai_db_manager import *

import requests, time, os, csv, json
import src.tools.tools_config
from src.tools.tools_config import *




"""
AHSS - Academic Hyper Search System
This tool allows you to search for academic resources using the CrossRef API, CORE API, and other sources.
You can search for resources based on keywords, authors, publication dates, and more.
It combines results and stores them to database
AI then process the data, and creates a list for trying to find the best resources for the user
"""

load_dotenv('.env')
logger = PokoLogger()

class AHSS(ABC):
    def __init__(self):

        self.columns = [
            'title',
            'doi',
            'year',
            'authors',
            'abstract',
            'keywords',
            'relevance_score',
            'pdf_url',
            'publisher',
            'journal',
            'type',
            'cited_by_count'
        ]
        try:
        # Load keywords and search queries from config
            self.keywords = tools_config.get_keywords()
            self.search_queries = tools.tools_config.get_search_queries()
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error loading keywords and search queries: {e}")
        

    def calculate_relevance_score(self, work: Dict) -> float:
        score = 0
        title = work.get('title', [''])[0].lower() if isinstance(work.get('title'), list) else str(work.get('title', '')).lower()
        abstract = str(work.get('abstract', '')).lower()
        keywords = self.keywords

        for keyword in keywords:
            keyword = keyword.lower()
            if keyword in title:
                score += 3
            if keyword in abstract:
                score += 2
                
        pub_year = work.get('published-print', {}).get('date-parts', [[0]])[0][0] if 'published-print' in work else work.get('publication_year', 0)
        if pub_year:
            current_year = datetime.now().year
            year_diff = current_year - int(pub_year)
            recency_score = max(0, 2 - (year_diff * 0.2))
            score += recency_score
            
        citations = work.get('is-referenced-by-count', work.get('cited_by_count', 0))
        citation_score = min(2, int(citations) / 100)
        score += citation_score
            
        return round(score, 2)

    @abstractmethod
    def search_resources(self, keywords: List[str], results_per_keyword: int) -> pd.DataFrame:
        pass

# CrossRef API Handler Class so we can search for academic resources in the CrossRef database
class CrossRefHandler(AHSS):
    def __init__(self):
        super().__init__()

        my_mail = os.getenv('MY_MAIL')

        self.base_url = "https://api.crossref.org/works"
        self.headers = {
            "User-Agent": f"PokoScribe/1.0 (mailto:{my_mail})"  # Replace with your details
        }
        self.download_path = Path("downloads")
        self.download_path.mkdir(exist_ok=True)
        
    def search_resources(self, 
                        results_per_keyword: int = 50,
                        from_year: Optional[int] = None) -> pd.DataFrame:
        """
        Search for academic resources using CrossRef API
        
        Args:
            results_per_keyword: Maximum number of results per keyword
            from_year: Minimum publication year
        """
        all_results = []

        keywords = self.keywords

        logger.info(ScriptIdentifier.AHSS, "Searching for academic resources using CrossRef API")
        try:
            for keyword in tqdm(keywords, desc="Processing keywords"):
                keyword_results = []
                offset = 0
                rows = 20  # CrossRef recommended page size
                
                query_parts = [
                f'query.bibliographic="{quote_plus(keyword)}"',
                'select=DOI,title,abstract,author,published-print,type,URL,link,is-referenced-by-count'
            ]
                
                if from_year:
                    query_parts.append(f'from-pub-date:{from_year}')
                    
                while len(keyword_results) < results_per_keyword:
                    try:
                        url = f"{self.base_url}?{'+'.join(query_parts)}&rows={rows}&offset={offset}"
                        response = requests.get(url, headers=self.headers)
                        response.raise_for_status()
                        data = response.json()
                        
                        works = data['message']['items']
                        if not works:
                            break
                            
                        # Process each work
                        for work in works:
                            if len(keyword_results) >= results_per_keyword:
                                break
                                
                            # Get DOI URL if available
                            doi_url = next((link['URL'] for link in work.get('link', [])
                                        if link.get('content-type', '').startswith('application/pdf')), None)
                            
                            result = {
                                'title': work.get('title', [''])[0],
                                'doi': work.get('DOI', ''),
                                'year': work.get('published-print', {}).get('date-parts', [[0]])[0][0],
                                'authors': '; '.join([f"{author.get('given', '')} {author.get('family', '')}" 
                                                for author in work.get('author', [])]),
                                'abstract': work.get('abstract', ''),
                                'keywords': keyword,
                                'relevance_score': self.calculate_relevance_score(work, [keyword]),
                                'pdf_url': doi_url,
                                'publisher': work.get('publisher', ''),
                                'journal': work.get('container-title', [''])[0],
                                'type': work.get('type', ''),
                                'cited_by_count': work.get('is-referenced-by-count', 0)
                            }

                            keyword_results.append(result)
                        
                        offset += rows
                        time.sleep(1)  # Respect rate limits
                        
                    except requests.exceptions.RequestException as e:
                        print(f"Error searching CrossRef API for keyword '{keyword}': {e}")
                        break
                
                all_results.extend(keyword_results)
                time.sleep(2)  # Delay between keywords
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error searching CrossRef API: {e}")

        try:         
            # Convert to DataFrame and remove duplicates
            df = pd.DataFrame(all_results)

            # Remove duplicates and sort by relevance
            df = df.drop_duplicates()
            df = df.sort_values('relevance_score', ascending=False)

            # Save results to CSV
            fh = "crossref_result.csv"
            df.to_csv(fh, index=False, encoding='utf-8')
            logger.info(ScriptIdentifier.AHSS, f"Saved CrossRef results to {fh}")
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error saving CrossRef results: {e}")
    

class OpenAlexHandler(AHSS):
    def __init__(self):
        super().__init__()

    def get_author_names(self, authorships):
        authors = []
        for authorship in authorships:
            if 'author' in authorship:
                author = authorship['author']
                name = author.get('display_name', 'Unknown Author')
                authors.append(name)
        return '; '.join(authors)  # Join authors with semicolon

    def search_resources(self, results_per_keyword: int = 50) -> pd.DataFrame:
            all_results = []
            keywords = self.keywords

            logger.info(ScriptIdentifier.AHSS, "Searching for academic resources using OpenALEX API")
            
            for keyword in tqdm(keywords, desc="Processing keywords"):
                try:
                    url = f"https://api.openalex.org/works?search={keyword}&per_page={results_per_keyword}"
                    response = requests.get(url)
                    data = response.json()
                    
                    for work in data.get("results", []):
                        result = {
                            'title': work.get('title', 'No title available'),
                            'doi': work.get('doi', 'N/A'),
                            'year': work.get('publication_year', 'N/A'),
                            'authors': self.get_author_names(work.get('authorships', [])),
                            'abstract': work.get('abstract', 'N/A'),
                            'keywords': keyword,
                            'relevance_score': self.calculate_relevance_score(work, [keyword]),
                            'pdf_url': work.get('pdf_url', 'N/A'),
                            'publisher': work.get('publisher', 'N/A'),
                            'journal': work.get('journal', 'N/A'),
                            'type': work.get('type', 'N/A'),
                            'cited_by_count': work.get('cited_by_count', 0)
                        }
                        all_results.append(result)
                        time.sleep(1)
                except requests.exceptions.RequestException as e:
                    print(f"Error searching OpenALEX API for keyword '{keyword}': {e}")
                    break
                    
            try:
                # Convert to DataFrame and remove duplicates
                df = pd.DataFrame(all_results)
                df = df.drop_duplicates()
                df = df.sort_values('relevance_score', ascending=False)

                fh = "openalex_result.csv"
                df.to_csv(fh, index=False, encoding='utf-8')
                logger.info(ScriptIdentifier.AHSS, f"Saved OpenALEX results to {fh}")
            except Exception as e:
                logger.error(ScriptIdentifier.AHSS, f"Error saving OpenALEX results: {e}")


class CoreAPIHandler(AHSS):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('CORE_API_KEY')

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def search_specific_papers(self) -> List[Dict]:
        search_queries = self.search_queries
        required_keywords = self.keywords
        papers = []
        
        logger.debug(ScriptIdentifier.AHSS, f"Starting search with queries: {search_queries}")
        logger.debug(ScriptIdentifier.AHSS, f"Required keywords: {required_keywords}")
        
        for query in search_queries:
            # Add required keywords to query
            enhanced_query = f"{query} AND ({' OR '.join(required_keywords)})"
            payload = {
                "q": enhanced_query,
                "limit": 50,
                "filters": {
                    "yearPublished": {"gte": 2015},
                    "downloadAllowed": True,
                    "hasFullText": True,
                    "language": "en",
                    "documentType": ["article", "journal article"]
                }
            }
            
            try:
                response = requests.post(
                    "https://api.core.ac.uk/v3/search/works",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                # Fix: Get data from response.json()
                response_data = response.json()
                if 'data' not in response_data:
                    logger.error(ScriptIdentifier.AHSS, f"No data field in response for query: {query}")
                    continue
                    
                papers.extend(response_data['data'])  # Fix: Use response_data instead of papers
                logger.info(ScriptIdentifier.AHSS, f"Found {len(response_data['data'])} papers for query: {query}")
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(ScriptIdentifier.AHSS, f"Error searching Core API for query '{query}': {e}")
                continue  # Changed break to continue to try other queries
            
        logger.info(ScriptIdentifier.AHSS, f"Total papers found: {len(papers)}")
        metadata = []
            
        for paper in papers:
            try:
                metadata_entry = {
                    'title': paper.get('title', 'No title available'),
                    'doi': paper.get('doi', 'N/A'),
                    'year': paper.get('yearPublished', 'N/A'),
                    'authors': '; '.join(a.get('name', 'Unknown Author') for a in paper.get('authors', [])),
                    'abstract': paper.get('abstract', 'N/A'),
                    'keywords': paper.get('keywords', 'N/A'),
                    'relevance_score': self.calculate_relevance_score({
                            'title': paper.get('title', ''),
                            'abstract': paper.get('abstract', ''),
                            'published-print': {'date-parts': [[paper.get('yearPublished', 0)]]},
                            'is-referenced-by-count': paper.get('citations', 0)
                        }),
                    'pdf_url': paper.get('downloadUrl', 'N/A'),
                    'publisher': paper.get('publisher', 'N/A'),
                    'journal': paper.get('journal', 'N/A'),
                    'type': paper.get('type', 'N/A'),
                    'cited_by_count': paper.get('citations', 0)
                }
                metadata.append(metadata_entry)
            except Exception as e:
                logger.error(ScriptIdentifier.AHSS, f"Error processing paper metadata: {e}")
                continue
        
        if not metadata:
            logger.warning(ScriptIdentifier.AHSS, "No metadata collected from papers")
            return []
            
        try:
            df = pd.DataFrame(metadata)
            df = df.drop_duplicates()
            df = df.sort_values('relevance_score', ascending=False)
            
            fh = "coreapi_result.csv"
            df.to_csv(fh, index=False, encoding='utf-8')
            logger.info(ScriptIdentifier.AHSS, f"Saved {len(df)} results to {fh}")
            return metadata
            
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error saving Core API results: {e}")
            return []



    def download_papers(self, papers: List[Dict], 
                       output_dir: str = "psychology_papers") -> None:
        """Download selected papers and save metadata"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save papers metadata first
        metadata_path = os.path.join(output_dir, "papers_metadata.json")
        self._save_metadata(papers, metadata_path)
        
        for paper in papers:
            if not paper.get('downloadUrl'):
                print(f"No download URL for paper: {paper.get('title', 'unknown')}")
                continue
                
            try:
                # Create filename from title
                safe_title = "".join(
                    x for x in paper['title'] 
                    if x.isalnum() or x in [' ', '-', '_']
                )
                filename = f"{safe_title[:100]}.pdf"
                filepath = os.path.join(output_dir, filename)
                
                # Get the download URL
                download_url = paper['downloadUrl']
                
                # Make authenticated request to download
                response = requests.get(
                    download_url,
                    headers=self.headers,  # Include API key in headers
                    stream=True,
                    allow_redirects=True  # Follow redirects if any
                )
                
                # If we get a redirect, follow it with authentication
                if response.history:
                    final_url = response.url
                    response = requests.get(
                        final_url,
                        headers=self.headers,
                        stream=True
                    )
                
                response.raise_for_status()
                
                # Check if we actually got a PDF
                content_type = response.headers.get('content-type', '')
                if 'application/pdf' not in content_type.lower():
                    print(f"Warning: Downloaded content for {safe_title} may not be a PDF")
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            
                print(f"Successfully downloaded: {filename}")
                
                # Add a small delay between downloads
                time.sleep(2)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"Access denied for paper: {paper.get('title', 'unknown')}")
                    print("This paper might require institutional access or subscription")
                elif e.response.status_code == 429:
                    print("Rate limit reached. Waiting before next download...")
                    time.sleep(60)  # Wait for a minute before continuing
                else:
                    print(f"HTTP Error downloading {paper.get('title', 'unknown')}: {e}")
            except Exception as e:
                print(f"Error downloading {paper.get('title', 'unknown')}: {e}")
                continue

