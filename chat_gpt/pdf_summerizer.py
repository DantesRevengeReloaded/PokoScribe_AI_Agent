import os, shutil, PyPDF2, time, tiktoken
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
import chat_gpt.gptpars as gptpars
from gptpars import *

gtppars = ChatGPTPars()
summpars = PdfSummerizerPars()

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with open(self.file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
        return text

class OpenAISummarizer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

        with open(summpars.prompts_summarization, 'r') as file:
            self.prompt_draft = file.read()

        with open(summpars.role_of_bot_summarization, 'r') as file:
            self.role_draft = file.read()
      

    def summarize(self, text):
        prompt = f"{self.prompt_draft}:\n\n{text}"
        response = self.client.chat.completions.create(
            messages=[
                {"role": f"{gtppars.role_system}", "content": f"{self.role_draft}"},
                {"role": f"{gtppars.role_user}", "content": prompt}
            ],
            model=gtppars.model,
            max_tokens=gtppars.max_tokens,
            temperature=gtppars.temperature,
        )

        summary = response.choices[0].message.content.strip()
        return summary

class PDFSummarizer:
    def __init__(self, input_folder, output_file, api_key, completed_folder, to_be_completed_folder):
        self.input_folder = input_folder
        self.output_file = output_file
        self.summarizer = OpenAISummarizer(api_key)
        self.completed_folder = completed_folder
        self.to_be_completed_folder = to_be_completed_folder
        self.limittokens = gtppars.tokenslimit

        # Create directories if they do not exist
        os.makedirs(self.completed_folder, exist_ok=True)
        os.makedirs(self.to_be_completed_folder, exist_ok=True)

    def process_pdfs(self):
        pdf_files = [os.path.join(self.input_folder, f) for f in os.listdir(self.input_folder) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            try:
                print(f"Processing {pdf_file}...")
                reader = PDFReader(pdf_file)
                pdf_text = reader.read()
                encoding = tiktoken.get_encoding("cl100k_base")
                tokencount = len(encoding.encode(pdf_text))
                if tokencount < self.limittokens: # adjust the limit of tokens per document in parameters of ai
                    summary = self.summarizer.summarize(pdf_text)
                else:
                    tokens = encoding.encode(pdf_text)
                    chunks = []
                    chunk_summaries = []
                    chunksize = self.limittokens
                    for i in range(0, len(tokens), chunksize):
                        chunk = encoding.decode(tokens[i:i + chunksize])
                        chunks.append(chunk)
                        for chunk in chunks:
                            chunksummary = self.summarizer.summarize(chunk)
                            chunk_summaries.append(chunksummary)
                    summary = ' '.join(chunk_summaries)

                with open(self.output_file, 'a') as file:
                    file.write(f"Summary of {pdf_file}:\n")
                    file.write(summary + '\n\n')
                    file.write('--------\n\n')

                # Move the file to the completed folder
                shutil.move(pdf_file, os.path.join(self.completed_folder, os.path.basename(pdf_file)))
                time.sleep(5)

            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
                # Move the file to the to be completed folder
                shutil.move(pdf_file, os.path.join(self.to_be_completed_folder, os.path.basename(pdf_file)))

if __name__ == "__main__":
    try:
        load_dotenv('.env')
        api_key = os.getenv('OPENAI_API_KEY')
        summarizer = PDFSummarizer(summpars.input_folder, summpars.big_text_file, api_key, 
                                   summpars.completed_folder, summpars.to_be_completed_folder)
        summarizer.process_pdfs()
    except Exception as e:
        print(f"Error: {e}")