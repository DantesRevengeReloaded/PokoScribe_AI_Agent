
class FolderPars:
    def __init__(self):
        # folder with total folders to be summarized, 
        # folder with completed files and folder with files failed to be summarized
        self.input_folder = 'C:\\Users\\ionka\\Desktop\\tests\\tobesummed'
        self.completed_folder = 'C:\\Users\\ionka\\Desktop\\tests\\completed'
        self.to_be_completed_folder = 'C:\\Users\\ionka\\Desktop\\tests\\problems'
        self.prompts_summarization = 'models/chat_gpt/prompts-roles/summarization_prompt.txt'
        self.role_of_bot_summarization = 'models/chat_gpt/prompts-roles/summarization_role.txt'
        
        # filed where summerizes are saved, if the file becomes source for chapters
        # be sure there are no other summeries and get wrong results
        self.big_text_file = 'models/chat_gpt/history/big_summary.txt'
        self.prompts_chapter = 'models/chat_gpt/prompts-roles/chapter__maker_prompt.txt'
        self.role_of_bot_chapter = 'models/chat_gpt/prompts-roles/chapter_maker_role.txt'

        # file with the text to be used as a source, propably produced by the summarizer
        self.paper_file = 'models/chat_gpt/paper.txt' 
        
        # file with the chapters produced by the chatbot appended ech time
        self.chapters_historicity = 'models/chat_gpt/history/chapters.txt'

        
class ChatGPTPars:
    def __init__(self):
        self.model="gpt-4o-mini"
        self.max_tokens=4500 # max output tokens
        self.temperature=0.7
        self.role_system = "system"
        self.role_user = "user"
        self.tokenslimit = 27000 # limit of tokens per document


class ChatGPTPdfSummerizerPars(FolderPars):
    def __init__(self):
        super().__init__()
        

class ChatGPTChapterMakerPars(FolderPars):
    def __init__(self):
        super().__init__()


class DeepSeekPars:
    def __init__(self):
        self.model="deepseek-chat"
        self.max_tokens=4500 # max output tokens
        self.temperature=0.7
        self.role_system = "system"
        self.role_user = "user"
        self.tokenslimit = 27000 # limit of tokens per document


class DeepSeekSummerizerPars(FolderPars):
    def __init__(self):
        super().__init__()
        
        self.prompts_summarization = 'models/deepseek/prompts-roles/summarization_prompt.txt'
        self.role_of_bot_summarization = 'models/deepseek/prompts-roles/summarization_role.txt'
        
        # filed where summerizes are saved, if the file becomes source for chapters
        # be sure there are no other summeries and get wrong results
        self.big_text_file = 'models/deepseek/history/big_summary.txt'

class DeepSeekChapterMakerPars:
    def __init__(self):
        self.prompts_chapter = 'models/deepseek/prompts-roles/chapter__maker_prompt.txt'
        self.role_of_bot_chapter = 'models/deepseek/prompts-roles/chapter_maker_role.txt'

        # file with the text to be used as a source, propably produced by the summarizer
        self.paper_file = 'models/deepseek\paper.txt' 
        
        # file with the chapters produced by the chatbot appended ech time
        self.chapters_historicity = 'models/deepseek/history/chapters.txt'

class GeminiPars:
    def __init__(self):
        self.model="gemini-1.5-pro"
        self.max_tokens=15000 # max output tokens
        self.temperature = 0.8
        self.role_system = "system"
        self.role_user = "user"
        self.tokenslimit = 27000 # limit of tokens per document
        self.top_p = 0.95, 
        self.top_k = 40,
        self.response_mime_type = "text/plain"


class GeminiSummerizerPars(FolderPars):
    def __init__(self):
        super().__init__()
        
        self.prompts_summarization = 'models/gemini\prompts-roles\summarization_prompt.txt'
        self.role_of_bot_summarization = 'models/gemini\prompts-roles\summarization_role.txt'
        
        # filed where summerizes are saved, if the file becomes source for chapters
        # be sure there are no other summeries and get wrong results
        self.big_text_file = 'models/gemini/history/big_summary.txt'

class GeminiChapterMakerPars:
    def __init__(self):
        self.prompts_chapter = 'models/gemini/prompts-roles/chapter__maker_prompt.txt'
        self.role_of_bot_chapter = 'models/gemini/prompts-roles/chapter_maker_role.txt'

        # file with the text to be used as a source, propably produced by the summarizer
        self.paper_file = 'models/gemini\paper.txt' 
        
        # file with the chapters produced by the chatbot appended ech time
        self.chapters_historicity = 'models/gemini/history/chapters.txt'