
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
        logger.info(ScriptIdentifier.CHAPTER, "Initializing BatchChapterMaker")
        try:
            self.summary_file = SystemPars().big_text_file
            self.token_limit = SystemPars().token_limit

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
            self.cached_responses = []
            current_batch = ""
            current_tokens = 0
            total_tokens = 0
            
            for paragraph in full_text.split('\n\n'):
                paragraph_tokens = TokenCounter().count_tokens(paragraph)
                total_tokens += paragraph_tokens

                if current_tokens + paragraph_tokens > self.token_limit:
                    batches.append(current_batch)
                    current_batch = paragraph
                    current_tokens = paragraph_tokens
                else:
                    current_batch += "\n\n" + paragraph if current_batch else paragraph
                    current_tokens += paragraph_tokens
            
            if current_batch:
                batches.append(current_batch)

            logger.info(ScriptIdentifier.CHAPTER, f"Total tokens in summary text: {total_tokens}")   
            logger.info(ScriptIdentifier.CHAPTER, f"Split text into {len(batches)} batches")
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
            logger.info(ScriptIdentifier.CHAPTER, "DeepSeek Parameters:")
            logger.info(ScriptIdentifier.CHAPTER, f"Model: {self.aiparameters.model}")
            logger.info(ScriptIdentifier.CHAPTER, f"Max output tokens: {self.aiparameters.max_tokens}")
            logger.info(ScriptIdentifier.CHAPTER, f"Temperature: {self.aiparameters.temperature}")
            logger.info(ScriptIdentifier.CHAPTER, f"Role of bot: {self.aiparameters.role_system}")
            logger.info(ScriptIdentifier.CHAPTER, f"Role of user: {self.aiparameters.role_user}")
            logger.info(ScriptIdentifier.CHAPTER, f"Token limit: {self.aiparameters.tokenslimit}")

            logger.info(ScriptIdentifier.CHAPTER, "DeepSeekChapterMaker initialized successfully")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error initializing DeepSeekChapterMaker: {e}")
            raise

    def make_chapter(self):
        def clean_response(response_text: str) -> str:
            """Clean and validate response text"""
            try:
                # Remove any leading/trailing whitespace
                cleaned = response_text.strip()
                # Ensure proper JSON structure if needed
                if cleaned.startswith('{') or cleaned.startswith('['):
                    import json
                    cleaned = json.loads(cleaned)
                    cleaned = json.dumps(cleaned)
                return cleaned
            except json.JSONDecodeError as e:
                logger.error(ScriptIdentifier.CHAPTER, f"JSON cleaning error: {e}")
                return response_text
            
        for i, batch in enumerate(self.batches, 1):
            retries = 3
            while retries > 0:
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
                    response = clean_response(response)
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
                
                except json.JSONDecodeError as e:
                    retries -= 1
                    logger.error(ScriptIdentifier.CHAPTER, 
                            f"JSON error in batch {i}, retries left {retries}: {e}")
                    if retries == 0:
                        continue

                except Exception as e:
                    logger.error(ScriptIdentifier.CHAPTER, f"Batch #{i} processing error: {e}")
                    break
        
        try:
         #Get the content of the responses from the cached responses list
            self.cached_responses = [response.choices[0].message.content for response in self.cached_responses]          

                #Create final outline from cached responses
            synthesis_prompt = f"{self.synthesis_prompt_text} {' '.join(self.cached_responses)}"
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error creating prompt for final response: {e}")

        try:
            logger.info(ScriptIdentifier.CHAPTER, f"Creating final chapter response")
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

            with open('resources\output_of_ai\chapters.txt', 'a', encoding='utf-8') as f:
                f.write('\n\n')
                f.write('-'*20)
                f.write('\n\n')
                f.write('Final Chapter Response for DeepSeek:')
                f.write('\n\n')
                f.write(response.choices[0].message.content)
            logger.info(ScriptIdentifier.CHAPTER, f"Final chapter response written to file")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Batch processing error: {e}")

