from openai import OpenAI
import openai
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)

# Get the prompt from the user
prompt = input("Enter your prompt: ")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="gpt-3.5-turbo",
)

# Extract the assistant's reply from the response
assistant_reply = chat_completion.choices[0].message.content


# Print the assistant's reply
print(assistant_reply)