
from ai_toolsf.ai_z_folder_pars import *
from ai_toolsf.ai_chapters_maker import *
from ai_toolsf.ai_pdf_summerizer import *

class AIBotSummarizer:
    def __init__(self):
        pass
    
    def chatgptsummerize(self):
        try:
            start_time = time.time()
            logger.info("Starting PDFSummarizer...")

            logger.info("Using OpenAI model...")
            aiparameters = ChatGPTPars()
            summparameters = ChatGPTPdfSummerizerPars()
            load_dotenv('.env')
            api_key = os.getenv('OPENAI_API_KEY')
            summarizer = PDFSummarizer(summparameters.input_folder, summparameters.big_text_file, api_key, 
                                    summparameters.completed_folder, summparameters.to_be_completed_folder)
            summarizer.process_pdfs('openai')
            end_time = time.time()
            logger.info(f"PDFSummarizer completed in {end_time - start_time} seconds.")
        except Exception as e:
            logger.error(f"Error in PDFSummarizer: {e}")

    def geminisummerize(self):
        try:
            start_time = time.time()
            logger.info("Using Gemini model...")
            aiparameters = GeminiPars()
            summparameters = GeminiSummerizerPars()
            load_dotenv('.env')
            api_key = os.getenv('GEMINI_API_KEY')
            summarizer = PDFSummarizer(summparameters.input_folder, summparameters.big_text_file, api_key, 
                                    summparameters.completed_folder, summparameters.to_be_completed_folder)
            summarizer.process_pdfs('gemini')
            end_time = time.time()
            logger.info(f"PDFSummarizer completed in {end_time - start_time} seconds.")
            logger.info(f"Total files processed: {summarizer.totalfilesprocessed}")
            logger.info(f"Completed files: {summarizer.completedfiles}")
        except Exception as e:
            logger.error(f"Error in PDFSummarizer: {e}")
        
    def deepseeksummerize(self):
        try:
            start_time = time.time()
            logger.info("Using DeepSeek model...")
            aiparameters = DeepSeekPars()
            summparameters = DeepSeekSummerizerPars()
            load_dotenv('.env')
            api_key = os.getenv('DEEPSEEK_API_KEY')
            summarizer = PDFSummarizer(summparameters.input_folder, summparameters.big_text_file, api_key, 
                                    summparameters.completed_folder, summparameters.to_be_completed_folder)
            summarizer.process_pdfs('deepseek')
            end_time = time.time()
            logger.info(f"PDFSummarizer completed in {end_time - start_time} seconds.")
            logger.info(f"Total files processed: {summarizer.totalfilesprocessed}")
            logger.info(f"Completed files: {summarizer.completedfiles}")
        except Exception as e:
            logger.error(f"Error in PDFSummarizer: {e}")