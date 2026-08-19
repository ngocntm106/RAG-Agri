import os
import sys
from dotenv import load_dotenv
from google import genai

sys.stdout.reconfigure(encoding='utf-8')

# Load env
env_path = os.path.join("ner_kb", ".env")
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("Testing gemini-3.6-flash...")
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents='Hãy trả lời ngắn gọn: OK',
    )
    print("gemini-3.6-flash success:", response.text)
except Exception as e:
    print("gemini-3.6-flash error:", e)
