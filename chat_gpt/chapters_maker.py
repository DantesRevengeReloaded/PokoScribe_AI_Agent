from openai import OpenAI
from dotenv import load_dotenv
import os
import chat_gpt.gptpars as gptpars
from gptpars import *

gptpppars = ChatGPTPars()
chapterpars = ChapterMakerPars()

with open(chapterpars.paper_file, 'r') as file:
    notes_file = file.read()

class OpenAIChapterMaker:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.role_of_bot = chapterpars.role_of_bot_chapter
        self.prompt_draft = chapterpars.prompts_chapter
        self.bot_model = gptpppars.model
        self.text = notes_file
    
      

    def create_chapter(self):
        prompt = f"{self.prompt_draft}:\n\n{self.text}"
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": f"{gptpppars.role_system}", "content": f"{self.role_of_bot}"},
                    {"role": f"{gptpppars.role_user}", "content": prompt}
                ],
                model=gptpppars.model,
                max_tokens=gptpppars.max_tokens,
                temperature=gptpppars.temperature,
            )

            chapter = response.choices[0].message.content.strip()
            return chapter
        except Exception as e:
            print(e)
            return None
    
if __name__ == "__main__":
    load_dotenv('.env')
    api_key = os.getenv('OPENAI_API_KEY')
    chapter_maker = OpenAIChapterMaker(api_key)
    chapter = chapter_maker.create_chapter()
    with open(chapterpars.chapters_historicity, 'a') as file:
        file.write(chapter_maker.prompt_draft)
        file.write('\nAnswer\n')
        file.write(chapter)
        file.write('\n\n--------\n')
