from openai import OpenAI
from dotenv import load_dotenv
import os

bot_model = "gpt-4o-mini"
role_of_bot = "you are an academic who wants to write a chapter for a paper about the risks in e-learning in businesses"
prompt_draft = "create from the following text a chapter for a paper about the difference between e-learning and other forms of digital transformation"

with open('z_diplo_maria/summary_v2.txt', 'r') as file:
    notes_file = file.read()

class OpenAIChapterMaker:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.role_of_bot = role_of_bot
        self.prompt_draft = prompt_draft
        self.bot_model = bot_model
        self.text = notes_file
    
      

    def create_chapter(self):
        prompt = f"{self.prompt_draft}:\n\n{self.text}"

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{self.role_of_bot}"},
                {"role": "user", "content": prompt}
            ],
            model=self.bot_model,
            max_tokens=5500,
            temperature=0.7,
        )

        chapter = response.choices[0].message.content.strip()
        return chapter
    
if __name__ == "__main__":
    load_dotenv('.env')
    api_key = os.getenv('OPENAI_API_KEY')
    chapter_maker = OpenAIChapterMaker(api_key)
    chapter = chapter_maker.create_chapter()
    with open('z_diplo_maria/chapter_v2.txt', 'w') as file:
        file.write(chapter)
        print("Chapter created and saved to chapter_v2.txt")
