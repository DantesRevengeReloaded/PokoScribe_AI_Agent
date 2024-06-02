import openai

openai.api_key ='sk-proj-fukOzHPXqpbA5UMcRbnLT3BlbkFJPY9Zae3yLm7l0PUuRUyK'

def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-004",  # You can choose a different engine like 'gpt-3.5-turbo'
        prompt=prompt,
        max_tokens=150,  # Adjust this value based on your needs
        n=1,
        stop=None,
        temperature=0.7,  # Adjust the creativity of the response
    )
    return response.choices[0].text.strip()

# Example usage
if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    response = generate_response(prompt)
    print(response)