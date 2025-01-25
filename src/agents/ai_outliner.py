
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

class ChatGPTOutliner(BatchOutliner):
    def __init__(self):
        super().__init__()
            
    def single_batch(self):
        for batch in self.batches:
            prompt f"{batch_prompt_text}",

            {batch}
                """Process single batch with AI model"""
                prompt = f"""Create a detailed outline for an academic paper section based on these summaries:

                {batch_text}

                Generate a structured outline with main points and sub-points."""
                
                try:
                    if self.model_type == 'openai':
                        response = self._process_with_openai(prompt)
                    elif self.model_type == 'gemini':
                        response = self._process_with_gemini(prompt)
                    elif self.model_type == 'deepseek':
                        response = self._process_with_deepseek(prompt)
                        
                    self.cached_responses.append(response)
                    return response
                    
                except Exception as e:
                    logger.error(ScriptIdentifier.OUTLINER, f"Batch processing error: {e}")
                    raise
                    
            def synthesize_final_outline(self) -> str:
                """Create final outline from cached responses"""
                synthesis_prompt = f"""Based on these separate outlines, create a unified, coherent outline:

            {' '.join(self.cached_responses)}

        Create a comprehensive outline that synthesizes all major themes and findings."""
                
                try:
                    if self.model_type == 'openai':
                        final_outline = self._process_with_openai(synthesis_prompt)
                    elif self.model_type == 'gemini':
                        final_outline = self._process_with_gemini(synthesis_prompt)
                    elif self.model_type == 'deepseek':
                        final_outline = self._process_with_deepseek(synthesis_prompt)
                        
                    return final_outline
                    
                except Exception as e:
                    logger.error(ScriptIdentifier.OUTLINER, 
                                f"Final synthesis error: {e}")
                    raise
                    
            def generate_outline(self) -> str:
                """Main method to generate complete outline"""
                try:
                    batches = self.split_into_batches()
                    
                    for i, batch in enumerate(batches, 1):
                        logger.info(ScriptIdentifier.OUTLINER, 
                                f"Processing batch {i}/{len(batches)}")
                        self.process_batch(batch)
                        
                    final_outline = self.synthesize_final_outline()
                    
                    return final_outline
                    
                except Exception as e:
                    logger.error(ScriptIdentifier.OUTLINER, 
                                f"Outline generation error: {e}")
                    raise


ll = BatchOutliner('deepseek')
ll.split_into_batches()