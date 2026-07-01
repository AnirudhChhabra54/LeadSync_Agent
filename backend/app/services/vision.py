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


EXTRACTION_PROMPT = """You are an expert at reading visiting/business cards. 
Analyze the provided image of a visiting card and extract the following fields as structured JSON:

{
  "name": "Full name of the person",
  "phone": "Phone number (include country code if visible)",
  "email": "Email address",
  "company": "Company/organization name",
  "designation": "Job title or designation"
}

Rules:
- Extract ONLY what is clearly visible on the card
- If a field is not present or not readable, use an empty string ""
- For phone numbers, include all digits and any country code prefix
- Do not infer or guess information that isn't on the card
- Return ONLY valid JSON, no markdown formatting, no code blocks
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

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_text(text=EXTRACTION_PROMPT),
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    ]
                )
            ],
        )

        # Parse the JSON response
        raw_text = response.text.strip()

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

        logger.info(f"Extracted contact: {contact_data.get('name', 'Unknown')}")
        return contact_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Vision extraction failed: {e}")
        return None
