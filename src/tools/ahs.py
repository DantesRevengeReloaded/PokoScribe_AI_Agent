import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus
from tqdm import tqdm
from abc import ABC, abstractmethod
from db_ai.ai_db_manager import *
import requests, time, os, csv


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
        logger.info(ScriptIdentifier.AHSS, "AHSS initializing.")
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

    def calculate_relevance_score(self, work: Dict, keywords: List[str]) -> float:
        score = 0
        title = work.get('title', [''])[0].lower() if isinstance(work.get('title'), list) else str(work.get('title', '')).lower()
        abstract = str(work.get('abstract', '')).lower()
        
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
                        keywords: List[str],
                        results_per_keyword: int = 50,
                        from_year: Optional[int] = None) -> pd.DataFrame:
        """
        Search for academic resources using CrossRef API
        
        Args:
            keywords: List of search keywords
            results_per_keyword: Maximum number of results per keyword
            from_year: Minimum publication year
        """
        all_results = []
        
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
                    
        # Convert to DataFrame and remove duplicates
        df = pd.DataFrame(all_results)
        # Sort by relevance score
        df = df.sort_values('relevance_score', ascending=False)
        return df
    

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

    def search_resources(self, keywords: List[str], results_per_keyword: int = 50) -> pd.DataFrame:
            all_results = []
            
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
                    
            
            df = pd.DataFrame(all_results)
            fh = "openalex_result.csv"
            df.to_csv(fh, index=False, encoding='utf-8')
            return df


