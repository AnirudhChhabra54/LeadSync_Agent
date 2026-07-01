"""
Node: check_duplicate — compare extracted contact against existing Google Sheets rows.
"""

import logging
from app.agent.state import AgentState
from app.services.sheets import find_duplicate

logger = logging.getLogger(__name__)


def check_duplicate(state: AgentState) -> dict:
    """
    Check if the extracted contact already exists in Google Sheets.
    Compares normalized phone and email against all existing rows.
    """
    contact = state.get("extracted_contact", {})
    phone = contact.get("phone", "")
    email = contact.get("email", "")

    logger.info(f"[dedup] Checking for duplicate: phone={phone}, email={email}")

    existing = find_duplicate(phone, email)

    if existing:
        timestamp = existing.get("Timestamp", "unknown date")
        name = existing.get("Name", "Unknown")
        logger.info(f"[dedup] DUPLICATE found: {name} (logged {timestamp})")
        return {
            "is_duplicate": True,
            "duplicate_info": existing,
        }
    else:
        logger.info("[dedup] No duplicate found — contact is unique")
        return {
            "is_duplicate": False,
            "duplicate_info": None,
        }
