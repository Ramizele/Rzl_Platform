from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping


def append_rows(
    output_csv: Path,
    *,
    rows: Iterable[Mapping[str, str]],
    fieldnames: tuple[str, ...],
) -> int:
    row_list = list(rows)
    if not row_list:
        return 0

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    file_has_content = output_csv.exists() and output_csv.stat().st_size > 0

    with output_csv.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        if not file_has_content:
            writer.writeheader()

        for row in row_list:
            normalized_row = {column: row.get(column, "") for column in fieldnames}
            writer.writerow(normalized_row)

    return len(row_list)
