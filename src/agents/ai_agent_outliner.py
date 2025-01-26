import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
import time
from src.config import *
from src.agents.ai_outliner import *
load_dotenv('.env')
logger = PokoLogger()

class AIOutlinerAgent:
    def __init__(self):
        pass

    def chatgptoutline(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTOUTLINER, "Using OpenAI model...")
            getoutline = ChatGPTOutliner()
            getoutline.outline_it()
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTOUTLINER, f"Outliner AI model with OpenAI completed in {end_time - start_time} seconds.")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTOUTLINER, f"Error in Outliner AI model of OpenAI: {e}")

    def deepseekoutline(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTOUTLINER, "Using DeepSeek model...")
            getoutline = DeepSeekOutliner()
            getoutline.outline_it()
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTOUTLINER, f"Outliner AI model with DeepSeek completed in {end_time - start_time} seconds.")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTOUTLINER, f"Error in Outliner AI model of DeepSeek {e}")
