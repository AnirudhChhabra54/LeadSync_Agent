"""
Node: write_to_sheet — append the confirmed contact to Google Sheets.
Also tracks pending contact in MongoDB for voice note linking.
"""

import logging
from datetime import datetime, timezone
from pymongo import MongoClient

from app.agent.state import AgentState
from app.config import get_settings
from app.services.sheets import append_contact_row

logger = logging.getLogger(__name__)


def write_to_sheet(state: AgentState) -> dict:
    """
    Write the confirmed, unique contact to Google Sheets.
    Sets the initial status to 'New — awaiting voice note'.
    Saves pending contact status to MongoDB.
    """
    contact = state.get("extracted_contact", {})
    enriched = state.get("enriched_website_linkedin", "")
    session_id = state.get("session_id", "")

    logger.info(f"[sheets] Writing contact to sheet: {contact.get('name', 'Unknown')}")

    row_index = append_contact_row(
        name=contact.get("name", ""),
        phone=contact.get("phone", ""),
        email=contact.get("email", ""),
        company=contact.get("company", ""),
        designation=contact.get("designation", ""),
        website_linkedin=enriched,
        session_id=session_id,
        status="New — awaiting voice note",
    )

    if row_index < 0:
        logger.error("[sheets] Failed to write to sheet")
        return {
            "error": "Failed to write contact to Google Sheets",
            "messages": [{
                "role": "assistant",
                "content": "⚠️ Contact confirmed but failed to save to Google Sheets. Please check credentials.",
            }],
        }

    logger.info(f"[sheets] Contact written at row {row_index}")

    # Track pending contact in MongoDB so voice note uploads link correctly
    try:
        settings = get_settings()
        if settings.MONGODB_URI:
            client = MongoClient(settings.MONGODB_URI)
            db = client.leadsync
            db.pending_contacts.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "session_id": session_id,
                        "contact_name": contact.get("name", ""),
                        "sheet_row": row_index,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )
            db.sessions.update_one(
                {"_id": session_id},
                {"$set": {"has_pending_contact": True}},
            )
            logger.info(f"[sheets] Pending contact '{contact.get('name')}' saved to MongoDB for session {session_id}")
    except Exception as e:
        logger.warning(f"[sheets] Could not update pending contact in MongoDB: {e}")

    return {
        "sheet_row_index": row_index,
        "pending_contact_name": contact.get("name", ""),
        "messages": [{
            "role": "assistant",
            "content": f"📝 Contact **{contact.get('name', '')}** saved to Google Sheets (row {row_index})!\n\n"
                       f"You can now attach a voice note to this contact by uploading an audio file.",
            "metadata": {"type": "sheet_write", "row_index": row_index},
        }],
    }
