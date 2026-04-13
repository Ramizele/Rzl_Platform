"""
Detecta y procesa links de Google Maps en mensajes de texto.

Si el mensaje contiene un link de ruta válido:
  - Parsea las paradas
  - Las guarda en sesión
  - Confirma al vendedor con la lista numerada

Si el link es de un lugar individual (no ruta), avisa al vendedor.
Retorna True si el mensaje fue manejado, False si no era un link de Maps.
"""

import logging
import re

from telegram import Update
from telegram.ext import ContextTypes

from config import config
from handlers import session
from services.route_parser import parse_route_url
from utils.formatter import _escape_md

logger = logging.getLogger(__name__)

MAPS_URL_PATTERN = re.compile(
    r"https?://(?:maps\.app\.goo\.gl/\S+|(?:www\.)?google\.com/maps/\S+)"
)


def contains_maps_link(text: str) -> bool:
    """Devuelve True si el texto contiene un link de Google Maps."""
    return bool(MAPS_URL_PATTERN.search(text))


async def handle_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Intenta procesar el mensaje como un link de ruta.
    Retorna True si el mensaje fue manejado (era un link de Maps).
    Retorna False si no había link de Maps.
    """
    text = update.message.text or ""
    match = MAPS_URL_PATTERN.search(text)
    if not match:
        return False

    user_id = update.effective_user.id
    url = match.group(0)

    await update.message.reply_text("🗺️ Procesando la ruta...")

    try:
        paradas = parse_route_url(url)
    except ValueError as e:
        await update.message.reply_text(
            f"⚠️ No pude leer la ruta: {e}\n"
            "Asegurate de mandar el link de una ruta con múltiples paradas, no de un lugar individual."
        )
        return True
    except Exception as e:
        logger.error(f"Route parsing failed for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ No pude procesar el link. ¿Podés mandarlo de nuevo?"
        )
        return True

    had_ruta = session.get_ruta(user_id) is not None
    session.set_ruta(user_id, paradas, config.fields)

    header = "✅ *Ruta actualizada*" if had_ruta else "✅ *Ruta cargada*"
    lines = [f"{header} — {len(paradas)} paradas:", ""]
    for i, parada in enumerate(paradas, 1):
        loc = " — ".join(filter(None, [parada.get("direccion"), parada.get("barrio")]))
        lines.append(f"  {i}. *{_escape_md(parada['nombre'])}*")
        if loc:
            lines.append(f"      📍 {_escape_md(loc)}")

    lines.append("")
    lines.append("Cuando llegues a cada lugar, mandame el audio normalmente.")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    return True
