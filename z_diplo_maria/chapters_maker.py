from openai import OpenAI
from dotenv import load_dotenv
import os

bot_model = "o1-mini"
role_of_bot = "you are an academic student who wants to write a paper about e learning in businesses, you have already summerized the articles and based on that you will synthesize using them as sources and refer to them using harvard reference inside the text"
prompt_draft = "create me the introduction of the paper based on the following text so i can add it to the paper"
with open('/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/my_ai/paper.txt', 'r') as file:
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
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": f"{self.role_of_bot}"},
                    {"role": "user", "content": prompt}
                ],
                model=self.bot_model,
                max_completion_tokens=6500,
                temperature=1,
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
    with open('z_diplo_maria/intro.txt', 'w') as file:
        file.write(chapter)
        print("Chapter created and saved to chapter_v5.txt")
