from ai_toolsf.ai_z_folder_pars import *
'''


'''
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
        
        self.prompts_summarization = 'deepseek/prompts-roles/summarization_prompt.txt'
        self.role_of_bot_summarization = 'deepseek/prompts-roles/summarization_role.txt'
        
        # filed where summerizes are saved, if the file becomes source for chapters
        # be sure there are no other summeries and get wrong results
        self.big_text_file = 'deepseek/history/big_summary.txt'

class DeepSeekChapterMakerPars:
    def __init__(self):
        self.prompts_chapter = 'deepseek/prompts-roles/chapter__maker_prompt.txt'
        self.role_of_bot_chapter = 'deepseek/prompts-roles/chapter_maker_role.txt'

        # file with the text to be used as a source, propably produced by the summarizer
        self.paper_file = 'deepseek\paper.txt' 
        
        # file with the chapters produced by the chatbot appended ech time
        self.chapters_historicity = 'deepseek/history/chapters.txt'