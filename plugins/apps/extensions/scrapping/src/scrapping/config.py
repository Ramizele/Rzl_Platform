from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence, Tuple

FIELDNAMES = (
    "Nombre",
    "Direccion",
    "Barrio",
    "Telefono",
    "Instagram_o_Web",
    "Estrellas",
    "Comentarios",
    "Estado",
    "Link Maps",
    "Query",
)

DEFAULT_USER_AGENTS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
)


@dataclass
class ScrappingConfig:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    queries_file: Path = field(init=False)
    output_csv: Path = field(init=False)
    duplicates_csv: Path = field(init=False)
    max_workers: int = 4
    timeout_seconds: int = 12
    scroll_idle_retries: int = 7
    headless_feed: bool = False
    headless_workers: bool = True
    feed_scroll_pause_range: Tuple[float, float] = (0.8, 1.6)
    request_delay_range: Tuple[float, float] = (0.8, 2.0)
    place_load_delay_range: Tuple[float, float] = (1.4, 2.4)
    user_agents: Sequence[str] = field(default_factory=lambda: DEFAULT_USER_AGENTS)

    def __post_init__(self) -> None:
        self.queries_file = self.project_root / "queries" / "cervecerias_por_localidad.txt"
        self.output_csv = self.project_root / "output" / "caba_scrapping.csv"
        self.duplicates_csv = self.project_root / "output" / "duplicados.csv"

    def ensure_output_paths(self) -> None:
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        self.duplicates_csv.parent.mkdir(parents=True, exist_ok=True)
