from openai import OpenAI
from dotenv import load_dotenv
import os
from src.config import *

aiparameters = ChatGPTPars()
chaptermaker_ai_parameters = ChatGPTChapterMakerPars()

import os, sys
from openai import OpenAI
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from logs.pokolog import PokoLogger, ScriptIdentifier
from src.tools.token_counter import *
from src.config import *
from src.db_ai.ai_db_manager import *

logger = PokoLogger()
load_dotenv('.env')


with open(chaptermaker_ai_parameters.paper_file, 'r') as file:
    notes_file = file.read()

class BatchChapterMaker():
    def __init__(self):
        logger.info(ScriptIdentifier.CHAPTER, "Initializing BatchCHAPTER")
        try:
            self.summary_file = SystemPars().big_text_file
            self.token_limit = SystemPars().token_limit
            # Initialize token counter and get summary stats
            totsum = TokenCounter()
            result = totsum.count_text(self.summary_file)
            self.token_count = result['tokens']  # Get token count directly

            
            self.cached_responses = []

            # Initialize prompts and roles and get their content
            CHAPTER_role = SystemPars().role_of_bot_CHAPTER
            single_batch_prompt = SystemPars().prompts_single_batch
            final_synthesis_prompt = SystemPars().prompts_final_synthesis

            # Return the actual text content using standard Python file reading
            with open(CHAPTER_role, 'r', encoding='utf-8') as f:
                self.role_text = f.read()
            with open(single_batch_prompt, 'r', encoding='utf-8') as f:
                self.batch_prompt_text = f.read()
            with open(final_synthesis_prompt, 'r', encoding='utf-8') as f:
                self.synthesis_prompt_text = f.read()
        
        #Split text into batches based on token limit
            tcoun = TokenCounter()
            full_text = tcoun.safe_read_text(self.summary_file)
            batches = []
            current_batch = ""
            current_tokens = 0
            
            for paragraph in full_text.split('\n\n'):
                paragraph_tokens = TokenCounter().count_tokens(paragraph)

                if current_tokens + paragraph_tokens > self.token_limit:
                    batches.append(current_batch)
                    current_batch = paragraph
                    current_tokens = paragraph_tokens
                else:
                    current_batch += "\n\n" + paragraph if current_batch else paragraph
                    current_tokens += paragraph_tokens
            
            if current_batch:
                batches.append(current_batch)
                
            logger.info(ScriptIdentifier.CHAPTER, 
                       f"Split text into {len(batches)} batches")
            self.batches = batches
            logger.info(ScriptIdentifier.CHAPTER, f"BatchCHAPTER initialized successfully")   
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error of Initialization of BatchCHAPTER, error: {e}")
            raise
class AIChapterMaker:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.role_of_bot = chaptermaker_ai_parameters.role_of_bot_chapter
        self.prompt_draft = chaptermaker_ai_parameters.prompts_chapter
        self.bot_model = aiparameters.model
        self.text = notes_file
    

    def create_chapter(self):
        prompt = f"{self.prompt_draft}:\n\n{self.text}"
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": f"{aiparameters.role_system}", "content": f"{self.role_of_bot}"},
                    {"role": f"{aiparameters.role_user}", "content": prompt}
                ],
                model=aiparameters.model,
                max_tokens=aiparameters.max_tokens,
                temperature=aiparameters.temperature,
            )

            chapter = response.choices[0].message.content.strip()
            return chapter
        except Exception as e:
            print(e)
            return None
    
if __name__ == "__main__":
    load_dotenv('.env')
    api_key = os.getenv('OPENAI_API_KEY')
    chapter_maker = AIChapterMaker(api_key)
    chapter = chapter_maker.create_chapter()
    with open(chaptermaker_ai_parameters.chapters_historicity, 'a') as file:
        file.write(chapter_maker.prompt_draft)
        file.write('\nAnswer\n')
        file.write(chapter)
        file.write('\n\n--------\n')
