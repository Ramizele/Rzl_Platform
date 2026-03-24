from __future__ import annotations

import csv
import re
from pathlib import Path

DEDUP_FIELDNAMES = ("Nombre", "Direccion")


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _build_key(nombre: str, direccion: str) -> tuple[str, str]:
    return (_normalize(nombre), _normalize(direccion))


def load_known_places(path: Path) -> dict[tuple[str, str], tuple[str, str]]:
    known_places: dict[tuple[str, str], tuple[str, str]] = {}
    if not path.exists():
        return known_places

    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            nombre = (row.get("Nombre") or "").strip()
            direccion = (row.get("Direccion") or "").strip()
            if not nombre or not direccion:
                continue
            known_places[_build_key(nombre, direccion)] = (nombre, direccion)

    return known_places


def add_known_place(
    known_places: dict[tuple[str, str], tuple[str, str]],
    row: dict[str, str],
) -> bool:
    nombre = (row.get("Nombre") or "").strip()
    direccion = (row.get("Direccion") or "").strip()
    if not nombre or not direccion:
        return False

    key = _build_key(nombre, direccion)
    if key in known_places:
        return False

    known_places[key] = (nombre, direccion)
    return True


def persist_known_places(path: Path, known_places: dict[tuple[str, str], tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DEDUP_FIELDNAMES))
        writer.writeheader()
        for _, (nombre, direccion) in sorted(known_places.items(), key=lambda item: item[1]):
            writer.writerow({"Nombre": nombre, "Direccion": direccion})
