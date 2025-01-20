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
from src.config import *

import requests, time, os, csv, json


"""
AHSS - Academic Hyper Search System
This tool allows you to search for academic resources using the CrossRef API, CORE API, and OpenAlex API.
You can search for resources based on keywords, authors, publication dates, and more.
This tool stores data in database
AI then process the data, and creates a list for trying to find the best resources for the user

Classes:
- AHSS: Abstract class for Academic Hyper Search System
- CrossRefHandler: Class for searching academic resources using CrossRef API
- OpenAlexHandler: Class for searching academic resources using OpenALEX API
- CoreAPIHandler: Class for searching academic resources using Core API
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
            self.keywords = get_keywords()
            self.search_queries = get_search_queries()
            self.projname = SystemPars().project_name
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error loading keywords and search queries: {e}")

        

    def calculate_relevance_score(self, work: Dict) -> float:
        try:
            score = 0
            # Standardize title handling
            title = (work.get('title', [''])[0].lower() 
                    if isinstance(work.get('title'), list) 
                    else str(work.get('title', '')).lower())
            
            # Standardize abstract handling
            abstract = str(work.get('abstract', '')).lower()
            
            # Get keywords from instance
            keywords = self.keywords
            
            # Calculate keyword matches
            for keyword in keywords:
                keyword = keyword.lower()
                if keyword in title:
                    score += 3
                if keyword in abstract:
                    score += 2
            
            # Calculate year score
            pub_year = (
                work.get('published-print', {}).get('date-parts', [[0]])[0][0] 
                if 'published-print' in work 
                else work.get('publication_year', work.get('yearPublished', 0))
            )
            
            if pub_year:
                current_year = datetime.now().year
                year_diff = current_year - int(pub_year)
                recency_score = max(0, 2 - (year_diff * 0.2))
                score += recency_score
            
            # Calculate citation score
            citations = int(work.get('is-referenced-by-count', 
                          work.get('cited_by_count', 
                          work.get('citations', 0))))
            citation_score = min(2, citations / 100)
            score += citation_score
            
            return round(score, 2)
            
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, 
                        f"Error calculating relevance score: {e}")
            return 0.0

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
                                'relevance_score': self.calculate_relevance_score(work),
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

            # save the results to database table metadata
            to_db_crossref = SaveMetaData()
            to_db_crossref.save_papers_metadata(df, 'crossref', self.projname)
            logger.info(ScriptIdentifier.AHSS, f"Saved {len(df)} results to database table metadata for CrossRef")

        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error saving CrossRef results: {e}")
    
# OpenALEX API Handler Class so we can search for academic resources in the OpenALEX database
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
                            'relevance_score': self.calculate_relevance_score(work),
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

                # save the results to database table metadata
                to_db_openalex = SaveMetaData()
                to_db_openalex.save_papers_metadata(df, 'openalex', self.projname)
                logger.info(ScriptIdentifier.AHSS, f"Saved {len(df)} results to database table metadata for OpenALEX")

            except Exception as e:
                logger.error(ScriptIdentifier.AHSS, f"Error saving OpenALEX results: {e}")

# Core API Handler Class so we can search for academic resources in the Core database
class CoreAPIHandler(AHSS):
    def __init__(self):
        super().__init__()
        logger.info(ScriptIdentifier.AHSS, "Initializing Core API Handler")
        try:
            self.api_key = os.getenv('CORE_API_KEY')

            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            logger.info(ScriptIdentifier.AHSS, "Core API Handler initialized")
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error initializing Core API Handler: {e}")
        
    def search_specific_papers(self) -> List[Dict]:
        search_queries = self.search_queries
        required_keywords = self.keywords
        papers = []
        
        # Create enhanced query with required keywords
        for query in search_queries:
            # Combine query with required keywords using OR
            keyword_query = " OR ".join(f'"{keyword}"' for keyword in required_keywords)
            enhanced_query = f'({query}) AND ({keyword_query})'
            
            payload = {
                "q": enhanced_query,
                "limit": 50,
                "filters": {
                    "year": {"gte": 2015},
                    "types": ["journal-article"],
                    "lang": "en"
                }
            }
            
            try:
                logger.debug(ScriptIdentifier.AHSS, f"Sending request with enhanced query: {enhanced_query}")
                response = requests.post(
                    "https://api.core.ac.uk/v3/search/works",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                response_data = response.json()
                
                if 'results' in response_data:
                    # Filter results that contain at least one required keyword
                    filtered_results = []
                    for result in response_data['results']:
                        title = str(result.get('title', '')).lower()
                        abstract = str(result.get('abstract', '')).lower()
                        
                        # Check if any required keyword is present
                        if any(keyword.lower() in title or keyword.lower() in abstract 
                            for keyword in required_keywords):
                            filtered_results.append(result)
                    
                    papers.extend(filtered_results)
                    logger.info(ScriptIdentifier.AHSS, 
                            f"Found {len(filtered_results)} relevant papers for query: {query}")
                else:
                    logger.error(ScriptIdentifier.AHSS, f"Unexpected response structure for query: {query}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(ScriptIdentifier.AHSS, f"Error searching Core API for query '{query}': {e}")
                continue

            
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

            # save the results to database table metadata
            to_db_coreapi = SaveMetaData()
            to_db_coreapi.save_papers_metadata(df, 'coreapi', self.projname)
            logger.info(ScriptIdentifier.AHSS, f"Saved {len(df)} results to database table metadata for Core API")
            
        except Exception as e:
            logger.error(ScriptIdentifier.AHSS, f"Error saving Core API results: {e}")
            return []




