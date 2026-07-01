"""
Agent state schema — the TypedDict that flows through every LangGraph node.
"""

from typing import Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Central state object for the LeadSync LangGraph agent.
    Every node reads from and writes to this state.
    """

    # ── Session ──────────────────────────────────────────────────────
    session_id: str

    # ── Input Classification ─────────────────────────────────────────
    input_type: str  # "image" | "audio" | "text"
    text_message: Optional[str]
    image_data: Optional[str]  # base64-encoded image
    image_mime_type: Optional[str]
    audio_data: Optional[bytes]
    audio_filename: Optional[str]
    audio_mime_type: Optional[str]

    # ── Extraction ───────────────────────────────────────────────────
    extracted_contact: Optional[dict]
    # Keys: name, phone, email, company, designation

    # ── Enrichment ───────────────────────────────────────────────────
    enriched_website_linkedin: Optional[str]

    # ── Confirmation (Human-in-the-Loop) ─────────────────────────────
    confirmation_status: Optional[str]  # "pending" | "approved" | "rejected"
    user_edits: Optional[dict]  # Edits made during confirmation

    # ── Deduplication ────────────────────────────────────────────────
    is_duplicate: bool
    duplicate_info: Optional[dict]  # Existing row data if duplicate found

    # ── Sheet Write ──────────────────────────────────────────────────
    sheet_row_index: Optional[int]  # 1-based row index of written row

    # ── WhatsApp ─────────────────────────────────────────────────────
    whatsapp_sent: bool

    # ── Voice Note ───────────────────────────────────────────────────
    audio_url: Optional[str]  # Cloudinary URL
    voice_summary: Optional[str]
    voice_transcription: Optional[str]

    # ── Chat Messages ────────────────────────────────────────────────
    messages: Annotated[list[dict], add_messages]
    # Each: {"role": "user"|"assistant"|"system", "content": "..."}

    # ── Pending Contact Tracking ─────────────────────────────────────
    pending_contact_name: Optional[str]
    # Name of the contact awaiting a voice note in this session

    # ── Flow Control ─────────────────────────────────────────────────
    awaiting_confirmation: bool
    error: Optional[str]
