import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.tools.ahss import CrossRefHandler, OpenAlexHandler, CoreAPIHandler

"""
# Run CrossRef search
handler = CrossRefHandler()
handler.search_resources()

# Run OpenAlex search
alex_handler = OpenAlexHandler()
alex_handler.search_resources()
"""
# Run Core API search
coreapi = CoreAPIHandler()
coreapi.search_specific_papers()

