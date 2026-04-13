"""
In-memory session state per Telegram user.

sessions[user_id] = {
    "bar":              {field_key: value | None, ...},  # active bar being captured
    "audio_count":      int,                              # audios received this bar
    "pending_action":   str | None,                       # e.g. "confirm_segment", "duplicate:7"
    "ruta_activa":      list[dict] | None,                # paradas de la ruta del día
    "ruta_completadas": list[str],                        # nombres de paradas ya registradas
}
"""

from typing import Any

from services import vendedores

# Module-level store — lives for the duration of the process
sessions: dict[int, dict] = {}


def _empty_bar(fields: list[dict]) -> dict[str, Any]:
    """Create a bar dict with all non-metadata field keys set to None."""
    return {f["key"]: None for f in fields if f["priority"] != "metadata"}


def get_or_create(user_id: int, fields: list[dict]) -> dict:
    if user_id not in sessions:
        bar = _empty_bar(fields)
        bar["vendedor"] = vendedores.get_vendedor(user_id)
        sessions[user_id] = {
            "bar": bar,
            "audio_count": 0,
            "pending_action": None,
            "ruta_activa": None,
            "ruta_completadas": [],
        }
    return sessions[user_id]


def merge(user_id: int, extracted: dict[str, Any], fields: list[dict]) -> dict:
    """
    Merge extracted fields into the active session.

    Rules:
    - Existing non-null values are NOT overwritten (first capture wins).
    - Exception: 'comentarios' values are concatenated with ' / '.
    - audio_count is incremented on each call.
    """
    session = get_or_create(user_id, fields)
    bar = session["bar"]

    if bar.get("vendedor") is None:
        bar["vendedor"] = vendedores.get_vendedor(user_id)

    for key, value in extracted.items():
        if value is None:
            continue
        existing = bar.get(key)
        if existing is None:
            bar[key] = value
        elif key == "comentarios":
            bar[key] = f"{existing} / {value}"
        # All other cases: keep existing (first capture wins)

    session["audio_count"] += 1
    return session


def get(user_id: int) -> dict | None:
    return sessions.get(user_id)


def has_any_data(user_id: int) -> bool:
    session = sessions.get(user_id)
    if not session:
        return False
    return any(v is not None for v in session["bar"].values())


def close(user_id: int, fields: list[dict]) -> dict:
    """
    Returns the current bar data snapshot and resets the session to empty.
    Safe to call even if no session exists.
    """
    session = get_or_create(user_id, fields)
    bar_snapshot = dict(session["bar"])
    sessions[user_id] = {
        "bar": _empty_bar(fields),
        "audio_count": 0,
        "pending_action": None,
        "ruta_activa": session.get("ruta_activa"),
        "ruta_completadas": session.get("ruta_completadas", []),
    }
    return bar_snapshot


def set_pending_action(user_id: int, action: str, fields: list[dict]):
    session = get_or_create(user_id, fields)
    session["pending_action"] = action


def get_pending_action(user_id: int) -> str | None:
    session = sessions.get(user_id)
    return session["pending_action"] if session else None


def clear_pending_action(user_id: int):
    if user_id in sessions:
        sessions[user_id]["pending_action"] = None


# ── Ruta helpers ───────────────────────────────────────────────────────────────


def set_ruta(user_id: int, paradas: list[dict], fields: list[dict]):
    """Guarda la ruta activa del vendedor, resetea completadas."""
    session = get_or_create(user_id, fields)
    session["ruta_activa"] = paradas
    session["ruta_completadas"] = []


def get_ruta(user_id: int) -> list[dict] | None:
    """Devuelve la ruta activa o None."""
    s = sessions.get(user_id)
    return s.get("ruta_activa") if s else None


def get_ruta_pendientes(user_id: int) -> list[dict]:
    """Devuelve las paradas que todavía no fueron registradas."""
    s = sessions.get(user_id)
    if not s or not s.get("ruta_activa"):
        return []
    completadas = set(s.get("ruta_completadas", []))
    return [p for p in s["ruta_activa"] if p["nombre"] not in completadas]


def marcar_parada_completada(user_id: int, nombre_parada: str):
    """Marca una parada como registrada."""
    if user_id in sessions:
        sessions[user_id].setdefault("ruta_completadas", []).append(nombre_parada)


def clear_ruta(user_id: int):
    """Limpia la ruta activa."""
    if user_id in sessions:
        sessions[user_id]["ruta_activa"] = None
        sessions[user_id]["ruta_completadas"] = []
