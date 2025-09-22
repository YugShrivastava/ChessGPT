import os
from google import genai
from dotenv import load_dotenv
import json

with open("./blackBox/prompt.txt" ,'r') as file:
    prompt_text = file.read() 
    print(prompt_text)

load_dotenv()
context = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}
import json
final_prompt = f"Here is some data:\n{context}"

api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

if not client:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents=final_prompt
)

print(response.text) 