import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from db_ai.ai_db_manager import *


tsek = AIDbManager()
psl = tsek.get_paper_sources("TESTS", [2, 3])

print(psl)