from openai import OpenAI
from dotenv import load_dotenv
import os
from src.agents.config import *

aiparameters = ChatGPTPars()
chaptermaker_ai_parameters = ChatGPTChapterMakerPars()

with open(chaptermaker_ai_parameters.paper_file, 'r') as file:
    notes_file = file.read()

class AIChapterMaker:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.role_of_bot = chaptermaker_ai_parameters.role_of_bot_chapter
        self.prompt_draft = chaptermaker_ai_parameters.prompts_chapter
        self.bot_model = aiparameters.model
        self.text = notes_file
    

    def create_chapter(self):
        prompt = f"{self.prompt_draft}:\n\n{self.text}"
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": f"{aiparameters.role_system}", "content": f"{self.role_of_bot}"},
                    {"role": f"{aiparameters.role_user}", "content": prompt}
                ],
                model=aiparameters.model,
                max_tokens=aiparameters.max_tokens,
                temperature=aiparameters.temperature,
            )

            chapter = response.choices[0].message.content.strip()
            return chapter
        except Exception as e:
            print(e)
            return None
    
if __name__ == "__main__":
    load_dotenv('.env')
    api_key = os.getenv('OPENAI_API_KEY')
    chapter_maker = AIChapterMaker(api_key)
    chapter = chapter_maker.create_chapter()
    with open(chaptermaker_ai_parameters.chapters_historicity, 'a') as file:
        file.write(chapter_maker.prompt_draft)
        file.write('\nAnswer\n')
        file.write(chapter)
        file.write('\n\n--------\n')
