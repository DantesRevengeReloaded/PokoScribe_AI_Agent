from openai import OpenAI
import os
from dotenv import load_dotenv
from aiparameters import AIParameters

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)
# Read the content of the file
with open('sources/testing/novelinstructs.txt', 'r') as file:
    content = file.read()

# Split the content by the delimiter to get the instructions
instructions = content.split('--')

# Loop over the instructions
for instruction in instructions:
    # Get the prompt from the instruction
    prompt1 = instruction.strip()


    # Read the existing content of the novel
    with open('sources/testing/novel.txt', 'r') as file:
        novel_content = file.read()

    novel_content = novel_content[-1000:] # Use only the last 1000 characters so the model can process it and dont be expensive
    # Get the prompt from the user
    user_prompt = prompt1 #input("Enter your prompt: ")

    # Append the specific message to the user's input
    prompt = 'Create a section of the novel making a chapter using the following sources as basic source for creating the story part: ' + user_prompt + ' Consider that the answer will append the following: ' + novel_content

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": AIParameters().openainovel(),
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
        max_tokens= 2000,
        temperature=0.7,
    )

    # Extract the assistant's reply from the response
    assistant_reply = chat_completion.choices[0].message.content


    # Append the assistant's reply to the novel
    with open('sources/testing/novel.txt', 'a') as file:
        file.write(assistant_reply + '\n')