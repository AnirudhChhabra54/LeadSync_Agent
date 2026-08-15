"""
Audio service — upload to Cloudinary and transcribe/summarize with Gemini.
"""

import logging
import tempfile
import os
import socket
from typing import Optional

try:
    import dns.resolver
    _orig_getaddrinfo = socket.getaddrinfo

    def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        try:
            return _orig_getaddrinfo(host, port, family, type, proto, flags)
        except socket.gaierror:
            try:
                r = dns.resolver.Resolver()
                r.nameservers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
                answers = r.resolve(host, "A")
                ip = answers[0].address
                return _orig_getaddrinfo(ip, port, family, type, proto, flags)
            except Exception:
                raise socket.gaierror(8, f"nodename nor servname provided, or not known")

    socket.getaddrinfo = _patched_getaddrinfo
except Exception:
    pass

import cloudinary
import cloudinary.uploader
from google import genai
from google.genai import types

from app.config import get_settings

logger = logging.getLogger(__name__)

_cloudinary_configured = False


def _configure_cloudinary():
    """Initialize Cloudinary config from environment variables."""
    global _cloudinary_configured
    if not _cloudinary_configured:
        settings = get_settings()
        if settings.CLOUDINARY_CLOUD_NAME:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
            )
            _cloudinary_configured = True
            logger.info("Cloudinary configured")
        else:
            logger.warning("Cloudinary credentials not configured")


def upload_audio_to_cloudinary(
    audio_bytes: bytes,
    filename: str = "voice_note.mp3",
) -> Optional[str]:
    """
    Upload an audio file to Cloudinary.
    Uses resource_type='auto' to support all audio formats (webm, mp3, wav, etc.).

    Returns the secure URL of the uploaded file, or None on failure.
    """
    _configure_cloudinary()
    settings = get_settings()

    if not settings.CLOUDINARY_CLOUD_NAME:
        logger.info("[STUB] Cloudinary not configured — returning mock URL")
        return "https://res.cloudinary.com/demo/video/upload/sample_voice_note.mp3"

    tmp_path = None
    try:
        # Write to temp file for upload
        suffix = os.path.splitext(filename)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        result = cloudinary.uploader.upload(
            tmp_path,
            resource_type="auto",
            folder="leadsync_voice_notes",
        )

        secure_url = result.get("secure_url")
        logger.info(f"Audio uploaded to Cloudinary: {secure_url}")
        return secure_url

    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str = "audio/mpeg",
) -> Optional[str]:
    """
    Transcribe audio using Gemini (single-provider approach).

    Returns the transcription text or None on failure.
    """
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        logger.info("[STUB] Gemini not configured — returning mock transcription")
        return "This is a mock transcription of the voice note. The client mentioned they are interested in our enterprise plan and would like a follow-up call next week."

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        transcription = None
        for model_name in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        types.Content(
                            parts=[
                                types.Part.from_text(
                                    text="Transcribe the following audio recording verbatim. Return only the transcription text, nothing else."
                                ),
                                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                            ]
                        )
                    ],
                )
                if response and response.text:
                    transcription = response.text.strip()
                    break
            except Exception as m_err:
                logger.warning(f"Audio model {model_name} failed: {m_err}")
                continue

        if transcription:
            logger.info(f"Audio transcribed: {len(transcription)} characters")
            return transcription
        return None

    except Exception as e:
        logger.error(f"Audio transcription failed: {e}")
        return None


def summarize_transcription(transcription: str) -> str:
    """
    Summarize a voice note transcription using Gemini.

    Returns a concise summary string.
    """
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        logger.info("[STUB] Gemini not configured — returning mock summary")
        return "Client interested in enterprise plan; requesting follow-up call next week."

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        for model_name in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"Summarize this voice note transcription in 1-2 concise sentences, focusing on key action items and decisions:\n\n{transcription}",
                )
                if response and response.text:
                    summary = response.text.strip()
                    logger.info(f"Transcription summarized: {summary[:80]}...")
                    return summary
            except Exception as m_err:
                logger.warning(f"Summary model {model_name} failed: {m_err}")
                continue

        return transcription[:200]

    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return transcription[:200]  # Fallback: truncated transcription
