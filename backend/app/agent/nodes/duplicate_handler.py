"""
Node: handle_duplicate — gracefully inform user when a duplicate contact is found.
"""

import logging
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def handle_duplicate(state: AgentState) -> dict:
    """
    Handle the case where a duplicate contact was found in Google Sheets.
    Inform the user with details of the existing entry.
    """
    dup = state.get("duplicate_info", {})
    contact = state.get("extracted_contact", {})

    existing_name = dup.get("Name", contact.get("name", "Unknown"))
    existing_date = dup.get("Timestamp", "unknown date")
    existing_company = dup.get("Company", "")

    logger.info(f"[handle_dup] Duplicate contact: {existing_name} (logged {existing_date})")

    msg = (
        f"⚠️ **Duplicate contact detected!**\n\n"
        f"**{existing_name}**"
    )
    if existing_company:
        msg += f" from **{existing_company}**"
    msg += (
        f" was already logged on **{existing_date}**.\n\n"
        f"No new row was created. If you'd like to update this contact, "
        f"please edit the record directly in Google Sheets.\n\n"
        f"You can upload another visiting card or attach a voice note."
    )

    return {
        "messages": [{
            "role": "assistant",
            "content": msg,
            "metadata": {"type": "duplicate", "existing_record": dup},
        }],
    }
