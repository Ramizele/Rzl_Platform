"""
Builds Telegram-ready response messages from session state.

All field ordering and labels come from config/fields.yaml —
never hardcoded here.
"""

from typing import Any

from config import config


def build_summary(session: dict) -> str:
    """
    Progressive summary shown after each audio/text input.
    Includes the next question to ask based on bot.behavior in the YAML.
    """
    bar: dict[str, Any] = session["bar"]
    behavior: str = config.bot.get("behavior", "activo")

    # ── Header ────────────────────────────────────────────────────────────
    nombre = bar.get("nombre")
    direccion = bar.get("direccion")
    barrio = bar.get("barrio")

    lines: list[str] = []
    if nombre:
        lines.append(f"📍 *{_escape_md(nombre)}*")
        loc = " — ".join(filter(None, [_escape_md(direccion) if direccion else None, _escape_md(barrio) if barrio else None]))
        if loc:
            lines.append(f"📌 {loc}")
        lines.append("")

    # ── Captured fields (clave + recomendado + util) ──────────────────────
    priority_fields = config.get_fields_ordered_by_ask_priority()
    util_fields = config.get_fields_by_priority("util")

    captured_priority = [
        (f, bar[f["key"]]) for f in priority_fields if bar.get(f["key"]) is not None
    ]
    captured_util = [
        (f, bar[f["key"]]) for f in util_fields if bar.get(f["key"]) is not None
    ]
    # Avoid double-counting fields that appear in both lists
    priority_keys = {f["key"] for f in priority_fields}
    captured_util = [(f, v) for f, v in captured_util if f["key"] not in priority_keys]

    all_captured = captured_priority + captured_util
    if all_captured:
        lines.append("✅ *Capturado:*")
        for field, value in all_captured:
            lines.append(f"  • {field['label']}: {_fmt(value)}")
        lines.append("")

    # ── Missing fields ─────────────────────────────────────────────────────
    missing_clave = [
        f for f in priority_fields
        if f["priority"] == "clave" and bar.get(f["key"]) is None
    ]
    missing_rec = [
        f for f in priority_fields
        if f["priority"] == "recomendado" and bar.get(f["key"]) is None
    ]

    if missing_clave:
        lines.append("⚠️ *Falta información CLAVE:*")
        for f in missing_clave:
            lines.append(f"  • {f['label']}")
        lines.append("")

    if missing_rec:
        lines.append("⚠️ *Falta información recomendada:*")
        for f in missing_rec:
            lines.append(f"  • {f['label']}")
        lines.append("")

    # ── Free comments ──────────────────────────────────────────────────────
    comentarios = bar.get("comentarios")
    if comentarios:
        lines.append("💬 *Notas extra:*")
        lines.append(f'  "{_escape_md(comentarios)}"')
        lines.append("")

    # ── Segment confirmation ───────────────────────────────────────────────
    seg_inferido = bar.get("segmento_inferido")
    seg_confirmado = bar.get("segmento_confirmado")
    if seg_inferido and not seg_confirmado:
        seg_label = config.segments.get(seg_inferido, {}).get("label", seg_inferido)
        birras = bar.get("birras_actuales_marcas")
        lines.append(f"🍺 Inferí segmento *{_escape_md(str(seg_label))}*")
        if birras:
            lines.append(f"  (marcas: {_escape_md(str(birras))})")
        lines.append("¿Es correcto? *(sí / no / [segmento correcto])*")
        return "\n".join(lines).strip()

    # ── Next question ──────────────────────────────────────────────────────
    all_priority = priority_fields
    next_q = _next_question(bar, all_priority, behavior)
    if next_q:
        lines.append(next_q)

    return "\n".join(lines).strip()


def build_final_summary(bar: dict[str, Any]) -> str:
    """
    Complete summary shown when the bar is closed ('siguiente'/'listo').
    Shows all captured fields and flags remaining gaps.
    """
    nombre = bar.get("nombre") or "Bar sin nombre"
    lines = [f"✅ *Bar guardado: {_escape_md(nombre)}*", ""]

    # All non-metadata fields in YAML order
    display_fields = [f for f in config.fields if f["priority"] not in ("metadata",)]
    for field in display_fields:
        value = bar.get(field["key"])
        if value is not None:
            lines.append(f"  • {field['label']}: {_fmt(value)}")

    # Remaining gaps for priority fields
    priority_fields = config.get_fields_ordered_by_ask_priority()
    missing = [f for f in priority_fields if bar.get(f["key"]) is None]
    if missing:
        lines.append("")
        lines.append("⚠️ *Quedó sin completar:*")
        for f in missing:
            icon = "🔴" if f["priority"] == "clave" else "🟡"
            lines.append(f"  {icon} {f['label']}")

    lines.append("")
    lines.append("¿Empezamos con el siguiente bar?")
    return "\n".join(lines)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _escape_md(text: str) -> str:
    """Escape characters special to Telegram legacy Markdown (parse_mode='Markdown')."""
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


def _fmt(value: Any) -> str:
    if isinstance(value, bool):
        return "Sí" if value else "No"
    return _escape_md(str(value))


def _next_question(
    bar: dict[str, Any], priority_fields: list[dict], behavior: str
) -> str | None:
    """
    Returns a single question string for the highest-priority missing field,
    respecting the bot behavior setting.

    Rules:
    - 'activo':  ask for any missing clave or recomendado field
    - 'hibrido': ask only for missing clave fields
    - 'pasivo':  never ask
    - Paired fields (same ask_priority): skip if any sibling is already captured
    """
    if behavior == "pasivo":
        return None

    for field in priority_fields:
        if bar.get(field["key"]) is not None:
            continue

        priority = field["priority"]
        if behavior == "hibrido" and priority != "clave":
            continue

        # Paired fields: if any sibling at the same ask_priority level is captured, skip
        ask_p = field.get("ask_priority")
        if ask_p is not None:
            siblings = [f for f in priority_fields if f.get("ask_priority") == ask_p]
            if len(siblings) > 1 and any(bar.get(s["key"]) is not None for s in siblings):
                continue

        return f"¿{field['label']}?"

    return None
