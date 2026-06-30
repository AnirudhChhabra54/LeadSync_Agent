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

from app.models import SessionInfo, SessionListResponse, SessionCreateResponse
from app.services.mongodb import MongoSessionStore

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


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated data."""
    store = MongoSessionStore()
    deleted = await store.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}
