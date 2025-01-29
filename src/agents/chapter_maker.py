import os, sys, json
from pathlib import Path
from typing import List, Dict
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from logs.pokolog import PokoLogger, ScriptIdentifier
from src.tools.token_counter import TokenCounter
from src.config import SystemPars, DeepSeekPars, ChatGPTPars

logger = PokoLogger()
load_dotenv('.env')

class BatchChapterMaker:
    def __init__(self):
        logger.info(ScriptIdentifier.CHAPTER, "Initializing BatchChapterMaker")
        self.summary_file = SystemPars().big_text_file
        self.token_limit = SystemPars().token_limit
        self.batches = []
        self.cached_responses = []

        try:
            self.role_text = self._read_file(SystemPars().role_of_bot_chapter)
            self.batch_prompt_text = self._read_file(SystemPars().prompts_chapter)
            self.synthesis_prompt_text = self._read_file(SystemPars().prompts_synthesis_chapter)
            self._split_text_into_batches()
            logger.info(ScriptIdentifier.CHAPTER, "BatchChapterMaker initialized successfully")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Error initializing BatchChapterMaker: {e}")
            raise

    def _read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _split_text_into_batches(self) -> None:
        full_text = TokenCounter().safe_read_text(self.summary_file)
        current_batch = ""
        current_tokens = 0
        total_tokens = 0

        for paragraph in full_text.split('\n\n'):
            paragraph_tokens = TokenCounter().count_tokens(paragraph)
            total_tokens += paragraph_tokens

            if current_tokens + paragraph_tokens > self.token_limit:
                self.batches.append(current_batch)
                current_batch = paragraph
                current_tokens = paragraph_tokens
            else:
                current_batch += "\n\n" + paragraph if current_batch else paragraph
                current_tokens += paragraph_tokens

        if current_batch:
            self.batches.append(current_batch)

        logger.info(ScriptIdentifier.CHAPTER, f"Split text into {len(self.batches)} batches")
        logger.info(ScriptIdentifier.CHAPTER, f"Total tokens in summary text: {total_tokens}")

    def make_chapter(self) -> None:
        self.cached_responses = []
        for i, batch in enumerate(self.batches, 1):
            logger.info(ScriptIdentifier.CHAPTER, f"Processing batch {i} out of {len(self.batches)}")
            batch_content = self._process_batch(batch, i)
            if batch_content:
                self.cached_responses.append(batch_content)
        if self.cached_responses:
            self._process_synthesis()

    def _process_batch(self, batch: str, batch_number: int) -> str:
        retries = self._get_retry_count()
        for attempt in range(retries + 1):
            try:
                logger.info(ScriptIdentifier.CHAPTER, f"Sending batch and prompt to AI model...")
                prompt = f"{self.batch_prompt_text}\n\n{batch}"
                client = self._get_client()
                messages = self._build_messages(prompt)
                parameters = self._get_api_parameters()
                response = client.chat.completions.create(messages=messages, **parameters)
                logger.info(ScriptIdentifier.CHAPTER, f"Received response for batch {batch_number}")
                content = response.choices[0].message.content
                cleaned_content = self._clean_response(content)
                logger.info(ScriptIdentifier.CHAPTER, f"Cleaned response for batch {batch_number}")
                
                self._write_batch_response(cleaned_content, batch_number)
                logger.info(ScriptIdentifier.CHAPTER, f"Batch {batch_number} processed successfully")
                return cleaned_content
            except Exception as e:
                if attempt < retries and isinstance(e, self._get_retry_exceptions()):
                    logger.warning(ScriptIdentifier.CHAPTER, 
                                 f"Retry {attempt+1}/{retries} for batch {batch_number}: {str(e)}")
                else:
                    logger.error(ScriptIdentifier.CHAPTER, 
                               f"Failed processing batch {batch_number}: {str(e)}")
                    return ""

        return ""

    def _process_synthesis(self) -> None:
        try:
            logger.info(ScriptIdentifier.CHAPTER, "Processing synthesis of all batches...")
            synthesis_prompt = f"{self.synthesis_prompt_text}\n\n{' '.join(self.cached_responses)}"
            client = self._get_client()
            messages = self._build_messages(synthesis_prompt)
            parameters = self._get_api_parameters()
            
            response = client.chat.completions.create(messages=messages, **parameters)
            final_content = response.choices[0].message.content
            self._write_final_response(final_content)
            logger.info(ScriptIdentifier.CHAPTER, "Synthesis processing completed and written to file")
        except Exception as e:
            logger.error(ScriptIdentifier.CHAPTER, f"Synthesis processing failed: {str(e)}")

    def _get_retry_count(self) -> int:
        return 0

    def _get_retry_exceptions(self) -> tuple:
        return ()

    def _get_client(self):
        raise NotImplementedError

    def _build_messages(self, prompt: str) -> List[Dict]:
        raise NotImplementedError

    def _get_api_parameters(self) -> Dict:
        raise NotImplementedError

    @staticmethod
    def _clean_response(response_text: str) -> str:
        cleaned = response_text.strip()
        if cleaned.startswith(('{', '[')):
            try:
                return json.dumps(json.loads(cleaned))
            except json.JSONDecodeError:
                pass
        return cleaned

    def _write_batch_response(self, content: str, batch_number: int) -> None:
        with open('resources/output_of_ai/chapters.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'='*20}\nBatch {batch_number} Response\n{'='*20}\n{content}")

    def _write_final_response(self, content: str) -> None:
        with open('resources/output_of_ai/chapters.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'#'*20}\nFinal Chapter Response\n{'#'*20}\n{content}")


class DeepSeekChapterMaker(BatchChapterMaker):
    def __init__(self):
        super().__init__()
        logger.info(ScriptIdentifier.CHAPTER, "Initializing DeepSeekChapterMaker")
        self.aiparameters = DeepSeekPars()
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self._log_parameters()

    def _log_parameters(self) -> None:
        logger.info(ScriptIdentifier.CHAPTER, "DeepSeek Parameters:")
        logger.info(ScriptIdentifier.CHAPTER, f"Model: {self.aiparameters.model}")
        logger.info(ScriptIdentifier.CHAPTER, f"Max tokens: {self.aiparameters.max_tokens}")
        logger.info(ScriptIdentifier.CHAPTER, f"Temperature: {self.aiparameters.temperature}")

    def _get_client(self):
        return OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def _build_messages(self, prompt: str) -> List[Dict]:
        return [
            {"role": "system", "content": self.role_text},
            {"role": "user", "content": prompt}
        ]

    def _get_api_parameters(self) -> Dict:
        return {
            "model": self.aiparameters.model,
            "max_tokens": self.aiparameters.max_tokens,
            "temperature": self.aiparameters.temperature
        }

    def _get_retry_count(self) -> int:
        return 3

    def _get_retry_exceptions(self) -> tuple:
        return (json.JSONDecodeError,)


class ChatGPTChapterMaker(BatchChapterMaker):
    def __init__(self):
        super().__init__()
        logger.info(ScriptIdentifier.CHAPTER, "Initializing ChatGPTChapterMaker")
        self.aiparameters = ChatGPTPars()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self._log_parameters()

    def _log_parameters(self) -> None:
        logger.info(ScriptIdentifier.CHAPTER, "ChatGPT Parameters:")
        logger.info(ScriptIdentifier.CHAPTER, f"Model: {self.aiparameters.model}")
        logger.info(ScriptIdentifier.CHAPTER, f"Max tokens: {self.aiparameters.max_tokens}")
        logger.info(ScriptIdentifier.CHAPTER, f"Temperature: {self.aiparameters.temperature}")

    def _get_client(self):
        return OpenAI(api_key=self.api_key)

    def _build_messages(self, prompt: str) -> List[Dict]:
        return [{"role": "user", "content": prompt}]

    def _get_api_parameters(self) -> Dict:
        return {
            "model": self.aiparameters.model,
            "max_completion_tokens": self.aiparameters.max_tokens,
            "temperature": self.aiparameters.temperature
        }


class GeminiChapterMaker(BatchChapterMaker):
    pass  # Implementation pending