"""
Field extraction via Groq LLM.

Input:  transcription text string
Output: dict with extracted field values (None for missing fields)

Retries once on JSON parse failure with an explicit error hint.
"""

import json
import logging
import re

from groq import Groq

from config import config
from prompts.extraction_prompt import build_extraction_prompt

logger = logging.getLogger(__name__)

_client = Groq(api_key=config.groq_api_key)
_LLM_MODEL = "llama-3.3-70b-versatile"


def extract(transcription: str) -> dict:
    """
    Extract structured bar fields from transcription text.
    Returns an empty dict on unrecoverable failure (logged as error).
    """
    if not transcription or not transcription.strip():
        return {}

    prompt = build_extraction_prompt(transcription)

    for attempt in range(2):
        try:
            raw = _call_llm(prompt)
            return _parse_json(raw)
        except json.JSONDecodeError as e:
            if attempt == 0:
                logger.warning(f"JSON parse failed (attempt 1): {e}. Retrying with hint.")
                prompt += (
                    f"\n\nERROR en tu respuesta anterior: {e}. "
                    "Devolvé ÚNICAMENTE JSON puro, sin markdown, sin backticks, sin texto extra."
                )
            else:
                logger.error(f"JSON parse failed (attempt 2): {e}. Returning empty dict.")
                return {}
        except Exception as e:
            logger.error(f"Groq LLM error: {e}")
            return {}

    return {}


def _call_llm(prompt: str) -> str:
    response = _client.chat.completions.create(
        model=_LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def _parse_json(raw: str) -> dict:
    """Strip markdown code fences if present, then parse JSON."""
    # Remove ```json ... ``` or ``` ... ``` wrappers
    clean = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean)
    return json.loads(clean.strip())
