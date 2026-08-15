"""
MongoDB service — session persistence and chat history storage.
Uses Motor (async MongoDB driver) for non-blocking operations.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, PyMongoError

try:
    import dns.resolver
    # Fallback to public DNS if local resolver fails on SRV records
    resolver = dns.resolver.get_default_resolver() if hasattr(dns.resolver, "get_default_resolver") else getattr(dns.resolver, "default_resolver", None)
    if callable(resolver):
        resolver = resolver()
    if resolver and hasattr(resolver, "nameservers"):
        resolver.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
except Exception:
    pass

from app.config import get_settings
from app.models import SessionInfo

logger = logging.getLogger(__name__)

# Module-level client (initialized on first use)
_client: Optional[AsyncIOMotorClient] = None
_db = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Get or create the async MongoDB client."""
    global _client, _db
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
        _db = _client.leadsync
        logger.info("MongoDB client initialized")
    return _client


def get_db():
    """Get the leadsync database instance."""
    global _db
    if _db is None:
        get_mongo_client()
    return _db


async def close_mongo_client():
    """Close the MongoDB client connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB client closed")


async def ping_mongo() -> bool:
    """Check MongoDB connectivity."""
    try:
        client = get_mongo_client()
        await client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False


class MongoSessionStore:
    """
    Manages chat sessions in MongoDB.

    Collections:
    - sessions: Session metadata (id, title, timestamps)
    - chat_history: Message history per session
    - pending_contacts: Tracks which contact is awaiting a voice note per session
    """

    def __init__(self):
        self.db = get_db()
        self.sessions = self.db["sessions"]
        self.chat_history = self.db["chat_history"]
        self.pending_contacts = self.db["pending_contacts"]

    async def create_session(self, session_info: SessionInfo) -> str:
        """Create a new session record."""
        doc = {
            "_id": session_info.session_id,
            "title": session_info.title,
            "created_at": session_info.created_at,
            "updated_at": session_info.updated_at,
            "message_count": 0,
            "has_pending_contact": False,
        }
        await self.sessions.insert_one(doc)
        logger.info(f"Created session: {session_info.session_id}")
        return session_info.session_id

    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieve a session by ID."""
        doc = await self.sessions.find_one({"_id": session_id})
        if not doc:
            return None
        return SessionInfo(
            session_id=doc["_id"],
            title=doc.get("title", "New Session"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            message_count=doc.get("message_count", 0),
            has_pending_contact=doc.get("has_pending_contact", False),
        )

    async def list_sessions(self) -> list[SessionInfo]:
        """List all sessions, most recent first."""
        cursor = self.sessions.find().sort("updated_at", -1)
        sessions = []
        async for doc in cursor:
            sessions.append(
                SessionInfo(
                    session_id=doc["_id"],
                    title=doc.get("title", "New Session"),
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"],
                    message_count=doc.get("message_count", 0),
                    has_pending_contact=doc.get("has_pending_contact", False),
                )
            )
        return sessions

    async def update_session(self, session_id: str, **updates):
        """Update session fields."""
        updates["updated_at"] = datetime.now(timezone.utc)
        await self.sessions.update_one(
            {"_id": session_id},
            {"$set": updates},
        )

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and its related data."""
        result = await self.sessions.delete_one({"_id": session_id})
        await self.chat_history.delete_many({"session_id": session_id})
        await self.pending_contacts.delete_many({"session_id": session_id})
        return result.deleted_count > 0

    async def add_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Append a message to the session's chat history."""
        doc = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc),
        }
        await self.chat_history.insert_one(doc)
        await self.sessions.update_one(
            {"_id": session_id},
            {
                "$inc": {"message_count": 1},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

    async def get_messages(self, session_id: str) -> list[dict]:
        """Get all messages for a session, in chronological order."""
        cursor = self.chat_history.find(
            {"session_id": session_id}
        ).sort("timestamp", 1)
        messages = []
        async for doc in cursor:
            messages.append({
                "role": doc["role"],
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "timestamp": doc["timestamp"],
            })
        return messages

    async def set_pending_contact(self, session_id: str, contact_data: dict, sheet_row: int):
        """
        Track a contact that is awaiting a voice note attachment.
        Only one pending contact per session at a time.
        """
        await self.pending_contacts.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "session_id": session_id,
                    "contact_data": contact_data,
                    "sheet_row": sheet_row,
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
        await self.update_session(session_id, has_pending_contact=True)

    async def get_pending_contact(self, session_id: str) -> Optional[dict]:
        """Get the pending contact for a session (if any)."""
        doc = await self.pending_contacts.find_one({"session_id": session_id})
        return doc

    async def clear_pending_contact(self, session_id: str):
        """Remove the pending contact after voice note is attached."""
        await self.pending_contacts.delete_many({"session_id": session_id})
        await self.update_session(session_id, has_pending_contact=False)
