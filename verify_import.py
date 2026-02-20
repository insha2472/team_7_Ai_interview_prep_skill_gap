try:
    from google import genai
    print("SUCCESS: google-genai is installed and genai is importable.")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"AN ERROR OCCURRED: {e}")
