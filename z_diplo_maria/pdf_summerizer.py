import os
import shutil
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
import time

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

        with open('z_diplo_maria/academics_promts/promt_summarization.txt', 'r') as file:
            self.prompt_draft = file.read()

        with open('z_diplo_maria/academics_promts/role_of_bot.txt', 'r') as file:
            self.role_draft = file.read()
      

    def summarize(self, text):
        prompt = f"{self.prompt_draft}:\n\n{text}"
        print(self.prompt_draft)

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{self.role_draft}"},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o-mini",
            max_tokens=3500,
            temperature=0.7,
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
                summary = self.summarizer.summarize(pdf_text)

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
    load_dotenv('.env')
    api_key = os.getenv('OPENAI_API_KEY')

    input_folder = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/test'
    big_text_file = 'big_summary.txt'
    completed_folder = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/completed'
    to_be_completed_folder = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/to_be_completed'

    summarizer = PDFSummarizer(input_folder, big_text_file, api_key, completed_folder, to_be_completed_folder)
    summarizer.process_pdfs()