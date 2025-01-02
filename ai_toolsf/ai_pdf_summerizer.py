import os, shutil, PyPDF2, time, tiktoken, logging, sys

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openai import OpenAI
from dotenv import load_dotenv
from typing import List
import models.chat_gpt.gptpars
from models.chat_gpt.gptpars import *
from logs.ai_z_logsconfig import *
import google.generativeai as genai
from models.gemini.geminipars import *
from models.deepseek.deepseekpars import *

# Initialize logging
config = get_log_config()
setup_logging(config)

# Get logger
logger = logging.getLogger('PDFSummarizer')

model_lists = ['openai', 'gemini', 'deepseek']

def initialize_parameters(model_type: str):
    global aiparameters, summparameters
    
    if model_type not in model_lists:
        raise ValueError(f"Invalid model type. Must be one of {model_lists}")
    
    if model_type == 'openai':
        aiparameters = ChatGPTPars()
        summparameters = ChatGPTPdfSummerizerPars()
    elif model_type == 'gemini':
        aiparameters = GeminiPars()
        summparameters = GeminiSummerizerPars()
    elif model_type == 'deepseek':
        aiparameters = DeepSeekPars()
        summparameters = DeepSeekSummerizerPars()
    
    if not aiparameters or not summparameters:
        raise RuntimeError("Failed to initialize AI parameters")

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        try:
            logger.info(f"Reading {self.file_path}...")
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error reading {self.file_path}: {e}")
            return None

class AISummarizer:
    def __init__(self, api_key):
        try:
            self.api_key = api_key
            
            # Convert to absolute paths
            prompt_path = os.path.abspath(summparameters.prompts_summarization)
            role_path = os.path.abspath(summparameters.role_of_bot_summarization)
            
            logger.info(f"Absolute prompt path: {prompt_path}")
            logger.info(f"Absolute role path: {role_path}")

            # Validate files exist and are not empty
            if not os.path.exists(prompt_path):
                raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            if not os.path.getsize(prompt_path):
                raise ValueError(f"Prompt file is empty: {prompt_path}")
                
            if not os.path.exists(role_path):
                raise FileNotFoundError(f"Role file not found: {role_path}")
            if not os.path.getsize(role_path):
                raise ValueError(f"Role file is empty: {role_path}")

            # Load prompts with UTF-8 encoding and error handling
            try:
                with open(prompt_path, 'r', encoding='utf-8-sig') as file1:
                    self.prompt_draft = file1.read().strip()
                    if not self.prompt_draft:
                        raise ValueError("Prompt file read but content is empty")
                logger.info(f"Prompt loaded successfully, content preview: {self.prompt_draft[:50]}...")
            except Exception as e:
                logger.error(f"Error reading prompt file: {e}")
                raise

            try:
                with open(role_path, 'r', encoding='utf-8-sig') as file2:
                    self.role_draft = file2.read().strip()
                    if not self.role_draft:
                        raise ValueError("Role file read but content is empty")
                logger.info(f"Role loaded successfully, content preview: {self.role_draft[:50]}...")
            except Exception as e:
                logger.error(f"Error reading role file: {e}")
                raise

        except Exception as e:
            logger.error(f"Error in AISummarizer initialization: {e}")
            raise
      

    def summarize(self, text, worked_model):
        
        logger.info("SESSION INFO:")
        logger.info(f"using source model: {worked_model}")
        logger.info(f"using model: {aiparameters.model}")
        logger.info(f"max tokens: {aiparameters.max_tokens}")
        logger.info(f"temperature: {aiparameters.temperature}")
        logger.info(f"role system: {aiparameters.role_system}")
        logger.info(f"role user: {aiparameters.role_user}")
        logger.info(f"prompt: {self.prompt_draft}")

        # change the schema depending on the model
        if worked_model == 'openai':
            try:
                prompt = f"{self.prompt_draft}: {text}"
            except Exception as e:
                logger.error(f"Error creating prompt: {str(e)}")
                return None
            try:
                self.client = OpenAI(api_key=self.api_key)
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": f"{aiparameters.role_system}", "content": f"{self.role_draft}"},
                        {"role": f"{aiparameters.role_user}", "content": prompt}
                    ],
                    model=aiparameters.model,
                    max_tokens=aiparameters.max_tokens,
                    temperature=aiparameters.temperature,
                )
            except Exception as e:
                logger.error(f"Error in OpenAI workflow: {str(e)}")
                return None
            
            try:
                summary = response.choices[0].message.content.strip()
                return summary
                
            except Exception as e:
                logger.error(f"Error in OpenAI response: {str(e)}")
                return None
        
        elif worked_model == 'deepseek':
            try:
                prompt = f"{self.prompt_draft}: {text}"
            except Exception as e:
                logger.error(f"Error creating prompt: {str(e)}")
                return None
            try:
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": f"{aiparameters.role_system}", "content": f"{self.role_draft}"},
                        {"role": f"{aiparameters.role_user}", "content": prompt}
                    ],
                    model=aiparameters.model,
                    max_tokens=aiparameters.max_tokens,
                    temperature=aiparameters.temperature,
                )
            except Exception as e:
                logger.error(f"Error in DeepSeek workflow: {str(e)}")
                return None
            try:
                summary = response.choices[0].message.content.strip()
                return summary
            except Exception as e:
                logger.error(f"Error in DeepSeek response: {str(e)}")
                return None
        
        elif worked_model == 'gemini':
          
            if isinstance(aiparameters.temperature, tuple):
                ttemperature = float(aiparameters.temperature[0])
            else:
                ttemperature = float(aiparameters.temperature)
            
            try:
                top_p = float(aiparameters.top_p[0]) if isinstance(aiparameters.top_p, tuple) else float(aiparameters.top_p)
                top_k = int(aiparameters.top_k[0]) if isinstance(aiparameters.top_k, tuple) else int(aiparameters.top_k)
            except Exception as e:
                logger.error(f"Invalid top_p or top_k: {aiparameters.top_p}, {aiparameters.top_k}. Error: {e}")
                return "Error: Invalid top_p or top_k values."
            
            try:
                genai.configure(api_key=self.api_key)
                generation_config = {
                    "temperature": ttemperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "max_output_tokens": aiparameters.max_tokens,
                    "response_mime_type": aiparameters.response_mime_type,
                }
                mod = genai.GenerativeModel(
                    model_name=str(aiparameters.model),
                    generation_config=generation_config,
                )
                prompt = f"{self.prompt_draft}: {text}"
                chat_session = mod.start_chat(history=[])
                
                try:
                    response = chat_session.send_message(prompt)
                except Exception as e:
                    logger.error(f"Error during send_message: {str(e)}")
                    raise
                
                if not response or not hasattr(response, 'text'):
                    logger.error("No valid text in Gemini response.")
                    return "Error: No valid response text."
                
                summary = response.text.strip()
                if not summary:
                    logger.error("Empty summary generated.")
                    return "Error: Empty summary."
                
                logger.info("Summary generated successfully in Gemini.")
                return summary

            except Exception as e:
                logger.error(f"Error in Gemini workflow: {str(e)}")
                return None

