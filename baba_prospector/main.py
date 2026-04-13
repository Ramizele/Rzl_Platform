"""
Baba Prospector Bot — entry point.

Run:
    python main.py
"""

import logging
import sys

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import config
from handlers.audio_handler import handle_audio
from handlers.text_handler import handle_text

# Force UTF-8 on Windows consoles (cp1252 can't encode emojis)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s  %(name)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    _validate_config()

    app = Application.builder().token(config.telegram_token).build()

    # Voice / audio messages
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    # Slash commands
    app.add_handler(CommandHandler(["start", "help"], handle_text))
    app.add_handler(CommandHandler("estado", handle_text))
    app.add_handler(CommandHandler("cancelar", handle_text))
    app.add_handler(CommandHandler("lista", handle_text))
    app.add_handler(CommandHandler("ruta", handle_text))

    # Plain text (bar info + close commands + confirmations)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🍺 Baba Prospector Bot started. Polling…")
    app.run_polling(drop_pending_updates=True)


def _validate_config():
    missing = []
    if not config.telegram_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not config.groq_api_key:
        missing.append("GROQ_API_KEY")
    if not config.sheets_id:
        missing.append("GOOGLE_SHEETS_ID")
    if missing:
        logger.error(f"Missing required env vars: {', '.join(missing)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
