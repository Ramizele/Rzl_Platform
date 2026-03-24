from __future__ import annotations

from pathlib import Path


def load_queries(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Queries file not found: {path}")

    queries: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            queries.append(line)

    if not queries:
        raise ValueError(f"No queries found in {path}")

    return queries
