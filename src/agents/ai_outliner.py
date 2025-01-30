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


class BatchOutliner:
    def __init__(self):
        logger.info(ScriptIdentifier.OUTLINER, "Initializing BatchOutliner")
        try:
            sys_params = SystemPars()
            self.summary_file = sys_params.big_text_file
            self.token_limit = sys_params.token_limit
            self.cached_responses = []

            # Initialize token counter
            self.token_count = TokenCounter().count_text(self.summary_file)['tokens']
            
            # Load prompt content
            self._load_prompt_files(sys_params)
            
            # Split text into batches
            full_text = TokenCounter().safe_read_text(self.summary_file)
            self.batches = self._split_into_batches(full_text)
            
            logger.info(ScriptIdentifier.OUTLINER, 
                       f"Split text into {len(self.batches)} batches")
            logger.info(ScriptIdentifier.OUTLINER, "BatchOutliner initialized successfully")   
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Initialization error: {e}")
            raise

    def model_info(self):
        if isinstance(self, DeepSeekOutliner):
            return {"model": "DeepSeek",
                    "parameters": str(self.aiparameters.__dict__)}
        elif isinstance(self, ChatGPTOutliner):
            return {"model": "ChatGPT",
                    "parameters": str(self.aiparameters.__dict__)}
        else:
            return {"model": "Unknown",
                    "parameters": "Unknown"}


    def _load_prompt_files(self, sys_params):
        try:
            """Load required prompt files into memory"""
            self.role_text = self._read_file(sys_params.role_of_bot_outliner)
            self.batch_prompt_text = self._read_file(sys_params.prompts_single_batch)
            self.synthesis_prompt_text = self._read_file(sys_params.prompts_final_synthesis)
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Error loading prompt files: {e}")
            raise

    def _read_file(self, path):
        """Helper method to safely read file contents"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Error reading {path}: {e}")
            raise

    def _split_into_batches(self, text):
        try:
            """Split text into token-limited batches"""
            batches, current_batch, current_tokens = [], "", 0
            for paragraph in text.split('\n\n'):
                para_tokens = TokenCounter().count_tokens(paragraph)
                if current_tokens + para_tokens > self.token_limit:
                    batches.append(current_batch)
                    current_batch, current_tokens = paragraph, para_tokens
                else:
                    current_batch += f"\n\n{paragraph}" if current_batch else paragraph
                    current_tokens += para_tokens
            if current_batch:
                batches.append(current_batch)
            return batches
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Error splitting text into batches: {e}")
            raise

    def _write_output(self, content, prefix, separator_length=20):
        """Universal method for writing output"""
        try:
            with open('resources/output_of_ai/outline.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n\n{'-'*separator_length}\n\n{prefix}\n{content}")
            logger.info(ScriptIdentifier.OUTLINER, f"{prefix} written to file")
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Error writing output: {e}")

    def _create_messages(self, prompt_content: str) -> List[Dict[str, str]]:
        """Create standardized message format for API calls"""
        if isinstance(self, DeepSeekOutliner):
            return [
                {"role": self.aiparameters.role_system, "content": prompt_content},
                {"role": self.aiparameters.role_user, "content": prompt_content}
            ]
        else:  # ChatGPTOutliner
            return [{"role": "user", "content": prompt_content}]

    def _process_api_call(self, prompt: str):
        """Handle API communication with error management"""
        try:
            params = {
                "messages": self._create_messages(prompt),
                "model": self.aiparameters.model,
                "temperature": self.aiparameters.temperature,
            }
            
            # Add model-specific parameters
            if isinstance(self, DeepSeekOutliner):
                params["max_tokens"] = self.aiparameters.max_tokens
            else:  # ChatGPTOutliner
                params["max_completion_tokens"] = self.aiparameters.max_tokens
                
            return self.client.chat.completions.create(**params)
            
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"API call failed: {e}")
            raise

    def outline_it(self):
        """Main processing pipeline"""
        self.cached_responses = []
        modelparams = self.model_info()
        for idx, batch in enumerate(self.batches, 1):
            try:
                logger.info(ScriptIdentifier.OUTLINER, 
                          f"Processing batch {idx}/{len(self.batches)}")
                prompt = f"{self.batch_prompt_text}\n{batch}"
                response = self._process_api_call(prompt)
                content = response.choices[0].message.content
                self.cached_responses.append(content)
                OutlineDb().insert_outline(content, 
                                           SystemPars().project_name, 
                                           modelparams["model"], 
                                           modelparams["parameters"],
                                           f"Batch Outline {idx}")
                
                self._write_output(content, f"Batch Outline {idx}", 10)
            except Exception as e:
                logger.error(ScriptIdentifier.OUTLINER, f"Batch {idx} failed: {e}")

        if self.cached_responses:
            logger.info(ScriptIdentifier.OUTLINER, "Final synthesis in progress")
            try:
                synthesis_prompt = f"{self.synthesis_prompt_text}\n{''.join(self.cached_responses)}"
                response = self._process_api_call(synthesis_prompt)
                OutlineDb().insert_outline(response.choices[0].message.content,
                                           SystemPars().project_name, 
                                           modelparams["model"], 
                                           modelparams["parameters"], 
                                           "Final Outline")
                self._write_output(response.choices[0].message.content, "Final Outline")
                logger.info(ScriptIdentifier.OUTLINER, "Final synthesis completed")
            except Exception as e:
                logger.error(ScriptIdentifier.OUTLINER, f"Final synthesis failed: {e}")


class DeepSeekOutliner(BatchOutliner):
    def __init__(self):
        """DeepSeek-specific initializer"""
        logger.info(ScriptIdentifier.OUTLINER, "Initializing DeepSeekOutliner")
        try:
            super().__init__()
            self.aiparameters = DeepSeekPars()
            self.client = OpenAI(
                api_key=os.getenv('DEEPSEEK_API_KEY'),
                base_url="https://api.deepseek.com"
            )
            logger.info(ScriptIdentifier.OUTLINER, "DeepSeekOutliner ready")
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Initialization failed: {e}")
            raise


class ChatGPTOutliner(BatchOutliner):
    def __init__(self):
        """ChatGPT-specific initializer"""
        logger.info(ScriptIdentifier.OUTLINER, "Initializing ChatGPTOutliner")
        try:
            super().__init__()
            self.aiparameters = ChatGPTPars()
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            logger.info(ScriptIdentifier.OUTLINER, "ChatGPTOutliner ready")
        except Exception as e:
            logger.error(ScriptIdentifier.OUTLINER, f"Initialization failed: {e}")
            raise

tk = ChatGPTOutliner()
tk.outline_it()


