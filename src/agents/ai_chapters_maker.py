
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

            # Return the actual text content using standard Python file reading
            with open(SystemPars().role_of_bot_chapter, 'r', encoding='utf-8') as f:
                self.role_text = f.read()
            with open(SystemPars().prompts_chapter, 'r', encoding='utf-8') as f:
                self.batch_prompt_text = f.read()
            with open(SystemPars().prompts_synthesis_chapter, 'r', encoding='utf-8') as f:
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
            logger.info(ScriptIdentifier.CHAPTER, f"BatchChapterMaker initialized successfully")   
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error of Initialization of BatchChapterMaker, error: {e}")
            raise

class DeepSeekChapterMaker(BatchChapterMaker):
    def __init__(self):
        logger.info(ScriptIdentifier.CHAPTER, "Initializing DeepSeekChapterMaker")
        try:
            super().__init__()
            self.aiparameters = DeepSeekPars()
            self.api_key = os.getenv('DEEPSEEK_API_KEY')
            logger.info(ScriptIdentifier.CHAPTER, f"parameters of DeepSeekChapterMaker : {self.aiparameters}")
            logger.info(ScriptIdentifier.CHAPTER, "DeepSeekChapterMaker initialized successfully")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error initializing DeepSeekChapterMaker: {e}")
            raise

    def make_chapter(self):
        for i, batch in enumerate(self.batches, 1):
            try:
                logger.info(ScriptIdentifier.CHAPTER, f"Processing batch {i} of {len(self.batches)}")
                prompt = f"{self.batch_prompt_text} {batch}"

                logger.info(ScriptIdentifier.CHAPTER, f"Prompt created for DeepSeek to create chapter in single batch")
            except Exception as e:
                logger.error(ScriptIdentifier.CHAPTER, f"Error creating prompt for single batch (DeepSeek): {str(e)}")
                
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
                logger.info(ScriptIdentifier.CHAPTER, f"DeepSeek response for batch chapter maker received without problems")
                self.cached_responses.append(response)
                with open('resources\output_of_ai\chapters.txt', 'a', encoding='utf-8') as f1:
                    f1.write('\n\n')
                    f1.write('-'*10)
                    f1.write('\n\n')
                    f1.write(f"Answer for Batch {i}")
                    f1.write('\n\n')
                    f1.write(response.choices[0].message.content)
                logger.info(ScriptIdentifier.CHAPTER, f"Chapter for #{i} batch is written to file")
            except Exception as e:
                logger.error(ScriptIdentifier.CHAPTER, f"Batch #{i} processing error: {e}")

        #Get the content of the responses from the cached responses list
        self.cached_responses = [response.choices[0].message.content for response in self.cached_responses]          

            #Create final outline from cached responses
        synthesis_prompt = f"{self.synthesis_prompt_text} {' '.join(self.cached_responses)}"


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
            logger.info(ScriptIdentifier.CHAPTER, f"DeepSeek response for Final Chapter Response received without problems")

            with open('resources/output_of_ai/outline.txt', 'a', encoding='utf-8') as f:
                f.write('\n\n')
                f.write('-'*20)
                f.write('\n\n')
                f.write('Final Chapter Response')
                f.write('\n\n')
                f.write(response.choices[0].message.content)
            logger.info(ScriptIdentifier.CHAPTER, f"Final chapter response written to file")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Batch processing error: {e}")


