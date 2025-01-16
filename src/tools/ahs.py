import requests
import time
import pandas as pd
from typing import List, Dict, Optional
import os
from pathlib import Path
import csv
from datetime import datetime
from urllib.parse import quote_plus
import time
from tqdm import tqdm


"""
AHSS - Academic Hyper Search System
This tool allows you to search for academic resources using the CrossRef API, CORE API, and other sources.
You can search for resources based on keywords, authors, publication dates, and more.
It combines results and stores them to database
AI then process the data, and creates a list for trying to find the best resources for the user
"""
class CrossRefHandler:
    def __init__(self):
        self.base_url = "https://api.crossref.org/works"
        self.headers = {
            "User-Agent": "YourInstitution/1.0 (mailto:c.karakostas10@gmail.com)"  # Replace with your details
        }
        self.download_path = Path("downloads")
        self.download_path.mkdir(exist_ok=True)
        
    def calculate_relevance_score(self, work: Dict, keywords: List[str]) -> float:
        """
        Calculate relevance score based on keyword matches and recency
        
        Args:
            work: Work metadata from CrossRef
            keywords: List of search keywords
        """
        score = 0
        
        # Get text fields to search in
        title = work.get('title', [''])[0].lower()
        abstract = work.get('abstract', '').lower()
        
        # Count keyword matches
        for keyword in keywords:
            keyword = keyword.lower()
            if keyword in title:
                score += 3  # Higher weight for title matches
            if keyword in abstract:
                score += 2  # Medium weight for abstract matches
                
        # Add recency bonus (max 2 points for current year)
        pub_year = work.get('published-print', {}).get('date-parts', [[0]])[0][0]
        if pub_year:
            current_year = datetime.now().year
            year_diff = current_year - pub_year
            recency_score = max(0, 2 - (year_diff * 0.2))  # Decrease score by 0.2 for each year old
            score += recency_score
            
        return round(score, 2)
 
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
                'filter=has-full-text:true,is-open-access:true'
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
                            'authors': '; '.join([author.get('given', '') + ' ' + author.get('family', '')
                                            for author in work.get('author', [])]),
                            'abstract': work.get('abstract', ''),
                            'keywords': keyword,  # Original search keyword
                            'relevance_score': self.calculate_relevance_score(work, [keyword]),
                            'pdf_url': doi_url,
                            'publisher': work.get('publisher', ''),
                            'journal': work.get('container-title', [''])[0],
                            'type': work.get('type', '')
                        }
                        
                        keyword_results.append(result)
                    
                    offset += rows
                    time.sleep(1)  # Respect rate limits
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error searching CrossRef API for keyword '{keyword}': {e}")
                    break
            
            print(f"\nFound {len(keyword_results)} results for '{keyword}'")
            all_results.extend(keyword_results)
            time.sleep(2)  # Delay between keywords
                    
        # Convert to DataFrame and remove duplicates
        df = pd.DataFrame(all_results)
        df.to_csv("trex.csv", index=False)
        
        # Sort by relevance score
        df = df.sort_values('relevance_score', ascending=False)
        
        print(f"\nTotal results after removing duplicates: {len(df)}")
        print("\nResults per keyword:")
        print(df['keywords'].value_counts())
        
        return df
    
    def save_results(self, df: pd.DataFrame, output_file: str = "crossref_results.csv"):
        """Save results to CSV file"""
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Results saved to {output_file}")

def main():
    handler = CrossRefHandler()
    
    # Define your search keywords
    keywords = [
        "job satisfaction",
        "work performance",
        "employee engagement",
        "employee turnover"       
    ]
    
    # Search for resources
    results_df = handler.search_resources(
        keywords=keywords,
        results_per_keyword=50,
        from_year=2020
    )
    
    # Save results
    handler.save_results(results_df)
    

if __name__ == "__main__":
    main()