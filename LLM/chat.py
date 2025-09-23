import os
from google import genai

def chat(analysis):
    with open("prompt.txt" ,'r') as file:
        prompt_text = file.read() 

    prompt = f"System Prompt: {prompt_text}, Analysis: {analysis}"

    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)

    if not client:
        raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )

    return response.text