"""
Chat endpoints — the primary interface between the frontend and the LangGraph agent.

POST /chat/message        — Send a text message or confirmation action
POST /chat/upload-image   — Upload a visiting card image
POST /chat/upload-audio   — Upload a voice note
"""

import base64
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models import (
    ChatMessageRequest,
    ChatResponse,
    ChatStatus,
    ChatMessage,
    MessageRole,
    ExtractedContact,
)
from app.agent.graph import get_agent_graph, run_agent, resume_agent
from app.services.mongodb import MongoSessionStore

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a text message or a confirmation/rejection action to the agent.

    - For regular text: just provide `message`
    - For confirmation: set `action='confirm'` and optionally provide `edits`
    - For rejection: set `action='reject'`
    """
    session_store = MongoSessionStore()

    # Handle confirmation/rejection (resume from interrupt)
    if request.action in ("confirm", "reject"):
        approved = request.action == "confirm"
        resume_value = {
            "approved": approved,
            "edits": request.edits or {},
        }
        result = await resume_agent(
            session_id=request.session_id,
            resume_value=resume_value,
        )
        return _build_response(request.session_id, result)

    # Handle regular text message
    if not request.message.strip():
        return ChatResponse(
            session_id=request.session_id,
            status=ChatStatus.COMPLETE,
            messages=[
                ChatMessage(
                    role=MessageRole.AGENT,
                    content="Please send a message, upload a visiting card image, or attach a voice note.",
                )
            ],
        )

    result = await run_agent(
        session_id=request.session_id,
        input_type="text",
        text_message=request.message,
    )
    return _build_response(request.session_id, result)


@router.post("/upload-image", response_model=ChatResponse)
async def upload_image(
    session_id: str = Form(...),
    file: UploadFile = File(..., description="Visiting card image (JPEG, PNG, WebP)"),
):
    """
    Upload a visiting card image for contact extraction.

    The image is sent to the LangGraph agent which will:
    1. Extract contact data via Gemini Vision
    2. Attempt company enrichment
    3. Pause for user confirmation (human-in-the-loop interrupt)
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/heic"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {file.content_type}. Allowed: {', '.join(allowed_types)}",
        )

    # Read and encode image
    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    result = await run_agent(
        session_id=session_id,
        input_type="image",
        image_data=image_b64,
        image_mime_type=file.content_type,
    )
    return _build_response(session_id, result)


@router.post("/upload-audio", response_model=ChatResponse)
async def upload_audio(
    session_id: str = Form(...),
    file: UploadFile = File(..., description="Voice note audio file"),
):
    """
    Upload a voice note to attach to the most recently processed contact in this session.

    The audio will be:
    1. Uploaded to Cloudinary for hosting
    2. Transcribed and summarized via Gemini
    3. Linked to the contact's Google Sheets row
    """
    allowed_types = {
        "audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg",
        "audio/webm", "audio/m4a", "audio/x-m4a", "audio/mp4",
    }
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type: {file.content_type}.",
        )

    audio_bytes = await file.read()

    result = await run_agent(
        session_id=session_id,
        input_type="audio",
        audio_data=audio_bytes,
        audio_filename=file.filename or "voice_note.mp3",
        audio_mime_type=file.content_type or "audio/mpeg",
    )
    return _build_response(session_id, result)


def _build_response(session_id: str, agent_result: dict) -> ChatResponse:
    """Convert agent graph output into a ChatResponse."""
    status = ChatStatus.COMPLETE

    # Check if the agent is waiting for confirmation
    if agent_result.get("awaiting_confirmation"):
        status = ChatStatus.AWAITING_CONFIRMATION

    # Build message list from agent output
    messages = []
    for msg in agent_result.get("messages", []):
        if isinstance(msg, dict):
            role_str = msg.get("role", "assistant")
            content = msg.get("content", "")
            metadata = msg.get("metadata")
        else:
            # Handle LangChain BaseMessage objects
            role_str = msg.type if hasattr(msg, "type") else "assistant"
            # Map LangChain types to our MessageRole Enum
            if role_str == "ai":
                role_str = "assistant"
            elif role_str == "human":
                role_str = "user"
            
            content = msg.content if hasattr(msg, "content") else str(msg)
            metadata = msg.additional_kwargs.get("metadata") if hasattr(msg, "additional_kwargs") else None

        try:
            role_enum = MessageRole(role_str)
        except ValueError:
            role_enum = MessageRole.ASSISTANT

        messages.append(
            ChatMessage(
                role=role_enum,
                content=content,
                metadata=metadata,
            )
        )

    # Extract contact data if available
    extracted = None
    if agent_result.get("extracted_contact"):
        extracted = ExtractedContact(**agent_result["extracted_contact"])

    return ChatResponse(
        session_id=session_id,
        status=status,
        messages=messages,
        extracted_data=extracted,
        error=agent_result.get("error"),
    )
