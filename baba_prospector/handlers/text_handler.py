"""
Handles text messages and slash commands.

Routing:
  /start | /help            → welcome message
  /estado                   → current bar state
  /cancelar                 → discard active bar
  /lista                    → last 5 saved bars
  "siguiente" | "listo"     → close & save active bar (configurable in YAML)
  pending_action handling   → segment confirmation, duplicate resolution
  free text                 → extract fields like an audio
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import config
from handlers import session
from handlers.route_handler import contains_maps_link, handle_route
from services import extractor, sheets, vendedores
from utils.formatter import _escape_md, build_final_summary, build_summary

logger = logging.getLogger(__name__)

# ── Help text ──────────────────────────────────────────────────────────────────

_close_cmds = " o ".join(f'*"{c}"*' for c in config.bot.get("close_commands", ["siguiente", "listo"]))

HELP_TEXT = f"""\
🍺 *Baba Prospector*

Mandame audios desde el bar y yo registro la info.

*Comandos:*
  /estado — Info capturada del bar actual
  /cancelar — Descartar el bar sin guardar
  /lista — Últimos 5 bares guardados
  /ruta — Ver paradas de la ruta activa
  /help — Este mensaje

*Para cerrar un bar:*
  Escribí {_close_cmds} cuando termines.

*Ruta del día:*
  Mandame el link de Google Maps con tus paradas antes de salir.
