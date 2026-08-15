"""
WhatsApp Business API service — send notifications to the manager via Meta Cloud API.
Supports both approved Message Templates and Freeform Text messages.
"""

import logging
from typing import Optional
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_whatsapp_template(
    to_number: str,
    template_name: str,
    language_code: str = "en_US",
    body_parameters: Optional[list[str]] = None,
) -> bool:
    """
    Send an approved WhatsApp Business message template.
    Required by Meta when initiating conversations outside the 24-hour customer window.
    """
    settings = get_settings()

    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.info(f"[STUB] Would send WhatsApp template '{template_name}' to {to_number}")
        return True

    # Strip any '+' prefix for Meta API recipient
    formatted_to = to_number.replace("+", "").replace(" ", "").replace("-", "").strip()

    template_payload = {
        "name": template_name,
        "language": {"code": language_code},
    }

    if body_parameters:
        template_payload["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in body_parameters],
            }
        ]

    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": formatted_to,
        "type": "template",
        "template": template_payload,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"✅ WhatsApp template '{template_name}' sent to {formatted_to}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ WhatsApp Template API error: {e.response.status_code} — {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"❌ WhatsApp Template send failed: {e}")
        return False


async def send_new_contact_notification(contact: dict) -> bool:
    """
    Notify the manager about a newly logged contact via WhatsApp.
    Attempts template message if configured; otherwise sends structured text with fallback.
    """
    settings = get_settings()

    name = contact.get("name", "Unknown")
    company = contact.get("company", "N/A")
    designation = contact.get("designation", "N/A")
    phone = contact.get("phone", "N/A")
    email = contact.get("email", "N/A")

    to_number = settings.WHATSAPP_MANAGER_NUMBER or ""
    formatted_to = to_number.replace("+", "").replace(" ", "").replace("-", "").strip()

    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.info(
            f"[STUB] Would send WhatsApp notification to {settings.WHATSAPP_MANAGER_NUMBER}:\n"
            f"Name: {name} | Company: {company} | Phone: {phone}"
        )
        return True

    # If an approved template is specified in configuration, use it
    if settings.WHATSAPP_TEMPLATE_NAME:
        from datetime import datetime, timezone
        date_str = datetime.now(timezone.utc).strftime("%b %d, %Y")

        if settings.WHATSAPP_TEMPLATE_NAME == "hello_world":
            params = None
        elif settings.WHATSAPP_TEMPLATE_NAME == "jaspers_market_order_confirmation_v1":
            # jaspers template expects 3 parameters: {{1}} customer name, {{2}} order/reference, {{3}} date
            params = [name, f"{company} ({designation})", date_str]
        else:
            params = [name, company, designation, phone, email]

        return await send_whatsapp_template(
            to_number=to_number,
            template_name=settings.WHATSAPP_TEMPLATE_NAME,
            language_code=settings.WHATSAPP_TEMPLATE_LANG,
            body_parameters=params,
        )

    # Freeform text message
    message_text = (
        f"🆕 *New Contact Logged — LeadSync*\n\n"
        f"*Name:* {name}\n"
        f"*Company:* {company}\n"
        f"*Designation:* {designation}\n"
        f"*Phone:* {phone}\n"
        f"*Email:* {email}\n\n"
        f"_Logged via LeadSync Agent_"
    )

    url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": formatted_to,
        "type": "text",
        "text": {"body": message_text},
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"✅ WhatsApp notification sent to {formatted_to}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"WhatsApp API error: {e.response.status_code} — {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False

