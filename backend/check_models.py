import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {key[:6]}... (length: {len(key) if key else 0})")

client = genai.Client()

models = list(client.models.list())
print(f"Total models fetched: {len(models)}")

for m in models:
    print(m.name)