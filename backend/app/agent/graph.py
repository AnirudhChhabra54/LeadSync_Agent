"""
LangGraph Agent Graph — the brain of LeadSync Agent.

This single StateGraph orchestrates the entire flow:
  receive_input → classify_input → (image/audio/text routing)
    → extract_card_data → enrich_company → confirm_with_user (INTERRUPT)
    → check_duplicate → [write_to_sheet + send_whatsapp] OR [handle_duplicate]
    → process_voice_note → update sheet row

Conditional edges handle branching for:
  - Input type (image vs audio vs text)
  - Confirmation (approved vs rejected)
  - Deduplication (unique vs duplicate)
"""

import logging
from typing import Optional

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command, interrupt
from pymongo import MongoClient

from app.agent.state import AgentState
from app.agent.nodes.classify import classify_input
from app.agent.nodes.extract import extract_card_data
from app.agent.nodes.enrich import enrich_company
from app.agent.nodes.confirm import confirm_with_user
from app.agent.nodes.dedup import check_duplicate
from app.agent.nodes.sheets import write_to_sheet
from app.agent.nodes.whatsapp import send_whatsapp
from app.agent.nodes.duplicate_handler import handle_duplicate
from app.agent.nodes.voice import process_voice_note
from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Module-level graph singleton ─────────────────────────────────────
_compiled_graph = None
_checkpointer = None


def _handle_text_message(state: AgentState) -> dict:
    """Handle a plain text message (no image or audio)."""
    text = state.get("text_message", "")
    pending = state.get("pending_contact_name", "")

    if pending:
        response = (
            f"I'm currently tracking contact **{pending}** in this session.\n\n"
            f"You can:\n"
            f"• Upload a **voice note** to attach to this contact\n"
            f"• Upload a **new visiting card** image\n"
            f"• Type a message"
        )
    else:
        response = (
            f"👋 Hello! I'm the LeadSync Agent. I can help you:\n\n"
            f"• **Upload a visiting card image** — I'll extract the contact info\n"
            f"• **Upload a voice note** — I'll attach it to the last processed contact\n\n"
            f"Go ahead and upload a visiting card to get started!"
        )

    return {
        "messages": [{
            "role": "assistant",
            "content": response,
        }],
    }


# ── Routing functions for conditional edges ──────────────────────────

def route_by_input_type(state: AgentState) -> str:
    """Route to the appropriate handler based on input type."""
    input_type = state.get("input_type", "text")
    if input_type == "image":
        return "extract_card_data"
    elif input_type == "audio":
        return "process_voice_note"
    else:
        return "handle_text"


def route_after_dedup(state: AgentState) -> str:
    """Route based on whether a duplicate was found during card processing."""
    if state.get("is_duplicate"):
        return "handle_duplicate"
    else:
        return "enrich_company"


def route_after_confirmation(state: AgentState) -> str:
    """Route based on user's confirmation decision."""
    status = state.get("confirmation_status", "")
    if status == "approved":
        return "write_to_sheet"
    else:
        return END


def build_graph() -> StateGraph:
    """
    Construct the LeadSync Agent LangGraph.

    Node flow:
    ┌─────────────────┐
    │  classify_input  │
    └────────┬────────┘
             │
      ┌──────┼──────────────┐
      │      │              │
    image   audio          text
      │      │              │
      ▼      ▼              ▼
    extract  process_voice  handle_text
      │      │              │
      ▼      │              ▼
    dedup    │             END
      │      │
    ┌─┴─┐    │
    │   │    ▼
  dup unique END
    │   │
    │   ▼
    │ enrich
    │   │
    │   ▼
    │ confirm (INTERRUPT)
    │   │
    │ ┌─┴─┐
    │ │   │
    │app  rej
    │ │   │
    │ ▼   ▼
    │write END
    │ │
    │ ▼
    │whatsapp
    │ │
    ▼ ▼
    END
    """
    builder = StateGraph(AgentState)

    # ── Add nodes ────────────────────────────────────────────────────
    builder.add_node("classify_input", classify_input)
    builder.add_node("extract_card_data", extract_card_data)
    builder.add_node("check_duplicate", check_duplicate)
    builder.add_node("enrich_company", enrich_company)
    builder.add_node("confirm_with_user", confirm_with_user)
    builder.add_node("write_to_sheet", write_to_sheet)
    builder.add_node("send_whatsapp", send_whatsapp)
    builder.add_node("handle_duplicate", handle_duplicate)
    builder.add_node("process_voice_note", process_voice_note)
    builder.add_node("handle_text", _handle_text_message)

    # ── Add edges ────────────────────────────────────────────────────

    # START → classify_input
    builder.add_edge(START, "classify_input")

    # classify_input → (conditional) image/audio/text handler
    builder.add_conditional_edges(
        "classify_input",
        route_by_input_type,
        {
            "extract_card_data": "extract_card_data",
            "process_voice_note": "process_voice_note",
            "handle_text": "handle_text",
        },
    )

    # Image path: extract → dedup check
    builder.add_edge("extract_card_data", "check_duplicate")

    # After dedup: duplicate → handle_duplicate (END), unique → enrich → confirm (INTERRUPT)
    builder.add_conditional_edges(
        "check_duplicate",
        route_after_dedup,
        {
            "handle_duplicate": "handle_duplicate",
            "enrich_company": "enrich_company",
        },
    )

    builder.add_edge("enrich_company", "confirm_with_user")

    # After confirmation: approved → write_to_sheet, rejected → END
    builder.add_conditional_edges(
        "confirm_with_user",
        route_after_confirmation,
        {
            "write_to_sheet": "write_to_sheet",
            END: END,
        },
    )

    # After write: send WhatsApp notification
    builder.add_edge("write_to_sheet", "send_whatsapp")

    # Terminal edges
    builder.add_edge("send_whatsapp", END)
    builder.add_edge("handle_duplicate", END)
    builder.add_edge("process_voice_note", END)
    builder.add_edge("handle_text", END)

    return builder


