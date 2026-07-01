"""
Node: send_whatsapp — notify the manager about a new contact via WhatsApp.
Currently stubbed (logs instead of sending) until WhatsApp Business account is active.
"""

import logging
import asyncio
from app.agent.state import AgentState
from app.services.whatsapp import send_new_contact_notification

logger = logging.getLogger(__name__)


def send_whatsapp(state: AgentState) -> dict:
    """
    Send a WhatsApp notification to the manager about the newly logged contact.
    Only fires for unique contacts (never for duplicates).
    """
    contact = state.get("extracted_contact", {})
    name = contact.get("name", "Unknown")

    logger.info(f"[whatsapp] Sending notification for: {name}")

    # Run async function in sync context (LangGraph nodes are sync)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                sent = pool.submit(
                    asyncio.run, send_new_contact_notification(contact)
                ).result()
        else:
            sent = asyncio.run(send_new_contact_notification(contact))
    except Exception as e:
        logger.error(f"[whatsapp] Failed to send notification: {e}")
        sent = False

    if sent:
        logger.info(f"[whatsapp] Notification sent for: {name}")
        return {
            "whatsapp_sent": True,
            "messages": [{
                "role": "assistant",
                "content": f"📱 WhatsApp notification sent to the manager about **{name}**.",
            }],
        }
    else:
        logger.warning(f"[whatsapp] Notification failed for: {name}")
        return {
            "whatsapp_sent": False,
            "messages": [{
                "role": "assistant",
                "content": f"⚠️ WhatsApp notification could not be sent (will retry later).",
            }],
        }
