import os
from datetime import datetime
import textwrap
import google.generativeai as genai

import os
from dotenv import load_dotenv
from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return textwrap.indent(text, '> ', predicate=lambda _: True)

class GenAIPokoDataCall:
  def __init__(self):
    load_dotenv()
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    # Selecting text model 
    model = genai.GenerativeModel('gemini-pro')
    self.model = model

  def generate_cont(self, prompt):
    response = self.model.generate_content(prompt)
    # Write any prompt of your choice
    prompt_text = str(prompt)
    response_text = to_markdown(response.text)
    responsedate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Create filename using responsedate
    filename = f"answers/response_{responsedate}.txt"

    # Save prompt, blank line, and response.text to a txt file
    with open(filename, 'w') as file:
      file.write(prompt_text + '\n\n' + response_text)

def prompt():
  # Prompt the user to enter a text
  prompt = input("Enter a prompt: ")
  return prompt
  
data_call = GenAIPokoDataCall()
userprompt = prompt()
# Call the generate_content method
data_call.generate_cont(userprompt)
  
