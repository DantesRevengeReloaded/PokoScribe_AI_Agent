#create bibliography file from a db
import sys
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *
from src.db_ai.ai_db_manager import AIDbManager, BiblioCreator

projname = SystemPars().project_name

get_cits = BiblioCreator()
df = get_cits.get_biblio(projname)

