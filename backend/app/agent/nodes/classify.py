"""
Node: classify_input — determines whether input is image, audio, or text.
"""

import logging
from app.agent.state import AgentState

logger = logging.getLogger(__name__)


def classify_input(state: AgentState) -> dict:
    """
    Inspect state to determine the type of input received.
    Sets input_type to 'image', 'audio', or 'text'.
    """
    if state.get("image_data"):
        input_type = "image"
        logger.info(f"[classify] Input classified as IMAGE for session {state['session_id']}")
    elif state.get("audio_data"):
        input_type = "audio"
        logger.info(f"[classify] Input classified as AUDIO for session {state['session_id']}")
    else:
        input_type = "text"
        logger.info(f"[classify] Input classified as TEXT for session {state['session_id']}")

    return {"input_type": input_type}
