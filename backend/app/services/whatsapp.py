"""
WhatsApp Business API service — send notifications to the manager.
Currently STUBBED: logs messages instead of sending real WhatsApp messages.
Will be wired to real Meta Cloud API once WhatsApp Business account is active.
"""

import logging
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_new_contact_notification(contact: dict) -> bool:
    """
    Notify the manager about a newly logged contact via WhatsApp.

    Args:
        contact: Dict with name, phone, email, company, designation.

    Returns:
        True if message was sent (or logged) successfully.
    """
    settings = get_settings()

    name = contact.get("name", "Unknown")
    company = contact.get("company", "N/A")
    designation = contact.get("designation", "N/A")
    phone = contact.get("phone", "N/A")
    email = contact.get("email", "N/A")

    message_text = (
        f"🆕 *New Contact Logged — LeadSync*\n\n"
        f"*Name:* {name}\n"
        f"*Company:* {company}\n"
        f"*Designation:* {designation}\n"
        f"*Phone:* {phone}\n"
        f"*Email:* {email}\n\n"
        f"_Logged via LeadSync Agent_"
    )

    # ── STUB MODE: Log instead of sending ────────────────────────────
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.info(
            f"[STUB] Would send WhatsApp notification to {settings.WHATSAPP_MANAGER_NUMBER}:\n"
            f"{message_text}"
        )
        return True

    # ── REAL MODE: Send via Meta Cloud API ───────────────────────────
    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.WHATSAPP_MANAGER_NUMBER,
        "type": "text",
        "text": {"body": message_text},
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"WhatsApp notification sent to {settings.WHATSAPP_MANAGER_NUMBER}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"WhatsApp API error: {e.response.status_code} — {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False
