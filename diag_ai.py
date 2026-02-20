import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Try with 1.5-flash which is widely available
MODEL_ID = "gemini-1.5-flash"

print(f"Testing Gemini with model: {MODEL_ID}")
try:
    response = client.models.generate_content(
        model=MODEL_ID,
        contents="Generate one MCQ question about Python. Return as JSON array.",
    )
    print("Response text:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
