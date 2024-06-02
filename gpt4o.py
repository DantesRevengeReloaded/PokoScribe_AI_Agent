from openai import OpenAI

openai.api_key ='sk-proj-fukOzHPXqpbA5UMcRbnLT3BlbkFJPY9Zae3yLm7l0PUuRUyK'

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can choose a different model like 'gpt-3.5-turbo'
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=150,  # Adjust this value based on your needs
        n=1,
        temperature=0.7,  # Adjust the creativity of the response
    )
    return response['choices'][0]['message']['content'].strip()

# Example usage
if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    response = generate_response(prompt)
    print(response)