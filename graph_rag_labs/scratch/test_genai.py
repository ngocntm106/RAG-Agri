import os
from dotenv import load_dotenv
from google import genai

env_path = r"c:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\buoi_17\.env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
client = genai.Client(api_key=api_key)

print("Testing gemini-3.6-flash...")
try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Xin chào, hãy phản hồi: OK"
    )
    print(f"SUCCESS: {response.text.strip()}")
except Exception as e:
    print(f"Error: {e}")