class ChatGPTChapterMaker(BatchChapterMaker):
    def __init__(self):
        logger.info(ScriptIdentifier.CHAPTER, "Initializing ChatGPTChapterMaker")
        try:
            super().__init__()
            self.aiparameters = ChatGPTPars()
            self.api_key = os.getenv('OPENAI_API_KEY')
            logger.info(ScriptIdentifier.CHAPTER, "ChatGPT Parameters:")
            logger.info(ScriptIdentifier.CHAPTER, f"Model: {self.aiparameters.model}")
            logger.info(ScriptIdentifier.CHAPTER, f"Max output tokens: {self.aiparameters.max_tokens}")
            logger.info(ScriptIdentifier.CHAPTER, f"Temperature: {self.aiparameters.temperature}")
            logger.info(ScriptIdentifier.CHAPTER, f"Role of bot: {self.aiparameters.role_system}")
            logger.info(ScriptIdentifier.CHAPTER, f"Role of user: {self.aiparameters.role_user}")
            logger.info(ScriptIdentifier.CHAPTER, f"Token limit: {self.aiparameters.tokenslimit}")

            logger.info(ScriptIdentifier.CHAPTER, "ChatGptChapterMaker initialized successfully")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error initializing ChatGptChapterMaker: {e}")
            raise

    def make_chapter(self):
        def clean_response(response_text: str) -> str:
            """Clean and validate response text"""
            try:
                # Remove any leading/trailing whitespace
                cleaned = response_text.strip()
                # Ensure proper JSON structure if needed
                if cleaned.startswith('{') or cleaned.startswith('['):
                    import json
                    cleaned = json.loads(cleaned)
                    cleaned = json.dumps(cleaned)
                return cleaned
            except json.JSONDecodeError as e:
                logger.error(ScriptIdentifier.CHAPTER, f"JSON cleaning error: {e}")
                return response_text
        for i, batch in enumerate(self.batches, 1):
            try:
                logger.info(ScriptIdentifier.CHAPTER, f"Processing batch {i} of {len(self.batches)}")
                prompt = f"{self.batch_prompt_text} {batch}"

                logger.info(ScriptIdentifier.CHAPTER, f"Prompt created for ChatGPT to create chapter in single batch")
            except Exception as e:
                logger.error(ScriptIdentifier.CHAPTER, f"Error creating prompt for single batch (ChatGPT): {str(e)}")
                
            try:
                self.client = OpenAI(api_key=self.api_key)
                response = self.client.chat.completions.create(
                    messages=[
                    
                    {"role": f"{self.aiparameters.role_user}", "content": prompt}
                    ],
                    model=self.aiparameters.model,
                    max_completion_tokens=self.aiparameters.max_tokens,
                    temperature=self.aiparameters.temperature,
                )
                logger.info(ScriptIdentifier.CHAPTER, f"ChatGPT response for batch chapter maker received without problems")
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
        
        try:
        #Get the content of the responses from the cached responses list
            self.cached_responses = [response.choices[0].message.content for response in self.cached_responses]          

                #Create final outline from cached responses
            synthesis_prompt = f"{self.synthesis_prompt_text} {' '.join(self.cached_responses)}"
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error creating prompt for final response: {e}")

        try:
            logger.info(ScriptIdentifier.CHAPTER, f"Creating final chapter response")
            self.client = OpenAI(api_key=self.api_key)
            response = self.client.chat.completions.create(
                messages=[
                    
                    {"role": f"{self.aiparameters.role_user}", "content": synthesis_prompt}
                ],
                model=self.aiparameters.model,
                max_completion_tokens=self.aiparameters.max_tokens,
                temperature=self.aiparameters.temperature,
            )
            logger.info(ScriptIdentifier.CHAPTER, f"ChatGPT response for Final Chapter Response received without problems")
            print(response.choices[0].message.content)
            with open('resources\output_of_ai\chapters.txt', 'a', encoding='utf-8') as f:
                f.write('\n\n')
                f.write('-'*20)
                f.write('\n\n')
                f.write('Final Chapter Response for ChatGPT:')
                f.write('\n\n')
                f.write(response.choices[0].message.content)
            logger.info(ScriptIdentifier.CHAPTER, f"Final chapter response written to file")
            print(response)
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Batch processing error: {e}")                

tl = ChatGPTChapterMaker()
tl.make_chapter()

