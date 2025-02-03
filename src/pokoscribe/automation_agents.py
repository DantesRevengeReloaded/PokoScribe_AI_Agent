import sys, os, time, functools
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *
from src.agents.chapter_maker import *
from src.agents.ai_summarizer import *
from src.agents.ai_outliner import *
from src.tools.ahss import *
from src.tools.sci_hub_dler import *
from src.db_ai.ai_db_manager import *

logger = PokoLogger()
load_dotenv('.env')

def ai_agent_timer(script_id):
    """Universal decorator for timing and logging all operations"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # Detect operation type
            is_ai_model = any(x in func_name for x in ['summarize', 'outline', 'chaptermaker'])
            is_source_op = any(x in func_name for x in ['metadata', 'filter', 'download'])
            
            try:
                # Log start based on operation type
                if is_ai_model:
                    model_name = func_name.replace('summarize', '').replace('outline', '').replace('chaptermaker', '')
                    logger.info(script_id, f"Using {model_name.upper()} model...")
                else:
                    logger.info(script_id, f"Starting {func_name}...")
                
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log metrics based on operation type
                if is_ai_model:
                    logger.info(script_id, 
                              f"{func_name} with {model_name.upper()} completed in {execution_time:.2f} seconds")
                else:
                    logger.info(script_id, 
                              f"{func_name} completed in {execution_time:.2f} seconds")
                
                # Log additional metrics if available
                if hasattr(result, 'totalfilesprocessed'):
                    logger.info(script_id, f"Total files processed: {result.totalfilesprocessed}")
                if hasattr(result, 'completedfiles'):
                    logger.info(script_id, f"Completed files: {result.completedfiles}")
                if isinstance(result, pd.DataFrame):
                    logger.info(script_id, f"Processed {len(result)} records")
                    
                return result
                
            except Exception as e:
                if is_ai_model:
                    logger.error(script_id, 
                               f"Error in {func_name} with {model_name.upper()}: {e}")
                else:
                    logger.error(script_id, f"Error in {func_name}: {e}")
                raise
                
        return wrapper
    return decorator


class GetSources:
    """
    This class is used to automate the process of getting metadata for a specific project,
    filter them using AI so it will get the most relevant paper
    and then download the paper from Sci-Hub.
    It will also store the metadata and the paper result for downloading in the database.

    Configure the project name and the keywords and search queries in the config.py file.
    """
    def __init__(self):
        pass


# Get the metadata and store it in the database
    @ai_agent_timer(ScriptIdentifier.MAIN)
    def get_metadata(self):
        """
        Get metadata from the database.
        """
        try:
            run_api_search = AHSSMain() # AHSS is a class that handles all API searches together
            run_api_search.run_search()
            logger.info(ScriptIdentifier.MAIN, "Metadata retrieved successfully from the platforms.")

        except Exception as e:
            logger.error(ScriptIdentifier.MAIN, f"Failed to get metadata in automated procedure: {e}")

    @ai_agent_timer(ScriptIdentifier.MAIN)
    def filter_metadata(self):
        """
        Filter metadata using AI chat gpt api.
        """
        try:
            projname = SystemPars().project_name
            retrieve_metadata = GetMetaData()
            df_retr = retrieve_metadata.get_papers_metadata_by_title(projname)
            df_retr_json = df_retr.to_json(orient="records")
            prompt_path = SystemPars().filter_sources_for_dl
            with open(prompt_path, 'r') as f:
                promptfile = f.read()

            prompt = f"{promptfile}\n\n{df_retr_json}"
            load_dotenv('.env')
            api_key = os.getenv('DEEPSEEK_API_KEY')
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            
            response = client.chat.completions.create(
                messages=[
                    
                    {"role": "user", "content": prompt}
                ],
                model="deepseek-chat",
                temperature=0.5,
            )
            filtered_metadata = response.choices[0].message.content.strip()
            
            # Extract SELECT statement from response using regex
            select_statement = re.search(r'[Ss][Ee][Ll][Ee][Cc][Tt].*?\)', filtered_metadata, re.DOTALL)
            if select_statement:
                sql = select_statement.group()
                # Store the filtered results
                store_metadata = GetMetaData()
                store_metadata.insert_filtered_metadata(sql)
            else:
                logger.error(ScriptIdentifier.MAIN, "Could not find SELECT statement in AI response")

        except Exception as e:
            logger.error(ScriptIdentifier.MAIN, f"Failed to filter metadata in automated procedure: {e}")

    @ai_agent_timer(ScriptIdentifier.MAIN)
    def download_filtered_papers(self):
        try:
            # Get project name and metadata
            projname = SystemPars().project_name
            retrieve_metadata = GetMetaData()
            df_retr = retrieve_metadata.get_filtered_metadata(projname)
            
            # Initialize downloader
            dl_paper = SciHubDler()
            
            # Process each paper
            for index, row in df_retr.iterrows():
                try:
                    # Clean and validate DOI
                    doi = str(row['doi']).strip()
                    if not doi or doi == 'N/A':
                        logger.warning(ScriptIdentifier.MAIN, 
                                    f"Invalid DOI for paper: {row['title']}")
                        continue
                    
                    # Download paper
                    success = dl_paper.download_paper(
                        doi=doi,
                        title=str(row['title']),
                        metadata_id=int(row['metadata_id'])
                    )
                    
                except Exception as e:
                    logger.error(ScriptIdentifier.MAIN, 
                            f"Error downloading paper {row['title']}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(ScriptIdentifier.MAIN, 
                        f"Failed to download filtered metadata: {e}")
            raise


class AIBotSummarizer:
    def __init__(self):
        pass
    
    @ai_agent_timer(ScriptIdentifier.MAIN)
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

    @ai_agent_timer(ScriptIdentifier.MAIN)
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

    @ai_agent_timer(ScriptIdentifier.MAIN)
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

    @ai_agent_timer(ScriptIdentifier.MAIN)
    def chatgptoutline(self):
        getoutline = ChatGPTOutliner()
        getoutline.outline_it()
        return getoutline

    @ai_agent_timer(ScriptIdentifier.MAIN)
    def deepseekoutline(self):
        getoutline = DeepSeekOutliner()
        getoutline.outline_it()
        return getoutline


class AIBotChapterMaker:
    def __init__(self):
        pass

    @ai_agent_timer(ScriptIdentifier.MAIN)
    def deepseekchaptermaker(self):
        chaptermaker = BatchChapterMaker()
        chaptermaker.make_chapter()
        return chaptermaker

    @ai_agent_timer(ScriptIdentifier.MAIN)
    def chatgptchaptermaker(self):
        chaptermaker = BatchChapterMaker()
        chaptermaker.make_chapter()
        return chaptermaker

pp = GetSources()
pp.get_metadata()