import sys
import os
from pathlib import Path
from time import time

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *
from src.agents.chapter_maker import *

logger = PokoLogger()


class AIBotChapterMaker:

    def __init__(self):
        pass

    def deepseekchaptermaker(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTCHAPTER, "Using DeepSeek model...")
            chaptermaker = BatchChapterMaker()
            chaptermaker.run_deepseek()
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTCHAPTER, f"ChapterMaker AI model with DeepSeek completed in {end_time - start_time} seconds.")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTCHAPTER, f"Error in ChapterMaker AI model of DeepSeek: {e}")

    def chatgptchaptermaker(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTCHAPTER, "Using OpenAI model...")
            chaptermaker = BatchChapterMaker()
            chaptermaker.run_chatgpt()
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTCHAPTER, f"ChapterMaker AI model with OpenAI completed in {end_time - start_time} seconds.")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTCHAPTER, f"Error in ChapterMaker AI model of OpenAI: {e}")