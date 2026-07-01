"""
Node: confirm_with_user — Human-in-the-loop interrupt for contact confirmation.
Uses LangGraph's interrupt() to pause the graph and wait for user approval.
"""

import logging
from langgraph.types import interrupt
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def confirm_with_user(state: AgentState) -> dict:
    """
    Pause the graph and ask the user to confirm the extracted contact data
    before writing to Google Sheets.

    Uses LangGraph interrupt() — the graph will be suspended here.
    When resumed via Command(resume={...}), the interrupt() call returns
    the resume value, and this node re-executes with that value.
    """
    contact = state.get("extracted_contact") or {}
    enriched = state.get("enriched_website_linkedin", "")

    if not contact:
        logger.info("[confirm] No extracted contact data. Aborting confirmation flow.")
        return {
            "confirmation_status": "rejected",
            "awaiting_confirmation": False
        }

    # Build the confirmation payload sent to the client
    confirmation_payload = {
        "action": "confirm_contact",
        "extracted_data": {
            **contact,
            "website_linkedin": enriched,
        },
        "message": "Please review the extracted contact details. Confirm to save, or reject to cancel.",
    }

    logger.info(f"[confirm] Requesting user confirmation for: {contact.get('name', 'Unknown')}")

    # ── INTERRUPT: Graph pauses here ─────────────────────────────────
    # On first run: interrupt() raises and the graph suspends.
    # On resume: interrupt() returns the value from Command(resume=...).
    user_response = interrupt(confirmation_payload)

    # ── Graph has been resumed with user's decision ──────────────────
    approved = user_response.get("approved", False)
    edits = user_response.get("edits", {})

    if approved:
        # Apply any user edits to the contact
        updated_contact = {**contact}
        for key, value in edits.items():
            if key in updated_contact and value:
                updated_contact[key] = value

        # Update enriched info if edited
        updated_enriched = edits.get("website_linkedin", enriched)

        logger.info(f"[confirm] User APPROVED contact: {updated_contact.get('name')}")
        return {
            "confirmation_status": "approved",
            "extracted_contact": updated_contact,
            "enriched_website_linkedin": updated_enriched,
            "user_edits": edits,
            "awaiting_confirmation": False,
            "messages": [{
                "role": "assistant",
                "content": "✅ Contact confirmed! Checking for duplicates...",
            }],
        }
    else:
        logger.info(f"[confirm] User REJECTED contact: {contact.get('name')}")
        return {
            "confirmation_status": "rejected",
            "awaiting_confirmation": False,
            "messages": [{
                "role": "assistant",
                "content": "❌ Contact submission cancelled. Upload another card or send a message.",
            }],
        }
