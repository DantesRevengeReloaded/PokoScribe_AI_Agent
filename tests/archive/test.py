import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse
from time import sleep

def download_paper(doi, scihub_url="https://sci-hub.se", download_dir="downloads"):
    """
    Download a scientific paper from Sci-Hub using its DOI.
    First searches for the paper on Sci-Hub's interface, then downloads the PDF.
    
    Args:
        doi (str): The DOI of the paper to download
        scihub_url (str): The base URL for Sci-Hub
        download_dir (str): Directory to save downloaded papers
    
    Returns:
        bool: True if download was successful, False otherwise
    """
    # Clean inputs
    doi = doi.strip()
    if not scihub_url.startswith(('http://', 'https://')):
        scihub_url = f"https://{scihub_url}"
    scihub_url = scihub_url.rstrip('/')
    
    # Create download directory
    os.makedirs(download_dir, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # First, get the search page
        search_url = f"{scihub_url}/{doi}"
        print(f"Searching: {search_url}")
        
        response = requests.get(search_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the download button or link
        # Try multiple possible selectors as Sci-Hub's HTML structure might vary
        download_button = (
            soup.find('button', string=lambda s: s and 'download' in s.lower()) or
            soup.find('a', string=lambda s: s and 'download' in s.lower()) or
            soup.find('a', {'href': lambda x: x and x.endswith('.pdf')}) or
            soup.find('embed', {'type': 'application/pdf'}) or
            soup.find('iframe', {'id': 'pdf'})
        )
        
        if not download_button:
            print("Could not find PDF download link")
            return False
            
        # Get the PDF URL
        pdf_url = None
        if 'href' in download_button.attrs:
            pdf_url = download_button['href']
        elif 'src' in download_button.attrs:
            pdf_url = download_button['src']
        else:
            # If no direct link, try to find it in the page
            embed = soup.find('embed', {'type': 'application/pdf'})
            if embed and 'src' in embed.attrs:
                pdf_url = embed['src']
        
        if not pdf_url:
            print("Could not extract PDF URL")
            return False
            
        # Handle relative URLs
        if not pdf_url.startswith(('http://', 'https://')):
            if pdf_url.startswith('//'):
                pdf_url = f"https:{pdf_url}"
            else:
                pdf_url = urljoin(scihub_url, pdf_url)
        
        print(f"Found PDF URL: {pdf_url}")
        
        # Download the PDF
        pdf_response = requests.get(pdf_url, headers=headers, timeout=30)
        pdf_response.raise_for_status()
        
        # Save the file
        filename = os.path.join(download_dir, f"{doi.replace('/', '_')}.pdf")
        with open(filename, 'wb') as f:
            f.write(pdf_response.content)
        
        print(f"Successfully downloaded to: {filename}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False

