import sys, json, re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.tools.ahss import CrossRefHandler, OpenAlexHandler, CoreAPIHandler
from src.tools.sci_hub_dler import *
from src.db_ai.ai_db_manager import *
from logs.pokolog import *
from src.config import SystemPars

logger = PokoLogger()

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
    def get_metadata(self):
        """
        Get metadata from the database.
        """
        try:
            # Run CrossRef search
            handler = CrossRefHandler()
            handler.search_resources()

            # Run OpenAlex search
            alex_handler = OpenAlexHandler()
            alex_handler.search_resources()

            # Run Core API search
            coreapi = CoreAPIHandler()
            coreapi.search_specific_papers()
            
            logger.info(ScriptIdentifier.MAIN, "Metadata retrieved successfully from the platforms.")
        except Exception as e:
            logger.error(ScriptIdentifier.MAIN, f"Failed to get metadata in automated procedure: {e}")

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

