from openai import OpenAI
import os
from dotenv import load_dotenv
from aiparameters import AIParameters
import time
import pandas as pd

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)




# Get the prompt from the instruction

datafile = input("Do you want to upload a file also? (yes/no): ")
while datafile != 'no' and datafile != 'No' and datafile != 'NO' and datafile != 'n' and datafile != 'N':
    if datafile == 'yes' or datafile == 'Yes' or datafile == 'YES' or datafile == 'y' or datafile == 'Y':
        fileh = str(input("Enter the absolute path of the file: "))
        try:
            if fileh.endswith('.txt'):
                try:
                    with open(fileh, 'r') as file:
                        fileh = file.read()
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    fileh = ''
                    break
            elif fileh.endswith('.xlsx'):
                try:
                    df = pd.read_excel(fileh)
                    fileh = df.to_string()
                    fileh = fileh[ : 1000]
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    fileh = ''
                    break
        except Exception as e:
            print(f"Error: {e}")
            fileh = ''
            break



# Get the prompt from the user
user_prompt = input("Enter your prompt: ")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": AIParameters().data_analysis(),
        },
        {
            "role": "user",
            "content": user_prompt +' ' + fileh,
        }
    ],
    model="gpt-4", # Replace to use the GPT-4 model or any other model
    max_tokens= 2500,
    temperature=0.7,
)

# Extract the assistant's reply from the responsez
assistant_reply = chat_completion.choices[0].message.content


# Append the assistant's reply to the novel
with open('/mnt/cf36a2d7-ecf4-46c7-a76a-5defe1ad7659/my_ai/sources/projectacademus/novel.txt', 'a') as file:
    file.write(assistant_reply + '\n')


    

