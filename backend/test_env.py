import os
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
print("Loading from:", env_path)
load_dotenv(env_path)
print("Keys loaded:", list(os.environ.keys())[-5:])
print("GOOGLE_SHEET_ID:", os.getenv("GOOGLE_SHEET_ID"))
print("GOOGLE_SERVICE_ACCOUNT_JSON length:", len(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")))
import json
try:
    j = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
    print("Parsed JSON type:", j.get("type"))
except Exception as e:
    print("JSON Error:", e)

