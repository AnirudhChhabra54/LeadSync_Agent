"""
Pydantic request/response models for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────

class InputType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatStatus(str, Enum):
    COMPLETE = "complete"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    PROCESSING = "processing"
    ERROR = "error"


# ── Contact ──────────────────────────────────────────────────────────

class ExtractedContact(BaseModel):
    """Structured contact data extracted from a visiting card."""
    name: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    designation: str = ""
    website_linkedin: str = ""


# ── Chat Messages ────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """A single message in a chat session."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict[str, Any]] = None


# ── Request Models ───────────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    """Request body for sending a text message or confirmation."""
    session_id: str = Field(..., description="Chat session identifier")
    message: str = Field(default="", description="User text message")
    action: Optional[str] = Field(
        default=None,
        description="Action type: 'confirm' or 'reject' for confirmation flow"
    )
    edits: Optional[dict[str, str]] = Field(
        default=None,
        description="Optional field edits when confirming extracted data"
    )


class ImageUploadRequest(BaseModel):
    """Metadata for image upload (file sent as form data)."""
    session_id: str = Field(..., description="Chat session identifier")


class AudioUploadRequest(BaseModel):
    """Metadata for audio upload (file sent as form data)."""
    session_id: str = Field(..., description="Chat session identifier")


# ── Response Models ──────────────────────────────────────────────────

class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    session_id: str
    status: ChatStatus
    messages: list[ChatMessage] = []
    extracted_data: Optional[ExtractedContact] = None
    error: Optional[str] = None


class SessionInfo(BaseModel):
    """Summary info for a chat session."""
    session_id: str
    title: str = "New Session"
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    has_pending_contact: bool = False


class SessionListResponse(BaseModel):
    """Response for listing all sessions."""
    sessions: list[SessionInfo] = []


class SessionCreateResponse(BaseModel):
    """Response when creating a new session."""
    session_id: str
    title: str
    created_at: datetime
