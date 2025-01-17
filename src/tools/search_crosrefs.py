import pandas as pd
from typing import List
import time
from tqdm import tqdm
import requests

def get_author_names(authorships):
    authors = []
    for authorship in authorships:
        if 'author' in authorship:
            author = authorship['author']
            name = author.get('display_name', 'Unknown Author')
            authors.append(name)
    return '; '.join(authors)  # Join authors with semicolon

def search_openalex(queries: List[str], results_per_query: int = 10) -> pd.DataFrame:
    all_results = []
    
    for query in tqdm(queries, desc="Processing queries"):
        try:
            url = f"https://api.openalex.org/works?search={query}&per_page={results_per_query}"
            response = requests.get(url)
            data = response.json()
            
            for work in data.get("results", []):
                result = {
                    'query': query,
                    'title': work.get('title', 'No title available'),
                    'doi': work.get('doi', 'N/A'),
                    'authors': get_author_names(work.get('authorships', [])),
                    'abstract': work.get('abstract', 'N/A'),
                    'publication_year': work.get('publication_year', 'N/A'),
                    'cited_by_count': work.get('cited_by_count', 0)
                }
                all_results.append(result)
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            continue
    
    df = pd.DataFrame(all_results)
    return df

if __name__ == "__main__":
    # Example queries
    queries = [
        "job satisfaction",
        "work performance",
        "employee engagement",
        "employee turnover"
    ]
    
    # Search and create DataFrame
    results_df = search_openalex(queries, results_per_query=20)
    
    # Save to CSV
    output_file = "openalex_results.csv"
    results_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nResults saved to {output_file}")
    print(f"Total results: {len(results_df)}")
    print("\nResults per query:")
    print(results_df['query'].value_counts())