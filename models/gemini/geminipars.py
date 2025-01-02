from ai_toolsf.ai_z_folder_pars import *
'''
Available models:



'''
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