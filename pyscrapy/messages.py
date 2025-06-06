import os
from dotenv import load_dotenv
load_dotenv()

geminikey=os.getenv("GOOGLE_API_KEY")

def get_gemini_key_value():
    if geminikey:
        return geminikey
    return None
    
