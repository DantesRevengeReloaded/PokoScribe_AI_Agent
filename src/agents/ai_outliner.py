
import os, json, openai, sys
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path
# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
from logs.pokolog import PokoLogger, ScriptIdentifier
from src.tools.token_counter import *
from src.config import *
import google.generativeai as genai
from src.db_ai.ai_db_manager import *
logger = PokoLogger()
load_dotenv('.env')

from concurrent.futures import ThreadPoolExecutor, as_completed


model_lists = SystemPars().model_lists

class PaperOutliner:
    def __init__ (self, model_type: str):
        self.model_type = model_type

        if model_type == 'openai':
            self.aiparameters = ChatGPTPars()
        elif model_type == 'gemini':
            self.aiparameters = GeminiPars()
        elif model_type == 'deepseek':
            self.aiparameters = DeepSeekPars()
        else:
            logger.warning(ScriptIdentifier.OUTLINER, f"Invalid model type. Not in supported list: {model_lists}")
            raise ValueError(f"Invalid model type. Not in supported list: {model_lists}")
        
        # Initialize token counter and get summary stats
        

class BatchOutliner():
    def __init__(self):
        self.summary_file = SystemPars().big_text_file
        self.token_limit = SystemPars().token_limit
        # Initialize token counter and get summary stats
        totsum = TokenCounter()
        result = totsum.count_text(self.summary_file)
        self.token_count = result['tokens']  # Get token count directly

        
        self.cached_responses = []
        self.tc = self.token_count
        # Initialize prompts and roles and get their content
        outliner_role = SystemPars().role_of_bot_outliner
        single_batch_prompt = SystemPars().prompts_single_batch
        final_synthesis_prompt = SystemPars().prompts_final_synthesis

        # Return the actual text content using standard Python file reading
        with open(outliner_role, 'r', encoding='utf-8') as f:
            self.role_text = f.read()
        with open(single_batch_prompt, 'r', encoding='utf-8') as f:
            self.batch_prompt_text = f.read()
        with open(final_synthesis_prompt, 'r', encoding='utf-8') as f:
            self.synthesis_prompt_text = f.read()

        
        #Split text into batches based on token limit
        try:
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
                
            logger.info(ScriptIdentifier.OUTLINER, 
                       f"Split text into {len(batches)} batches")
            self.batches = batches
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Batch splitting error: {e}")
            raise

class DeepSeekOutliner(BatchOutliner):
    def __init__(self):
        super().__init__()
        self.aiparameters = DeepSeekPars()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
            
        for i, batch in enumerate(self.batches, 1):
            try:
                logger.info(ScriptIdentifier.OUTLINER, f"Processing batch {i} of {len(self.batches)}")
                prompt = f"{self.batch_prompt_text} {batch}"

                logger.info(ScriptIdentifier.OUTLINER, f"Prompt created for DeepSeek to outline single batch")
            except Exception as e:
                logger.error(ScriptIdentifier.OUTLINER, f"Error creating prompt for single batch (DeepSeek): {str(e)}")
                
            try:
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                response = self.client.chat.completions.create(
                    messages=[
                    {"role": f"{self.aiparameters.role_system}", "content": f"{prompt}"},
                    {"role": f"{self.aiparameters.role_user}", "content": prompt}
                    ],
                    model=self.aiparameters.model,
                    max_tokens=self.aiparameters.max_tokens,
                    temperature=self.aiparameters.temperature,
                )
                logger.info(ScriptIdentifier.OUTLINER, f"DeepSeek response received without problems")
                self.cached_responses.append(response)
            except Exception as e:
                logger.error(ScriptIdentifier.OUTLINER, f"Batch processing error: {e}")  
                print(self.cached_responses)
        
        self.cached_responses = [response.choices[0].message.content for response in self.cached_responses]          

            """Create final outline from cached responses"""
        synthesis_prompt = f"""Based on these separate outlines that are product of parts of a single summary text, create a unified, coherent outline:

        {' '.join(self.cached_responses)}

        Create a comprehensive outline that synthesizes all major themes and findings."""


        try:
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            response = self.client.chat.completions.create(
                messages=[
                    {"role": f"{self.aiparameters.role_system}", "content": f"{synthesis_prompt}"},
                    {"role": f"{self.aiparameters.role_user}", "content": synthesis_prompt}
                ],
                model=self.aiparameters.model,
                max_tokens=self.aiparameters.max_tokens,
                temperature=self.aiparameters.temperature,
            )
            logger.info(ScriptIdentifier.OUTLINER, f"DeepSeek response received without problems")
            print(response)
            with open('resources/output_of_ai/outline.txt', 'a', encoding='utf-8') as f:
                f.write(response.choices[0].message.content)
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Batch processing error: {e}")



ds = DeepSeekOutliner()
ds.single_batch()
