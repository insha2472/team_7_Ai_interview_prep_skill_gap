from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    print(f"Genai dir: {dir(genai)}")
    if hasattr(genai, 'Client'):
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("Successfully created client.")
        
        # Try to create a dummy chat to see the type
        # We don't need a real API call if we just want to look at the module structure
        if hasattr(client, 'chats'):
            print(f"Client.chats dir: {dir(client.chats)}")
            
    if hasattr(genai, 'chats'):
        print(f"Genai.chats dir: {dir(genai.chats)}")
except Exception as e:
    print(f"Error: {e}")
