"""
Handles incoming voice/audio messages.

Flow:
  1. Download OGG to /tmp
  2. Transcribe via Groq Whisper
  3. Extract fields via Groq LLM
  4. Merge into session
  5. Send formatted summary back
  6. Temp files cleaned up inside transcriber
"""

import logging
import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from config import config
from handlers import session
from services import extractor, transcriber, vendedores
from utils.formatter import build_summary

logger = logging.getLogger(__name__)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    voice = update.message.voice or update.message.audio

    if not voice:
        return

    # Vendedor registration gate
    if vendedores.get_vendedor(user_id) is None:
        session.set_pending_action(user_id, "registro_vendedor", config.fields)
        await update.message.reply_text("👋 ¡Hola! Antes de empezar, ¿cuál es tu nombre?")
        return

    # ── Download ───────────────────────────────────────────────────────────
    ogg_path = os.path.join(
        tempfile.gettempdir(), f"baba_{user_id}_{voice.file_unique_id}.ogg"
    )
    try:
        tg_file = await context.bot.get_file(voice.file_id)
        await tg_file.download_to_drive(ogg_path)
    except Exception as e:
        logger.error(f"Audio download failed for user {user_id}: {e}")
        await update.message.reply_text("❌ No pude descargar el audio. Intentá de nuevo.")
        return

    # ── Transcribe ─────────────────────────────────────────────────────────
    await update.message.reply_text("🎙️ Transcribiendo...")
    try:
        text = transcriber.transcribe(ogg_path)
    except Exception as e:
        logger.error(f"Transcription failed for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ No pude transcribir el audio. ¿Podés mandarlo de nuevo o hablar más claro?"
        )
        # transcriber cleans up files in its finally block
        return

    if not text:
        await update.message.reply_text(
            "❌ No entendí el audio. Intentá acercarte al micrófono o mandar el mensaje de vuelta."
        )
        return

    # ── Extract fields ─────────────────────────────────────────────────────
    ruta_paradas = session.get_ruta(user_id)
    extracted = extractor.extract(text, ruta_paradas=ruta_paradas)
    if not extracted:
        await update.message.reply_text(
            "⚠️ Transcribí el audio pero no pude extraer campos.\n"
            f'_Transcripción: "{text}"_\n'
            "Podés mandarlo de nuevo o escribir la info directamente.",
            parse_mode="Markdown",
        )
        return

    # ── Update session ─────────────────────────────────────────────────────
    current_session = session.merge(user_id, extracted, config.fields)

    # ── Respond ────────────────────────────────────────────────────────────
    response = build_summary(current_session)
    await update.message.reply_text(response, parse_mode="Markdown")
