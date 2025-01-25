import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *
from src.agents.ai_outliner import *
load_dotenv('.env')
logger = PokoLogger()

class AIBotOutliner:
    pass

    def deepseekoutline(self):
        try:
            logger.info(ScriptIdentifier.OUTLINER, "Using DeepSeek model...")
            outliner = PaperOutliner('deepseek')
            outliner.process_pdfs('deepseek')
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTOUTLINER, f"Error in Outliner AI model of DeepSeek {e}")