import httpx

from config import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing in backend/.env")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"

response = httpx.get(url)

print(response.json())