class PDFSummarizer:
    def __init__(self, input_folder, output_file, api_key, completed_folder, 
                 to_be_completed_folder, model_type):
        """
        Initialize PDFSummarizer with parameters.
        Args:
            input_folder (str): Folder containing PDFs to process
            output_file (str): Output file for summaries
            api_key (str): API key for AI service
            completed_folder (str): Folder for processed PDFs
            to_be_completed_folder (str): Folder for failed PDFs
            model_type (str): AI model type to use check the model_lists
        """
        try:
            logger.info("Initializing PDFSummarizer...")
            # Initialize parameters based on model type passed in main
            initialize_parameters(model_type)
            self.input_folder = input_folder
            self.output_file = output_file
            self.summarizer = AISummarizer(api_key)
            self.completed_folder = completed_folder
            self.to_be_completed_folder = to_be_completed_folder
            self.limittokens = aiparameters.tokenslimit
            self.model_type = model_type
            # Create directories if they do not exist
            os.makedirs(self.completed_folder, exist_ok=True)
            os.makedirs(self.to_be_completed_folder, exist_ok=True)
            self.totalfilesprocessed = 0
            self.completedfiles = 0
            logger.info("PDFSummarizer initialized without errors.")

        except Exception as e:
            logger.error(f"Error initializing PDFSummarizer: {e}")
            raise


    def process_pdfs(self, worked_model):
        try:
            pdf_files = [os.path.join(self.input_folder, f) for f in os.listdir(self.input_folder) if f.endswith('.pdf')]
            logger.info(f"Found {len(pdf_files)} PDF files in {self.input_folder}...")
        except Exception as e:
            logger.error(f"Error finding PDF files in {self.input_folder}: {e}")
            return
        for pdf_file in pdf_files:
            self.totalfilesprocessed += 1
            try:
                logger.info(f"Processing {pdf_file}...")
                reader = PDFReader(pdf_file)
                pdf_text = reader.read()
                encoding = tiktoken.get_encoding("cl100k_base")
                tokencount = len(encoding.encode(pdf_text))
                logger.info(f"Token count of {pdf_file}: {tokencount}")
                if tokencount < self.limittokens: # adjust the limit of tokens per document in parameters of ai
                   logger.info(f"Summarizing {pdf_file} (less than 27k tokens)...")
                   summary = self.summarizer.summarize(pdf_text, worked_model)
                else:
                    logger.info(f"Summarizing {pdf_file} (more than 27k tokens, chunking method initiated)...")
                    tokens = encoding.encode(pdf_text)
                    chunks = []
                    chunk_summaries = []
                    chunksize = self.limittokens
                    for i in range(0, len(tokens), chunksize):
                        try:
                            chunk = encoding.decode(tokens[i:i + chunksize])
                            chunks.append(chunk)
                            chunknums = 0
                            for chunk in chunks:
                                chunksummary = self.summarizer.summarize(chunk, worked_model)
                                chunk_summaries.append(chunksummary)
                                chunknums += 1
                        except Exception as e:
                            logger.error(f"Error summarizing using chunk in {chunknums} chunk: {e}")
                    logger.info(f"Chunk of{chunknums} parts of initial file summarized in total.")
                    summary = ' '.join(chunk_summaries)
                    logger.info(f"Summary of {pdf_file}:\n{summary}")

                with open(self.output_file, 'a') as file:
                    try:
                        file.write(f"Summary of {pdf_file}:\n")
                        file.write(summary + '\n\n')
                        file.write('--------\n\n')
                        logger.info(f"Summary of {pdf_file} saved to {self.output_file}")
                        self.completedfiles += 1
                    except Exception as e:
                        logger.error(f"Error saving summary of {pdf_file} to {self.output_file}: {e}")

                # Move the file to the completed folder
                shutil.move(pdf_file, os.path.join(self.completed_folder, os.path.basename(pdf_file)))
                logger.info(f"{pdf_file} moved to {self.completed_folder} waiting 3 seconds for next file...")
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
                # Move the file to the to be completed folder
                shutil.move(pdf_file, os.path.join(self.to_be_completed_folder, os.path.basename(pdf_file)))
                logger.info(f"{pdf_file} moved to {self.to_be_completed_folder}")



