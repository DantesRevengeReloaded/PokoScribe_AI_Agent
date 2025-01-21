import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SystemPars:
    def __init__(self):
        # folder with total folders to be summarized, 
        # folder with completed files and folder with files failed to be summarized
        self.input_folder = 'data\summary_agent\input'
        self.completed_folder = 'data\summary_agent\completed'
        self.to_be_completed_folder = 'data\summary_agent\incompleted'

        #prompts and roles for the summarization tools
        self.prompts_summarization = 'prompts-roles\prompts-roles\summarization_prompt.txt'
        self.role_of_bot_summarization = 'prompts-roles\prompts-roles\summarization_role.txt'
        self.citation_sum = 'prompts-roles\prompts-roles\summarization_citation.txt'
        
        # filed where summerizes are saved, if the file becomes source for chapters
        # be sure there are no other summeries and get wrong results
        self.big_text_file = 'prompts-roles\history\summary_total.txt'
        self.prompts_chapter = 'prompts-roles\prompts-roles\chapter_maker_prompt.txt'
        self.role_of_bot_chapter = 'prompts-roles\prompts-roles\chapter_maker_role.txt'

        # file with the text to be used as a source, propably produced by the summarizer
        self.paper_file = 'prompts-roles\prompts-roles\paper.txt' 
        
        # file with the chapters produced by the chatbot appended ech time
        self.chapters_historicity = 'prompts-roles\history\chapters.txt'

        self.project_name = 'Panos_Karydis'

        self.filter_sources_for_dl = 'prompt-engineering\main_for_filtering_resources.txt'

# Define the keywords and search queries to be used in the search of AHSS tool      
def get_keywords() -> list:
    keywords = [
        "job satisfaction",
        "work performance",
        "employee engagement",
        "employee turnover",
        "employee performance",
        "business outcome",
        "productivity",
        "workplace psychology",
        "employee satisfaction",
        "organizational performance"
    ]
    return keywords

def get_search_queries() -> list:
    search_queries = [
            "worker satisfaction business performance",
            "employee psychology productivity",
            "job satisfaction organizational performance",
            "workplace psychology business metrics",
            "employee wellbeing productivity",
            "employee satisfaction",
            "job satisfaction"
        ]
    return search_queries
        
class ChatGPTPars:
    def __init__(self):
        self.model="gpt-4o-mini"
        self.max_tokens=4500 # max output tokens
        self.temperature=0.7
        self.role_system = "system"
        self.role_user = "user"
        self.tokenslimit = 27000 # limit of tokens per document


class ChatGPTPdfSummerizerPars(SystemPars):
    def __init__(self):
        super().__init__()
        

class ChatGPTChapterMakerPars(SystemPars):
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


class DeepSeekSummerizerPars(SystemPars):
    def __init__(self):
        super().__init__()

class DeepSeekChapterMakerPars:
    def __init__(self):
        super().__init__()

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


class GeminiSummerizerPars(SystemPars):
    def __init__(self):
        super().__init__()
        

class GeminiChapterMakerPars(SystemPars):
    def __init__(self):
        super().__init__()