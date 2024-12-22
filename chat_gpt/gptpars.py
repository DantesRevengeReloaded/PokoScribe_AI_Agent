
'''
Available models:

gpt-4o
$2.50 / 1M input tokens
$1.25 / 1M cached** input tokens
$10.00 / 1M output tokens

gpt-4o-mini
$0.150 / 1M input tokens
$0.075 / 1M cached** input tokens
$0.600 / 1M output tokens

o1
$15.00 / 1M input tokens
$7.50 / 1M cached* input tokens
$60.00 / 1M output** tokens

o1-mini
$3.00 / 1M input tokens
$1.50 / 1M cached* input tokens
$12.00 / 1M output** tokens

'''
class ChatGPTPars:
    def __init__(self):
        self.model="gpt-4o-mini"
        self.max_tokens=4500
        self.temperature=0.7
        self.role_system = "system"
        self.role_user = "user"


class PdfSummerizerPars:
    def __init__(self):
        self.prompts_summarization = 'chat_gpt/prompts-roles/summarization_prompt.txt'
        self.role_of_bot_summarization = 'chat_gpt/prompts-roles/summarization_role.txt'
        self.input_folder = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/test'
        self.big_text_file = 'chat_gpt/history/big_summary.txt'
        self.completed_folder = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/completed'
        self.to_be_completed_folder = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/project_diplo_maria/1 RESEARCH/ACADEMIA/to_be_completed'


class ChapterMakerPars:
    def __init__(self):
        self.prompts_chapter = 'chat_gpt/prompts-roles/chapter__maker_prompt.txt'
        self.role_of_bot_chapter = 'chat_gpt/prompts-roles/chapter_maker_role.txt'
        self.paper_file = '/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/my_ai/paper.txt'
        self.chapters_historicity = 'chat_gpt/history/chapters.txt'