import sys, json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.tools.ahss import CrossRefHandler, OpenAlexHandler, CoreAPIHandler
from src.db_ai.ai_db_manager import *
from logs.pokolog import *
from src.config import SystemPars

logger = PokoLogger()
"""
This script is used to automate the process of getting metadata for a specific project,
filter them using AI so it will get the most relevant paper
and then download the paper from Sci-Hub.
It will also store the metadata and the paper result for downloading in the database.

Configure the project name and the keywords and search queries in the config.py file.
"""

# Get the metadata and store it in the database
def get_metadata():
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
    except Exception as e:
        logger.error(ScriptIdentifier.MAIN, f"Failed to get metadata in automated procedure: {e}")

def filter_metadata():
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
        api_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a bot."},
                {"role": "user", "content": prompt}
            ],
            model="o1-mini",
            max_tokens=1000,
            temperature=0.5,
        )
        filtered_metadata = response.choices[0].message.content.strip()
        return filtered_metadata

    except Exception as e:
        logger.error(ScriptIdentifier.MAIN, f"Failed to filter metadata in automated procedure: {e}")

filter_metadata()


