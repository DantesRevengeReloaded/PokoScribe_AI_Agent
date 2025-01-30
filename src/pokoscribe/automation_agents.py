import sys, os, time, functools
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *
from src.agents.chapter_maker import *
from src.agents.ai_summarizer import *
from src.agents.ai_outliner import *

logger = PokoLogger()
load_dotenv('.env')

def ai_agent_timer(script_id):
    """Decorator for timing and logging AI agent operations"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            model_name = func.__name__.replace('summarize', '').replace('outline', '').replace('chaptermaker', '')
            
            try:
                logger.info(script_id, f"Using {model_name.upper()} model...")
                result = func(*args, **kwargs)
                
                execution_time = time.time() - start_time
                logger.info(script_id, 
                          f"{func.__name__} with {model_name.upper()} completed in {execution_time:.2f} seconds")
                
                # Log metrics if available
                if hasattr(result, 'totalfilesprocessed'):
                    logger.info(script_id, f"Total files processed: {result.totalfilesprocessed}")
                if hasattr(result, 'completedfiles'):
                    logger.info(script_id, f"Completed files: {result.completedfiles}")
                    
                return result
                
            except Exception as e:
                logger.error(script_id, f"Error in {func.__name__} with {model_name.upper()}: {e}")
                raise
                
        return wrapper
    return decorator


class AIBotSummarizer:
    def __init__(self):
        pass
    
    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def chatgptsummerize(self):
        summparameters = ChatGPTPdfSummerizerPars()
        api_key = os.getenv('OPENAI_API_KEY')
        summarizer = PDFSummarizer(
            summparameters.input_folder, 
            summparameters.big_text_file,
            api_key, 
            summparameters.completed_folder,
            summparameters.to_be_completed_folder,
            'openai'
        )
        summarizer.process_pdfs('openai')
        return summarizer

    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def geminisummerize(self):
        summparameters = GeminiSummerizerPars()
        api_key = os.getenv('GEMINI_API_KEY')
        summarizer = PDFSummarizer(
            summparameters.input_folder,
            summparameters.big_text_file,
            api_key,
            summparameters.completed_folder,
            summparameters.to_be_completed_folder,
            'gemini'
        )
        summarizer.process_pdfs('gemini')
        return summarizer

    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def deepseeksummerize(self):
        summparameters = DeepSeekSummerizerPars()
        api_key = os.getenv('DEEPSEEK_API_KEY')
        summarizer = PDFSummarizer(
            summparameters.input_folder,
            summparameters.big_text_file,
            api_key,
            summparameters.completed_folder,
            summparameters.to_be_completed_folder,
            'deepseek'
        )
        summarizer.process_pdfs('deepseek')
        return summarizer


class AIOutlinerAgent:
    def __init__(self):
        pass

    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def chatgptoutline(self):
        getoutline = ChatGPTOutliner()
        getoutline.outline_it()
        return getoutline

    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def deepseekoutline(self):
        getoutline = DeepSeekOutliner()
        getoutline.outline_it()
        return getoutline


class AIBotChapterMaker:
    def __init__(self):
        pass

    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def deepseekchaptermaker(self):
        chaptermaker = BatchChapterMaker()
        chaptermaker.make_chapter()
        return chaptermaker

    @ai_agent_timer(ScriptIdentifier.AGENTS)
    def chatgptchaptermaker(self):
        chaptermaker = BatchChapterMaker()
        chaptermaker.make_chapter()
        return chaptermaker

tt = AIBotSummarizer()
tt.deepseeksummerize()