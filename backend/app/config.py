"""
Application configuration — all secrets loaded from environment variables.
"""

import json
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Central configuration for LeadSync Agent.
    All values are read from environment variables (or a .env file).
    """

    # ── MongoDB ──────────────────────────────────────────────────────
    MONGODB_URI: Optional[str] = None

    # ── Google Sheets ────────────────────────────────────────────────
    GOOGLE_SHEET_ID: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    # ── Gemini ───────────────────────────────────────────────────────
    GEMINI_API_KEY: Optional[str] = None

    # ── WhatsApp ─────────────────────────────────────────────────────
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_MANAGER_NUMBER: Optional[str] = None
    WHATSAPP_TEMPLATE_NAME: Optional[str] = None
    WHATSAPP_TEMPLATE_LANG: str = "en_US"

    # ── Cloudinary ───────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # ── App ──────────────────────────────────────────────────────────
    APP_NAME: str = "LeadSync Agent"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    GOOGLE_SHEETS_TAB_NAME: str = "Contacts"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../.env")
        env_file_encoding = "utf-8"

    @property
    def google_creds_dict(self) -> dict:
        """Parse the GOOGLE_SERVICE_ACCOUNT_JSON string into a dictionary."""
        if not self.GOOGLE_SERVICE_ACCOUNT_JSON:
            return {}
        try:
            return json.loads(self.GOOGLE_SERVICE_ACCOUNT_JSON)
        except json.JSONDecodeError:
            return {}


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
