# check_models.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file")
else:
    print(f"🔑 Checking API Key: {api_key[:5]}... (hidden)")
    try:
        genai.configure(api_key=api_key)
        print("\n🔍 listing available embedding models...")
        
        found = False
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"✅ FOUND: {m.name}")
                found = True
        
        if not found:
            print("❌ No embedding models found. Check if 'Generative Language API' is enabled in Google Cloud Console.")
            
    except Exception as e:
        print(f"❌ Error connecting to Google: {e}")