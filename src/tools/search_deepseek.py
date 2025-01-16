import requests
from typing import List, Dict
import os
from datetime import datetime
import json
from dotenv import load_dotenv
import time
import csv

class TargetedPaperDownloader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def search_specific_papers(self) -> List[Dict]:
        """
        Search for specific papers about worker psychology and performance
        """
        search_queries = [
            "worker satisfaction business performance",
            "employee psychology productivity",
            "job satisfaction organizational performance",
            "workplace psychology business metrics",
            "employee wellbeing productivity",
            "employee satisfaction",
            "job satisfaction"
        ]
        
        required_keywords = [
            "job satisfaction",
            "employee performance",
            "business outcome",
            "productivity",
            "workplace psychology",
            "employee satisfaction",
        ]
        
        all_results = []
        
        for query in search_queries:
            payload = {
                "q": query,
                "limit": 50,
                "filters": {
                    "yearPublished": {"gte": 2018},
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
                data = response.json()
                
                if 'results' in data:
                    # Filter results based on required keywords
                    filtered_results = self._filter_relevant_papers(
                        data['results'], required_keywords
                    )
                    all_results.extend(filtered_results)
                else:
                    print(f"No results found for query: {query}")
                
            except requests.exceptions.RequestException as e:
                print(f"API Error with query '{query}': {e}")
            except Exception as e:
                print(f"Error processing query '{query}': {e}")
                continue
        
        # Remove duplicates and sort by relevance
        unique_results = self._remove_duplicates(all_results)
        sorted_results = sorted(
            unique_results, 
            key=lambda x: x.get('relevance_score', 0), 
            reverse=True
        )
        
        return sorted_results

    def _filter_relevant_papers(self, 
                              papers: List[Dict], 
                              keywords: List[str]) -> List[Dict]:
        """Filter papers to ensure they match our specific criteria"""
        relevant_papers = []
        
        for paper in papers:
            # Safely get abstract and title, defaulting to empty string if None
            abstract = (paper.get('abstract') or '').lower()
            title = (paper.get('title') or '').lower()
            
            # Check if paper has minimum required keywords
            keyword_count = sum(1 for keyword in keywords 
                              if keyword.lower() in abstract 
                              or keyword.lower() in title)
            
            # Paper must have at least 2 of our required keywords
            if keyword_count >= 2:
                # Add relevance score
                paper['relevance_score'] = self._calculate_relevance(
                    paper, keywords
                )
                relevant_papers.append(paper)
        
        return relevant_papers

    def _calculate_relevance(self, paper: Dict, keywords: List[str]) -> float:
        """Calculate relevance score for paper"""
        score = 0.0
        abstract = (paper.get('abstract') or '').lower()
        title = (paper.get('title') or '').lower()
        
        # Keywords in title are worth more
        for keyword in keywords:
            if keyword.lower() in title:
                score += 2.0
            if keyword.lower() in abstract:
                score += 1.0
        
        # Recent papers get bonus
        year = paper.get('yearPublished') or 0
        if year >= 2022:
            score += 1.5
        elif year >= 2020:
            score += 1.0
        
        # Citations indicate impact
        citations = paper.get('citations', 0) or 0
        score += min(citations / 100, 2.0)
        
        return score

    def _remove_duplicates(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on title"""
        seen_titles = set()
        unique_papers = []
        
        for paper in papers:
            title = paper.get('title', '').lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
                
        return unique_papers

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
                
                # Verify if the URL is accessible
                response = requests.head(
                    download_url,
                    headers=self.headers,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    print(f"Access denied for paper: {safe_title}")
                    continue
                
                # Download the PDF
                response = requests.get(
                    download_url,
                    headers=self.headers,
                    stream=True,
                    allow_redirects=True
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

    def _save_metadata(self, papers: List[Dict], filepath: str) -> None:
        """Save papers metadata for future reference"""
        metadata = []
        
        for paper in papers:
            metadata.append({
                'title': paper.get('title'),
                'authors': [a.get('name') for a in paper.get('authors', [])],
                'year': paper.get('yearPublished'),
                'journal': paper.get('journal'),
                'abstract': paper.get('abstract'),
                'relevance_score': paper.get('relevance_score'),
                'citations': paper.get('citations'),
                'download_url': paper.get('downloadUrl')
            })
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

def main():
    load_dotenv('.env')    
    api_key = os.getenv('CORE_API_KEY')
    if not api_key:
        print("Please set your CORE_API_KEY environment variable")
        return
        
    downloader = TargetedPaperDownloader(api_key)
    
    # Search for specific papers
    papers = downloader.search_specific_papers()
    
    if not papers:
        print("No papers found matching the criteria")
        return
        
    # Print found papers before downloading
    print(f"\nFound {len(papers)} relevant papers:")
    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Relevance Score: {paper.get('relevance_score', 0):.2f}")
        print(f"   Year: {paper.get('yearPublished', 'Unknown')}")
        print(f"   Citations: {paper.get('citations', 0)}")
    
    # Ask user which papers to download
    try:
        indices = input("\nEnter the numbers of papers to download (comma-separated): ")
        selected_indices = [int(i.strip()) - 1 for i in indices.split(',')]
        selected_papers = [papers[i] for i in selected_indices if i < len(papers)]
        
        if selected_papers:
            downloader.download_papers(selected_papers)
        else:
            print("No valid papers selected")
    except Exception as e:
        print(f"Error processing selection: {e}")

if __name__ == "__main__":
    main()