def get_checkpointer():
    """Get or create the MongoDB checkpointer for graph state persistence."""
    global _checkpointer
    if _checkpointer is None:
        settings = get_settings()
        client = MongoClient(settings.MONGODB_URI)
        _checkpointer = MongoDBSaver(client, db_name="leadsync_checkpoints")
        logger.info("MongoDB checkpointer initialized")
    return _checkpointer


def get_agent_graph():
    """Get or create the compiled agent graph singleton."""
    global _compiled_graph
    if _compiled_graph is None:
        builder = build_graph()
        checkpointer = get_checkpointer()
        _compiled_graph = builder.compile(checkpointer=checkpointer)
        logger.info("LangGraph agent compiled successfully")
    return _compiled_graph


async def run_agent(
    session_id: str,
    input_type: str = "text",
    text_message: str = "",
    image_data: str = "",
    image_mime_type: str = "image/jpeg",
    audio_data: bytes = b"",
    audio_filename: str = "",
    audio_mime_type: str = "audio/mpeg",
) -> dict:
    """
    Run the agent graph with the given input.

    Returns a dict with:
    - messages: list of message dicts
    - awaiting_confirmation: bool (if graph is interrupted)
    - extracted_contact: dict (if available)
    - error: str (if any)
    """
    graph = get_agent_graph()
    config = {"configurable": {"thread_id": session_id}}

    # Check if there's a pending contact from a previous run in this session
    pending_name = ""
    existing_msg_count = 0
    try:
        existing_state = graph.get_state(config)
        if existing_state and existing_state.values:
            pending_name = existing_state.values.get("pending_contact_name", "")
            existing_msg_count = len(existing_state.values.get("messages", []))
    except Exception:
        pass

    initial_state = {
        "session_id": session_id,
        "input_type": input_type,
        "text_message": text_message,
        "image_data": image_data if image_data else None,
        "image_mime_type": image_mime_type,
        "audio_data": audio_data if audio_data else None,
        "audio_filename": audio_filename,
        "audio_mime_type": audio_mime_type,
        "extracted_contact": None,
        "enriched_website_linkedin": None,
        "confirmation_status": None,
        "user_edits": None,
        "is_duplicate": False,
        "duplicate_info": None,
        "sheet_row_index": None,
        "whatsapp_sent": False,
        "audio_url": None,
        "voice_summary": None,
        "voice_transcription": None,
        "messages": [],
        "pending_contact_name": pending_name,
        "awaiting_confirmation": False,
        "error": None,
    }

    try:
        # Run the graph — it may interrupt at confirm_with_user
        result = graph.invoke(initial_state, config=config)

        # Check if we hit an interrupt
        state_snapshot = graph.get_state(config)
        is_interrupted = bool(state_snapshot.tasks and any(
            hasattr(t, 'interrupts') and t.interrupts for t in state_snapshot.tasks
        ))

        if is_interrupted:
            # Graph is paused at confirm_with_user
            # Extract the interrupt payload
            interrupt_data = None
            for task in state_snapshot.tasks:
                if hasattr(task, 'interrupts') and task.interrupts:
                    interrupt_data = task.interrupts[0].value
                    break

            all_msgs = result.get("messages", []) if isinstance(result, dict) else []
            return {
                "messages": all_msgs[existing_msg_count:],
                "awaiting_confirmation": True,
                "extracted_contact": interrupt_data.get("extracted_data") if interrupt_data else None,
                "error": None,
            }

        all_msgs = result.get("messages", []) if isinstance(result, dict) else []
        return {
            "messages": all_msgs[existing_msg_count:],
            "awaiting_confirmation": False,
            "extracted_contact": result.get("extracted_contact") if isinstance(result, dict) else None,
            "error": result.get("error") if isinstance(result, dict) else None,
        }

    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        return {
            "messages": [{"role": "assistant", "content": f"❌ An error occurred: {str(e)}"}],
            "awaiting_confirmation": False,
            "extracted_contact": None,
            "error": str(e),
        }


async def resume_agent(session_id: str, resume_value: dict) -> dict:
    """
    Resume the agent graph from a human-in-the-loop interrupt.

    Args:
        session_id: The session/thread ID.
        resume_value: Dict with 'approved' (bool) and 'edits' (dict).
    """
    graph = get_agent_graph()
    config = {"configurable": {"thread_id": session_id}}

    try:
        existing_msg_count = 0
        existing_state = graph.get_state(config)
        if existing_state and existing_state.values:
            existing_msg_count = len(existing_state.values.get("messages", []))

        result = graph.invoke(Command(resume=resume_value), config=config)

        all_msgs = result.get("messages", []) if isinstance(result, dict) else []
        return {
            "messages": all_msgs[existing_msg_count:],
            "awaiting_confirmation": False,
            "extracted_contact": result.get("extracted_contact") if isinstance(result, dict) else None,
            "error": result.get("error") if isinstance(result, dict) else None,
        }

    except Exception as e:
        logger.error(f"Agent resume failed: {e}", exc_info=True)
        return {
            "messages": [{"role": "assistant", "content": f"❌ Failed to resume: {str(e)}"}],
            "awaiting_confirmation": False,
            "extracted_contact": None,
            "error": str(e),
        }
