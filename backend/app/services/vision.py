"""
Vision service — extract contact data from visiting card images using Gemini.
"""

import base64
import json
import logging
from typing import Optional

from google import genai
from google.genai import types

from app.config import get_settings

logger = logging.getLogger(__name__)


EXTRACTION_PROMPT = """You are an expert at reading visiting and business cards. 
Analyze the provided image of a visiting card and extract the following fields as structured JSON:

{
  "name": "Full name of the person",
  "phone": "Phone number (include country code if visible)",
  "email": "Email address (e.g. user@example.com)",
  "company": "Company or organization name (e.g. Google, Acme Inc)",
  "designation": "Job title or designation (e.g. Senior Software Engineer, Founder, Director)"
}

CRITICAL RULES:
- "email" MUST be the email address (containing '@').
- "company" MUST ONLY be the company, brand, or organization name. NEVER put an email address into the "company" field. If no separate company name is visible, use "".
- "name" MUST be the person's name, not the company name.
- If a field is not present or not readable, use an empty string "".
- For phone numbers, include all digits and any country code prefix.
- Do not infer or guess information that isn't on the card.
- Return ONLY valid JSON, no markdown formatting, no code blocks.
"""


def extract_contact_from_image(
    image_b64: str,
    mime_type: str = "image/jpeg",
) -> Optional[dict]:
    """
    Extract contact data from a visiting card image using Gemini Vision.

    Args:
        image_b64: Base64-encoded image string.
        mime_type: MIME type of the image (jpeg, png, webp).

    Returns:
        Dict with keys: name, phone, email, company, designation.
        Returns None if extraction fails.
    """
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        logger.warning("[STUB] Gemini API key not configured — returning mock data")
        return {
            "name": "John Doe",
            "phone": "+1-555-0123",
            "email": "john.doe@example.com",
            "company": "Acme Corporation",
            "designation": "Senior Vice President",
        }

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        image_bytes = base64.b64decode(image_b64)

        raw_text = None
        for model_name in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Content(
                            parts=[
                                types.Part.from_text(text=EXTRACTION_PROMPT),
                                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                            ]
                        )
                    ],
                )
                if response and response.text:
                    raw_text = response.text.strip()
                    break
            except Exception as m_err:
                logger.warning(f"Vision model {model_name} failed: {m_err}")
                continue

        if not raw_text:
            logger.error("All Gemini vision models failed or returned empty text")
            return None

        # Handle markdown-wrapped JSON
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])

        contact_data = json.loads(raw_text)

        # Validate expected keys
        expected_keys = {"name", "phone", "email", "company", "designation"}
        for key in expected_keys:
            if key not in contact_data:
                contact_data[key] = ""
            elif isinstance(contact_data[key], str):
                contact_data[key] = contact_data[key].strip()

        # ── Post-Processing & Field Disambiguation ─────────────────────────
        # Ensure email is not mistakenly populated into company
        comp_val = contact_data.get("company", "")
        email_val = contact_data.get("email", "")

        if "@" in comp_val:
            # If company contains '@', it is an email address
            if not email_val:
                contact_data["email"] = comp_val
            contact_data["company"] = ""

        # Clean up any mailto: prefix
        if contact_data.get("email", "").lower().startswith("mailto:"):
            contact_data["email"] = contact_data["email"][7:].strip()

        logger.info(f"Extracted contact: {contact_data.get('name', 'Unknown')}")
        return contact_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Vision extraction failed: {e}")
        return None
