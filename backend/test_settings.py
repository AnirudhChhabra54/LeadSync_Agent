from app.config import get_settings
settings = get_settings()
print("Google Sheet ID:", settings.GOOGLE_SHEET_ID)
print("Google Creds length:", len(settings.GOOGLE_SERVICE_ACCOUNT_JSON) if settings.GOOGLE_SERVICE_ACCOUNT_JSON else None)
print("Gemini Key length:", len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None)
