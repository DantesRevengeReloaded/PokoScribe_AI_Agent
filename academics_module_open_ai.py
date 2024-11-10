import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

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

    def summarize(self, text):
        prompt = f"Summarize the following content of an academic article, consider that the :\n\n{text}"

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo",
            max_tokens=2500,
            temperature=0.7,
        )

        summary = response.choices[0].message.content.strip()
        return summary

class PDFSummarizer:
    def __init__(self, pdf_files, output_file, api_key):
        self.pdf_files = pdf_files
        self.output_file = output_file
        self.summarizer = OpenAISummarizer(api_key)

    def process_pdfs(self):
        for pdf_file in self.pdf_files:
            print(f"Processing {pdf_file}...")
            reader = PDFReader(pdf_file)
            pdf_text = reader.read()
            summary = self.summarizer.summarize(pdf_text)

            with open(self.output_file, 'a') as file:
                file.write(f"Summary of {pdf_file}:\n")
                file.write(summary + '\n\n')

if __name__ == "__main__":
    load_dotenv('.env')
    api_key = os.getenv('OPENAI_API_KEY')

    pdf_files = [
        '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/1_DIGITAL_TRANSFORMATION_THEORY/Digital_transformation_conceptual_framew.pdf',
        # Add more PDF file paths as needed
    ]

    big_text_file = 'big_summary.txt'
    try:

        summarizer = PDFSummarizer(pdf_files, big_text_file, api_key)
        summarizer.process_pdfs()
    except Exception as e:
        print(f"Error: {e}")
        