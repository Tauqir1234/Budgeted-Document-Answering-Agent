import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("1. Starting script...", flush=True)

# Explicitly load .env from the script's folder
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

print(f"2. API Key loaded: {bool(api_key)}", flush=True)

if not api_key:
    print("\n[ERROR] GEMINI_API_KEY is missing or empty inside .env!", flush=True)
    sys.exit(1)

try:
    from google import genai
    print("3. Google GenAI library imported.", flush=True)

    client = genai.Client(api_key=api_key)
    print("4. Client initialized. Requesting Gemini...", flush=True)

    # Updated to active model endpoint
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Say 'Hello World'"
    )

    print("\n--- RESPONSE FROM GEMINI ---", flush=True)
    print(response.text, flush=True)

except Exception as e:
    print(f"\nCRITICAL ERROR: {type(e).__name__}: {e}", flush=True)