import requests, os, re, sys, time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from time import sleep
from dotenv import load_dotenv
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from logs.pokolog import *
from src.db_ai.ai_db_manager import *

load_dotenv('.env')
logger = PokoLogger()

def sanitize_filename(filename):
    """
    Sanitize a string to be used as a filename.
    Removes invalid characters and truncates to 255 characters.
    
    Args:
        filename (str): The filename to sanitize
    
    Returns:
        str: The sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Truncate to 255 characters
    return filename[:255]

class SciHubDler:
    def __init__(self):
        pass


    def download_paper(self, doi, title, metadata_id, scihub_url="https://sci-hub.se", download_dir="resources/downloads"):
        """
        Download a scientific paper from Sci-Hub using its DOI.
        First searches for the paper on Sci-Hub's interface, then downloads the PDF.
        
        Args:
            doi (str): The DOI of the paper to download
            title (str): The title of the paper to download
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
            logger.info(ScriptIdentifier.SCIHUB, f"Searching: {search_url}")
            
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
                logger.error(ScriptIdentifier.SCIHUB, "Could not find PDF download link")
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
                logger.error(ScriptIdentifier.SCIHUB, "Could not extract PDF URL")
                return False
                
            # Handle relative URLs
            if not pdf_url.startswith(('http://', 'https://')):
                if pdf_url.startswith('//'):
                    pdf_url = f"https:{pdf_url}"
                else:
                    pdf_url = urljoin(scihub_url, pdf_url)
            
            logger.info(ScriptIdentifier.SCIHUB, f"Found PDF URL: {pdf_url}")
            
            # Download the PDF
            pdf_response = requests.get(pdf_url, headers=headers, timeout=30)
            pdf_response.raise_for_status()

            titleforpath = sanitize_filename(title)
            # Save the file
            filename = os.path.join(download_dir, f"{titleforpath}.pdf")
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            
            logger.info(ScriptIdentifier.SCIHUB, f"Downloaded: {filename}")
            insert_update_dl = GetMetaData()
            insert_update_dl.update_filtered_metadata_succeeded_dl(metadata_id, True)
            logger.info(ScriptIdentifier.SCIHUB, f"Updated metadata with download status for {title}")
            time.sleep(3)
            
        except requests.exceptions.RequestException as e:
            logger.error(ScriptIdentifier.SCIHUB, f"Request error: for {title} file: {str(e)}")
        except Exception as e:
            logger.error(ScriptIdentifier.SCIHUB, f" Unexpected error for {title} file: {str(e)}")

