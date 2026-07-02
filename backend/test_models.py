import asyncio
from google import genai
from app.config import get_settings

def test():
    settings = get_settings()
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    print("Listing models...")
    try:
        models = client.models.list()
        for m in models:
            print(m.name)
    except Exception as e:
        import traceback
        traceback.print_exc()

test()
