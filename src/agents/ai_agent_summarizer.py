import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.agents.config import *
from agents.ai_summarizer import *

logger = PokoLogger()


class AIBotSummarizer:
    def __init__(self):
        pass
    
    def chatgptsummerize(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, "Using OpenAI model...")
            summparameters = ChatGPTPdfSummerizerPars()
            load_dotenv('.env')
            api_key = os.getenv('OPENAI_API_KEY')
            summarizer = PDFSummarizer(summparameters.input_folder, summparameters.big_text_file, api_key, 
                                    summparameters.completed_folder, summparameters.to_be_completed_folder, 'openai')
            summarizer.process_pdfs('openai')
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Summarizer AI model with OpenAI completed in {end_time - start_time} seconds.")
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Total files processed: {summarizer.totalfilesprocessed}")
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Completed files: {summarizer.completedfiles}")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTSUMMARIZER, f"Error in Summarizer AI model of OpenAI: {e}")

    def geminisummerize(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, "Using Gemini model...")
            summparameters = GeminiSummerizerPars()
            load_dotenv('.env')
            api_key = os.getenv('GEMINI_API_KEY')
            summarizer = PDFSummarizer(summparameters.input_folder, summparameters.big_text_file, api_key, 
                                    summparameters.completed_folder, summparameters.to_be_completed_folder, 'gemini')
            summarizer.process_pdfs('gemini')
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Summarizer AI model with Gemini completed in {end_time - start_time} seconds.")
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Total files processed: {summarizer.totalfilesprocessed}")
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Completed files: {summarizer.completedfiles}")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTSUMMARIZER, f"Error in Summarizer AI model of Gemini {e}")
        
    def deepseeksummerize(self):
        try:
            start_time = time.time()
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, "Using DeepSeek model...")
            summparameters = DeepSeekSummerizerPars()
            load_dotenv('.env')
            api_key = os.getenv('DEEPSEEK_API_KEY')
            summarizer = PDFSummarizer(summparameters.input_folder, summparameters.big_text_file, api_key, 
                                    summparameters.completed_folder, summparameters.to_be_completed_folder, 'deepseek')
            summarizer.process_pdfs('deepseek')
            end_time = time.time()
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Summarizer AI model with DeepSeek completed in {end_time - start_time} seconds.")
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Total files processed: {summarizer.totalfilesprocessed}")
            logger.info(ScriptIdentifier.AGENTSUMMARIZER, f"Completed files: {summarizer.completedfiles}")
        except Exception as e:
            logger.error(ScriptIdentifier.AGENTSUMMARIZER, f"Error in Summarizer AI model of Deepseek {e}")

to = AIBotSummarizer()
to.chatgptsummerize()