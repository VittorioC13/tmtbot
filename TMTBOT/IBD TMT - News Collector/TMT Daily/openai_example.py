import openai
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client
client = openai.Client(api_key=OPENAI_API_KEY)

def get_completion(prompt, model="gpt-3.5-turbo", temperature=0.7):
    """
    Get a completion from OpenAI's API.
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use (default: gpt-3.5-turbo)
        temperature (float): Controls randomness (0-1, default: 0.7)
        
    Returns:
        str: The model's response
    """
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        # Return the response text
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_completion_with_system(prompt, system_message, model="gpt-3.5-turbo", temperature=0.7):
    """
    Get a completion with a system message from OpenAI's API.
    
    Args:
        prompt (str): The prompt to send to the API
        system_message (str): The system message to set the AI's behavior
        model (str): The model to use (default: gpt-3.5-turbo)
        temperature (float): Controls randomness (0-1, default: 0.7)
        
    Returns:
        str: The model's response
    """
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        
        # Return the response text
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_chat_completion(messages, model="gpt-3.5-turbo", temperature=0.7):
    """
    Get a chat completion from OpenAI's API.
    
    Args:
        messages (list): List of message dictionaries with 'role' and 'content'
        model (str): The model to use (default: gpt-3.5-turbo)
        temperature (float): Controls randomness (0-1, default: 0.7)
        
    Returns:
        str: The model's response
    """
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        
        # Return the response text
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    # Simple completion
    prompt = "What are the three main types of machine learning?"
    response = get_completion(prompt)
    print("\nSimple Completion:")
    print(response)
    
    # Completion with system message
    system_msg = "You are a helpful coding assistant that explains concepts clearly and provides code examples."
    prompt = "Explain how to use a try-except block in Python."
    response = get_completion_with_system(prompt, system_msg)
    print("\nCompletion with System Message:")
    print(response)
    
    # Chat completion with multiple messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language known for its simplicity and readability."},
        {"role": "user", "content": "What are its main features?"}
    ]
    response = get_chat_completion(messages)
    print("\nChat Completion:")
    print(response) 