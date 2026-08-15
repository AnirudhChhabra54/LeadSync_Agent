"""
Node: process_voice_note — upload audio to Cloudinary and transcribe via Gemini.
Then update the matching contact's Google Sheets row.
"""

import logging
from pymongo import MongoClient

from app.agent.state import AgentState
from app.config import get_settings
from app.services.audio import upload_audio_to_cloudinary, transcribe_audio, summarize_transcription
from app.services.sheets import update_row_voice_note, find_row_by_session_and_name

logger = logging.getLogger(__name__)


def process_voice_note(state: AgentState) -> dict:
    """
    Process an uploaded voice note:
    1. Upload to Cloudinary for hosting
    2. Transcribe with Gemini
    3. Summarize the transcription
    4. Update the matching contact row in Google Sheets
    """
    audio_data = state.get("audio_data")
    audio_filename = state.get("audio_filename", "voice_note.mp3")
    audio_mime_type = state.get("audio_mime_type", "audio/mpeg")
    session_id = state.get("session_id", "")
    pending_name = state.get("pending_contact_name", "")
    row_index = state.get("sheet_row_index")

    if not audio_data:
        return {
            "error": "No audio data provided",
            "messages": [{
                "role": "assistant",
                "content": "❌ No audio data received. Please upload a voice note.",
            }],
        }

    # If pending contact is not in state, attempt to fetch from MongoDB
    if not pending_name or not row_index:
        try:
            settings = get_settings()
            if settings.MONGODB_URI:
                client = MongoClient(settings.MONGODB_URI)
                db = client.leadsync
                pending_doc = db.pending_contacts.find_one({"session_id": session_id})
                if pending_doc:
                    pending_name = pending_name or pending_doc.get("contact_name", "")
                    row_index = row_index or pending_doc.get("sheet_row")
                    logger.info(f"[voice] Retrieved pending contact '{pending_name}' (row {row_index}) from MongoDB")
        except Exception as e:
            logger.warning(f"[voice] Could not fetch pending contact from MongoDB: {e}")

    if not pending_name:
        return {
            "messages": [{
                "role": "assistant",
                "content": "⚠️ No contact is currently awaiting a voice note in this session. "
                           "Please upload a visiting card first, then attach a voice note.",
            }],
        }

    logger.info(f"[voice] Processing voice note for contact: {pending_name}")

    # Step 1: Upload to Cloudinary
    audio_url = upload_audio_to_cloudinary(audio_data, audio_filename)
    if not audio_url:
        return {
            "error": "Failed to upload audio",
            "messages": [{
                "role": "assistant",
                "content": "❌ Failed to upload the voice note. Please try again.",
            }],
        }

    # Step 2: Transcribe via Gemini
    transcription = transcribe_audio(audio_data, audio_mime_type)
    if not transcription:
        transcription = "(Transcription unavailable)"

    # Step 3: Summarize via Gemini
    summary = summarize_transcription(transcription)

    # Step 4: Find sheet row if not known
    if not row_index or row_index <= 0:
        row_index = find_row_by_session_and_name(session_id, pending_name)

    if row_index and row_index > 0:
        update_row_voice_note(
            row_index=row_index,
            audio_url=audio_url,
            voice_summary=summary,
            status="Complete — voice note attached",
        )
        logger.info(f"[voice] Sheet row {row_index} updated with voice note")
    else:
        logger.warning(f"[voice] Could not find sheet row for {pending_name} in session {session_id}")

    # Clear pending contact in MongoDB
    try:
        settings = get_settings()
        if settings.MONGODB_URI:
            client = MongoClient(settings.MONGODB_URI)
            db = client.leadsync
            db.pending_contacts.delete_many({"session_id": session_id})
            db.sessions.update_one({"_id": session_id}, {"$set": {"has_pending_contact": False}})
            logger.info(f"[voice] Cleared pending contact for session {session_id} in MongoDB")
    except Exception as e:
        logger.warning(f"[voice] Could not clear pending contact in MongoDB: {e}")

    return {
        "audio_data": None,  # Purge raw audio bytes to keep MongoDB checkpoints small
        "audio_url": audio_url,
        "voice_transcription": transcription,
        "voice_summary": summary,
        "pending_contact_name": None,  # Clear pending in graph state
        "messages": [{
            "role": "assistant",
            "content": (
                f"🎙️ Voice note attached to **{pending_name}**!\n\n"
                f"**Audio URL:** [Listen]({audio_url})\n\n"
                f"**Summary:** {summary}\n\n"
                f"The contact record has been updated in Google Sheets."
            ),
            "metadata": {
                "type": "voice_note",
                "audio_url": audio_url,
                "summary": summary,
                "transcription": transcription,
            },
        }],
    }
