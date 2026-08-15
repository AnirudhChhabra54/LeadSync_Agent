"""
Session management endpoints.

GET    /sessions          — List all sessions
POST   /sessions          — Create a new session
GET    /sessions/{id}     — Get a specific session's details
DELETE /sessions/{id}     — Delete a session
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from app.models import (
    SessionInfo,
    SessionListResponse,
    SessionCreateResponse,
    SessionMessagesResponse,
    ChatMessage,
    MessageRole,
    ChatStatus,
    ExtractedContact,
)
from app.services.mongodb import MongoSessionStore
from app.agent.graph import get_agent_graph

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=SessionListResponse)
async def list_sessions():
    """List all chat sessions, sorted by most recently updated."""
    store = MongoSessionStore()
    sessions = await store.list_sessions()
    return SessionListResponse(sessions=sessions)


@router.post("", response_model=SessionCreateResponse)
async def create_session():
    """Create a new chat session."""
    store = MongoSessionStore()
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    session_info = SessionInfo(
        session_id=session_id,
        title="New Session",
        created_at=now,
        updated_at=now,
        message_count=0,
        has_pending_contact=False,
    )
    await store.create_session(session_info)

    return SessionCreateResponse(
        session_id=session_id,
        title=session_info.title,
        created_at=now,
    )


@router.get("/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Get details for a specific session."""
    store = MongoSessionStore()
    session = await store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/messages", response_model=SessionMessagesResponse)
async def get_session_messages(session_id: str):
    """
    Get all messages and active status (including interrupted/awaiting confirmation state)
    for a specific session.
    """
    store = MongoSessionStore()
    session = await store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = []
    status = ChatStatus.COMPLETE
    extracted_contact = None

    # Check LangGraph state checkpoint
    try:
        graph = get_agent_graph()
        config = {"configurable": {"thread_id": session_id}}
        state = graph.get_state(config)

        if state and state.values:
            # Extract messages
            raw_msgs = state.values.get("messages", [])
            for msg in raw_msgs:
                if isinstance(msg, dict):
                    role_str = msg.get("role", "assistant")
                    content = msg.get("content", "")
                    meta = msg.get("metadata")
                else:
                    role_str = getattr(msg, "type", "assistant")
                    if role_str == "ai":
                        role_str = "assistant"
                    elif role_str == "human":
                        role_str = "user"
                    content = getattr(msg, "content", str(msg))
                    meta = getattr(msg, "additional_kwargs", {}).get("metadata")

                try:
                    role_enum = MessageRole(role_str)
                except ValueError:
                    role_enum = MessageRole.ASSISTANT

                messages.append(
                    ChatMessage(
                        role=role_enum,
                        content=content,
                        metadata=meta,
                    )
                )

            # Check if interrupted
            is_interrupted = bool(state.tasks and any(
                hasattr(t, 'interrupts') and t.interrupts for t in state.tasks
            ))
            if is_interrupted:
                status = ChatStatus.AWAITING_CONFIRMATION
                for task in state.tasks:
                    if hasattr(task, 'interrupts') and task.interrupts:
                        int_val = task.interrupts[0].value
                        if isinstance(int_val, dict) and int_val.get("extracted_data"):
                            extracted_contact = ExtractedContact(**int_val["extracted_data"])
                        break

            if not extracted_contact and state.values.get("extracted_contact"):
                extracted_contact = ExtractedContact(**state.values["extracted_contact"])

    except Exception:
        # Fallback to MongoSessionStore if graph state is empty
        raw_msgs = await store.get_messages(session_id)
        for msg in raw_msgs:
            try:
                role_enum = MessageRole(msg.get("role", "assistant"))
            except ValueError:
                role_enum = MessageRole.ASSISTANT
            messages.append(
                ChatMessage(
                    role=role_enum,
                    content=msg.get("content", ""),
                    metadata=msg.get("metadata"),
                )
            )

    return SessionMessagesResponse(
        session_id=session_id,
        status=status,
        messages=messages,
        extracted_data=extracted_contact,
        has_pending_contact=session.has_pending_contact,
    )


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated data."""
    store = MongoSessionStore()
    deleted = await store.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}

