import requests

query = "job satisfaction work performance"
url = f"https://api.crossref.org/works?query={query}&rows=10"
response = requests.get(url)
data = response.json()

for item in data["message"]["items"]:
    print(f"Title: {item['title'][0]}")
    print(f"DOI: {item.get('DOI', 'N/A')}")
    print(f"Authors: {[author['given'] + ' ' + author['family'] for author in item.get('author', [])]}")
    print(f"Abstract: {item.get('abstract', 'N/A')}")
    print("-" * 50)