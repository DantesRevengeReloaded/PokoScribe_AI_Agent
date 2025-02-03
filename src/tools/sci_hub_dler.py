import re
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Project imports should remain at top
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from logs.pokolog import *
from src.db_ai.ai_db_manager import *

load_dotenv('.env')
logger = PokoLogger()

class SciHubDler:
    PDF_SELECTORS = [
        ('button', {'string': re.compile(r'download', re.I)}),
        ('a', {'href': re.compile(r'\.pdf$')}),
        ('embed', {'type': 'application/pdf'}),
        ('iframe', {'id': 'pdf'})
    ]
    DEFAULT_SCIHUB_URL = "https://sci-hub.se"
    DEFAULT_DOWNLOAD_DIR = Path("resources/downloads")
    RETRY_STRATEGY = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    def __init__(self):
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=self.RETRY_STRATEGY))
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = PokoLogger()
        self.db_manager = GetMetaData()
        self.DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename removing invalid characters and truncating to 255 chars."""
        return re.sub(r'[<>:"/\\|?*]', '', filename)[:255]

    def _find_pdf_element(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Search for PDF element in BeautifulSoup object using multiple selectors."""
        for tag, attrs in self.PDF_SELECTORS:
            element = soup.find(tag, attrs)
            if element:
                return element
        return None

    def _extract_pdf_url(self, element: Tag, base_url: str) -> Optional[str]:
        """Extract PDF URL from HTML element."""
        for attr in ['href', 'src']:
            if attr in element.attrs:
                url = element[attr]
                if url.startswith('//'):
                    return f'https:{url}'
                if not url.startswith(('http://', 'https://')):
                    return urljoin(base_url, url)
                return url
        return None

    def _construct_filename(self, metadata_id: int, title: str) -> Path:
        """Generate safe filename with metadata ID and sanitized title."""
        clean_title = self.sanitize_filename(title)
        return self.DEFAULT_DOWNLOAD_DIR / f"{metadata_id}_{clean_title}.pdf"

    def download_paper(
        self,
        doi: str,
        title: str,
        metadata_id: int,
        scihub_url: str = DEFAULT_SCIHUB_URL,
        throttle_delay: int = 3
    ) -> bool:
        """Download a paper from Sci-Hub with retry logic and proper resource management."""
        doi = doi.strip()
        if not doi:
            self.logger.error(ScriptIdentifier.SCIHUB, "Empty DOI provided")
            return False

        try:
            # Normalize Sci-Hub URL
            scihub_url = scihub_url.strip('/')
            if not scihub_url.startswith(('http://', 'https://')):
                scihub_url = f'https://{scihub_url}'

            # Fetch search page
            search_url = f"{scihub_url}/{doi}"
            self.logger.info(ScriptIdentifier.SCIHUB, f"Searching: {search_url}")

            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_element = self._find_pdf_element(soup)
            
            if not pdf_element:
                self.logger.error(ScriptIdentifier.SCIHUB, "No PDF element found")
                return False

            pdf_url = self._extract_pdf_url(pdf_element, scihub_url)
            if not pdf_url:
                self.logger.error(ScriptIdentifier.SCIHUB, "Failed to extract PDF URL")
                return False

            self.logger.info(ScriptIdentifier.SCIHUB, f"Found PDF URL: {pdf_url}")

            # Download PDF
            pdf_response = self.session.get(pdf_url, timeout=60)
            pdf_response.raise_for_status()

            # Save file
            file_path = self._construct_filename(metadata_id, title)
            file_path.write_bytes(pdf_response.content)
            self.logger.info(ScriptIdentifier.SCIHUB, f"Saved: {file_path}")

            # Update database
            self.db_manager.update_filtered_metadata_succeeded_dl(metadata_id)
            self.logger.info(ScriptIdentifier.SCIHUB, f"Updated metadata for {title}")
            
            time.sleep(throttle_delay)
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(ScriptIdentifier.SCIHUB, f"Network error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(ScriptIdentifier.SCIHUB, f"Unexpected error: {str(e)}")
            return False