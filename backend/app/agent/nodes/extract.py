"""
Node: extract_card_data — uses Gemini Vision to extract contact fields from a card image.
"""

import logging
from app.agent.state import AgentState
from app.services.vision import extract_contact_from_image

logger = logging.getLogger(__name__)


def extract_card_data(state: AgentState) -> dict:
    """
    Extract contact data from the uploaded visiting card image.
    Calls the Gemini Vision service.
    """
    image_data = state.get("image_data", "")
    mime_type = state.get("image_mime_type", "image/jpeg")

    if not image_data:
        logger.error("[extract] No image data in state")
        return {
            "error": "No image data provided",
            "messages": [{"role": "assistant", "content": "❌ No image data received. Please upload a visiting card image."}],
        }

    logger.info(f"[extract] Extracting contact from image for session {state['session_id']}")

    contact = extract_contact_from_image(image_data, mime_type)

    if contact is None:
        return {
            "error": "Failed to extract contact data from the image",
            "messages": [{"role": "assistant", "content": "❌ I couldn't read the visiting card. Please try uploading a clearer image."}],
        }

    logger.info(f"[extract] Extracted: {contact.get('name', 'Unknown')}")

    return {
        "extracted_contact": contact,
        "messages": [{
            "role": "assistant",
            "content": f"📇 Extracted contact from the card:\n\n"
                       f"**Name:** {contact.get('name', 'N/A')}\n"
                       f"**Phone:** {contact.get('phone', 'N/A')}\n"
                       f"**Email:** {contact.get('email', 'N/A')}\n"
                       f"**Company:** {contact.get('company', 'N/A')}\n"
                       f"**Designation:** {contact.get('designation', 'N/A')}",
            "metadata": {"type": "extraction", "contact": contact},
        }],
    }
