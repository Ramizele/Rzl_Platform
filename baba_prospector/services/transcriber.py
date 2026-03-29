"""
Audio transcription via Groq Whisper.

Input:  path to a downloaded OGG/OPUS file
Output: transcribed text string

The OGG is converted to MP3 with pydub (requires ffmpeg in PATH),
sent to Groq Whisper, then both temp files are deleted.
"""

import logging
import os

from groq import Groq
from pydub import AudioSegment

from config import config

logger = logging.getLogger(__name__)

_client = Groq(api_key=config.groq_api_key)
_WHISPER_MODEL = "whisper-large-v3"


def transcribe(ogg_path: str) -> str:
    """
    Transcribe an OGG audio file. Raises on unrecoverable errors.
    Deletes both the OGG and the converted MP3 when done (success or failure).
    """
    mp3_path = ogg_path.replace(".ogg", ".mp3")
    try:
        _convert_to_mp3(ogg_path, mp3_path)
        return _call_whisper(mp3_path)
    finally:
        _cleanup(ogg_path, mp3_path)


def _convert_to_mp3(ogg_path: str, mp3_path: str):
    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(mp3_path, format="mp3")
    except Exception as e:
        raise RuntimeError(f"Audio conversion failed: {e}") from e


def _call_whisper(mp3_path: str) -> str:
    # language is "es" (ISO 639-1), strip region code if present
    lang = config.bot.get("language", "es").split("-")[0]
    try:
        with open(mp3_path, "rb") as f:
            result = _client.audio.transcriptions.create(
                model=_WHISPER_MODEL,
                file=f,
                language=lang,
                response_format="text",
            )
        # Groq returns a plain string when response_format="text"
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
