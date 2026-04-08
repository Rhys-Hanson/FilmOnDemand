import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("API Key not found")
    exit(1)

client = genai.Client(api_key=api_key)

try:
    models = client.models.list()
    for m in models:
        # Check for m.supported_methods or similar
        print(f"Name: {m.name}, Methods: {getattr(m, 'supported_methods', 'Unknown')}")
except Exception as e:
    print(f"Error: {e}")