"""

# ── Main dispatcher ────────────────────────────────────────────────────────────


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    text_lower = text.lower()

    # Maps route link — intercept before any other processing
    if contains_maps_link(text):
        await handle_route(update, context)
        return

    # Commands (with or without leading slash)
    if text_lower in ("/start", "/help", "start", "help"):
        await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
        return

    if text_lower == "/estado":
        await _cmd_estado(update, user_id)
        return

    if text_lower == "/cancelar":
        await _cmd_cancelar(update, user_id)
        return

    if text_lower == "/lista":
        await _cmd_lista(update)
        return

    if text_lower == "/ruta":
        await _cmd_ruta(update, user_id)
        return

    # Vendedor registration gate
    if vendedores.get_vendedor(user_id) is None:
        pending = session.get_pending_action(user_id)
        if pending == "registro_vendedor":
            nombre = text.strip()
            vendedores.save_vendedor(user_id, nombre)
            session.clear_pending_action(user_id)
            await update.message.reply_text(
                f"✅ Registrado como *{nombre}*. ¡Ahora sí, mandame info del primer bar!",
                parse_mode="Markdown",
            )
            return
        session.set_pending_action(user_id, "registro_vendedor", config.fields)
        await update.message.reply_text("👋 ¡Hola! Antes de empezar, ¿cuál es tu nombre?")
        return

    # Close-bar commands
    close_commands = [c.lower() for c in config.bot.get("close_commands", ["siguiente", "listo"])]
    if text_lower in close_commands:
        await _close_bar(update, user_id)
        return

    # Pending action intercepts
    pending = session.get_pending_action(user_id)

    if pending == "confirm_segment":
        await _handle_segment_confirmation(update, user_id, text_lower)
        return

    if pending and pending.startswith("duplicate:"):
        await _handle_duplicate_resolution(update, user_id, text_lower, pending)
        return

    # Default: treat free text as additional bar info
    ruta_paradas = session.get_ruta(user_id)
    extracted = extractor.extract(text, ruta_paradas=ruta_paradas)
    current_session = session.merge(user_id, extracted, config.fields)
    response = build_summary(current_session)
    await update.message.reply_text(response, parse_mode="Markdown")


# ── Command handlers ───────────────────────────────────────────────────────────


async def _cmd_estado(update: Update, user_id: int):
    current = session.get(user_id)
    if not current or not session.has_any_data(user_id):
        await update.message.reply_text("No tenés ningún bar en progreso.")
        return
    await update.message.reply_text(build_summary(current), parse_mode="Markdown")


async def _cmd_cancelar(update: Update, user_id: int):
    session.close(user_id, config.fields)
    await update.message.reply_text("🗑️ Bar descartado. Podés empezar con uno nuevo.")


async def _cmd_lista(update: Update):
    try:
        bars = sheets.get_last_n_bars(5)
    except Exception as e:
        logger.error(f"Error fetching bar list: {e}")
        await update.message.reply_text("❌ No pude conectar con Sheets. Verificá las credenciales.")
        return

    if not bars:
        await update.message.reply_text("No hay bares guardados todavía.")
        return

    lines = ["📋 *Últimos 5 bares:*", ""]
    for bar in bars:
        nombre = bar.get("nombre") or "Sin nombre"
        loc = " — ".join(filter(None, [bar.get("barrio", ""), bar.get("direccion", "")]))
        fecha = bar.get("fecha_visita", "")
        entry = f"• *{nombre}*"
        if loc:
            entry += f" — {loc}"
        if fecha:
            entry += f" ({fecha})"
        lines.append(entry)

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def _cmd_ruta(update: Update, user_id: int):
    ruta = session.get_ruta(user_id)
    if not ruta:
        await update.message.reply_text(
            "No hay ninguna ruta activa. Mandame el link de Google Maps con tus paradas."
        )
        return

    pendientes = session.get_ruta_pendientes(user_id)
    pendientes_nombres = {p["nombre"] for p in pendientes}
    completadas_count = len(ruta) - len(pendientes)

    lines = [f"🗺️ *Ruta activa — {completadas_count}/{len(ruta)} completadas:*", ""]
    for parada in ruta:
        icon = "✅" if parada["nombre"] not in pendientes_nombres else "⏳"
        lines.append(f"  {icon} {_escape_md(parada['nombre'])}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── Close-bar flow ─────────────────────────────────────────────────────────────


async def _close_bar(update: Update, user_id: int):
    if not session.has_any_data(user_id):
        await update.message.reply_text("No hay ningún bar en progreso para guardar.")
        return

    current = session.get(user_id)
    bar_data = dict(current["bar"])
    nombre = bar_data.get("nombre")

    # Duplicate check
    if nombre:
        try:
            existing_row = sheets.find_bar_by_name(nombre)
            if existing_row:
                session.set_pending_action(user_id, f"duplicate:{existing_row}", config.fields)
                await update.message.reply_text(
                    f"⚠️ Ya tengo un registro de *{nombre}*.\n\n"
                    "¿Qué hacemos?\n"
                    "  • *actualizar* — piso el registro existente\n"
                    "  • *nuevo* — creo uno nuevo",
                    parse_mode="Markdown",
                )
                return
        except Exception as e:
            logger.warning(f"Duplicate check failed: {e}. Proceeding to save.")

    await _save_and_confirm(update, user_id, bar_data)


async def _save_and_confirm(
    update: Update,
    user_id: int,
    bar_data: dict,
    update_row: int | None = None,
):
    try:
        if update_row:
            sheets.update_bar(update_row, bar_data)
        else:
            sheets.append_bar(bar_data)
    except Exception as e:
        logger.error(f"Sheets save failed: {e}")
        await update.message.reply_text(
            "❌ No pude guardar en Sheets. Verificá las credenciales.\n"
            "La sesión sigue abierta — podés intentar de nuevo."
        )
        return

    bar_nombre = bar_data.get("nombre")
    if bar_nombre:
        session.marcar_parada_completada(user_id, bar_nombre)

    summary = build_final_summary(bar_data)
    session.close(user_id, config.fields)
    await update.message.reply_text(summary, parse_mode="Markdown")


# ── Pending action handlers ────────────────────────────────────────────────────


async def _handle_segment_confirmation(update: Update, user_id: int, text_lower: str):
    current = session.get(user_id)
    if not current:
        return

    session.clear_pending_action(user_id)
    seg_inferido = current["bar"].get("segmento_inferido")

    if text_lower in ("sí", "si", "yes", "ok", "dale", "correcto"):
        current["bar"]["segmento_confirmado"] = seg_inferido
    else:
        # Accept a segment key directly ("art_alto", "industrial", etc.)
        valid_segs = list(config.segments.keys())
        # Also accept segment labels (case-insensitive)
        label_to_key = {v["label"].lower(): k for k, v in config.segments.items()}
        resolved = label_to_key.get(text_lower) or (text_lower if text_lower in valid_segs else None)

        if resolved:
            current["bar"]["segmento_confirmado"] = resolved
            current["bar"]["segmento_inferido"] = resolved
        else:
            valid_display = ", ".join(valid_segs)
            await update.message.reply_text(
                f"No reconocí ese segmento. Opciones: {valid_display}"
            )
            session.set_pending_action(user_id, "confirm_segment", config.fields)
            return

    response = build_summary(current)
    await update.message.reply_text(response, parse_mode="Markdown")


async def _handle_duplicate_resolution(
    update: Update, user_id: int, text_lower: str, pending: str
):
    row = int(pending.split(":")[1])
    session.clear_pending_action(user_id)
    current = session.get(user_id)
    if not current:
        return

    bar_data = dict(current["bar"])

    if text_lower in ("actualizar", "update", "pisar", "actualiza"):
        await _save_and_confirm(update, user_id, bar_data, update_row=row)
    elif text_lower in ("nuevo", "new", "crear", "crea"):
        await _save_and_confirm(update, user_id, bar_data)
    else:
        # Re-set the pending action and ask again
        session.set_pending_action(user_id, f"duplicate:{row}", config.fields)
        await update.message.reply_text(
            "Respondé *actualizar* (piso el existente) o *nuevo* (creo uno nuevo).",
            parse_mode="Markdown",
        )
