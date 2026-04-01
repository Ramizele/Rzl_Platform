"""
Audio transcription via Groq Whisper.

Input:  path to a downloaded OGG/OPUS file
Output: transcribed text string

The OGG is sent directly to Groq Whisper (supports ogg/opus natively),
then the temp file is deleted.
"""

import logging
import os

from groq import Groq

from config import config

logger = logging.getLogger(__name__)

_client = Groq(api_key=config.groq_api_key)
_WHISPER_MODEL = "whisper-large-v3"


def transcribe(ogg_path: str) -> str:
    """
    Transcribe an OGG audio file. Raises on unrecoverable errors.
    Deletes the OGG when done (success or failure).
    """
    try:
        return _call_whisper(ogg_path)
    finally:
        _cleanup(ogg_path)


def _call_whisper(ogg_path: str) -> str:
    lang = config.bot.get("language", "es").split("-")[0]
    try:
        with open(ogg_path, "rb") as f:
            result = _client.audio.transcriptions.create(
                model=_WHISPER_MODEL,
                file=(os.path.basename(ogg_path), f, "audio/ogg"),
                language=lang,
                response_format="text",
            )
        text = result if isinstance(result, str) else getattr(result, "text", str(result))
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Groq Whisper API error: {e}") from e


def _cleanup(*paths: str):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except OSError as e:
            logger.warning(f"Could not delete temp file {path}: {e}")
