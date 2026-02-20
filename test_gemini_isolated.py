import os
from google import genai
from dotenv import load_dotenv

def test():
    with open("gemini_result.txt", "w") as f:
        f.write("Testing started...\n")
        try:
            load_dotenv()
            key = os.getenv("GEMINI_API_KEY")
            f.write(f"Key found: {bool(key)}\n")
            client = genai.Client(api_key=key)
            f.write("Client created. Sending prompt...\n")
            response = client.models.generate_content(model="gemini-2.0-flash", contents="hi")
            f.write(f"Response: {response.text}\n")
        except Exception as e:
            f.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    test()
