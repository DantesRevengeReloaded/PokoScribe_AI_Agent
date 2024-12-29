import os, shutil, PyPDF2, time, tiktoken, logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from chat_gpt.gptpars import *
from logs.ai_z_logsconfig import *
import google.generativeai as genai
from gemini.geminipars import *
from deepseek.deepseekpars import *

# Initialize logging
config = get_log_config()
setup_logging(config)

# Get logger
logger = logging.getLogger('PDFSummarizer')

model_lists = ['openai', 'gemini', 'deepseek']

aiparameters = None
summparameters = None

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
            self.client = OpenAI(api_key=api_key)

            with open(summparameters.prompts_summarization, 'r') as file:
                self.prompt_draft = file.read()

            with open(summparameters.role_of_bot_summarization, 'r') as file:
                self.role_draft = file.read()
        except Exception as e:
            logger.error(f"Error initializing AISummarizer: {e}")
      

    def summarize(self, text, worked_model):
        prompt = f"{self.prompt_draft}:\n\n{text}"
        logger.info("SESSION INFO:")
        logger.info(f"using source model: {worked_model}")
        logger.info(f"using model: {aiparameters.model}")
        logger.info(f"max tokens: {aiparameters.max_tokens}")
        logger.info(f"temperature: {aiparameters.temperature}")
        logger.info(f"role system: {aiparameters.role_system}")
        logger.info(f"role user: {aiparameters.role_user}")
        logger.info(f"prompt: {self.prompt_draft}")

        # change the schema depending on the model
        if worked_model == 'openai' or worked_model == 'deepseek':
            response = self.client.chat.completions.create(
                messages=[
                    {"role": f"{aiparameters.role_system}", "content": f"{self.role_draft}"},
                    {"role": f"{aiparameters.role_user}", "content": prompt}
                ],
                model=aiparameters.model,
                max_tokens=aiparameters.max_tokens,
                temperature=aiparameters.temperature,
            )
            summary = response.choices[0].message.content.strip()
            return summary
        
        elif worked_model == 'gemini':
            generation_config = {
            "temperature": aiparameters.temperature,
            "top_p": aiparameters.top_p,
            "top_k": aiparameters.top_k,
            "max_output_tokens": aiparameters.max_tokens,
            "response_mime_type": aiparameters.response_mime_type
            }

            model = genai.GenerativeModel(
            model_name=aiparameters.model,
            generation_config=generation_config,
            )

            chat_session = model.start_chat(
            history=[
            ]
            )
            prompt = f"{self.prompt_draft}:\n\n{text}"

            summary = chat_session.send_message(prompt)
            return summary
        else:
            logger.error(f"Model {worked_model} not found in the list of available models: {model_lists}")
            return None

class PDFSummarizer:
    def __init__(self, input_folder, output_file, api_key, completed_folder, to_be_completed_folder):
        try:
            logger.info("Initializing PDFSummarizer...")
            self.input_folder = input_folder
            self.output_file = output_file
            self.summarizer = AISummarizer(api_key)
            self.completed_folder = completed_folder
            self.to_be_completed_folder = to_be_completed_folder
            self.limittokens = aiparameters.tokenslimit
            # Create directories if they do not exist
            os.makedirs(self.completed_folder, exist_ok=True)
            os.makedirs(self.to_be_completed_folder, exist_ok=True)
            self.totalfilesprocessed = 0
            self.completedfiles = 0
            logger.info("PDFSummarizer initialized without errors.")

        except Exception as e:
            logger.error(f"Error initializing PDFSummarizer: {e}")


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



