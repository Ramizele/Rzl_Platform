"""Persistent vendor registry backed by data/vendedores.json."""

import json
from pathlib import Path

_DATA_FILE = Path(__file__).parent.parent / "data" / "vendedores.json"


def _load() -> dict:
    if not _DATA_FILE.exists():
        return {}
    return json.loads(_DATA_FILE.read_text(encoding="utf-8"))


def _save(data: dict):
    _DATA_FILE.parent.mkdir(exist_ok=True)
    _DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_vendedor(user_id: int) -> str | None:
    return _load().get(str(user_id))


def save_vendedor(user_id: int, nombre: str):
    data = _load()
    data[str(user_id)] = nombre.strip()
    _save(data)
