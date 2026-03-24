from __future__ import annotations

import argparse
import csv
from pathlib import Path


def extract_coordinates(link: str | None) -> tuple[float | None, float | None]:
    if not link:
        return None, None

    try:
        if "/@" in link:
            lat, lon = link.split("/@", 1)[1].split(",", 2)[:2]
            return float(lat), float(lon)

        if "maps?q=" in link:
            lat, lon = link.split("maps?q=", 1)[1].split(",", 2)[:2]
            return float(lat), float(lon)

        if "!3d" in link and "!4d" in link:
            lat = link.split("!3d", 1)[1].split("!", 1)[0]
            lon = link.split("!4d", 1)[1].split("!", 1)[0]
            return float(lat), float(lon)
    except (ValueError, IndexError):
        return None, None

    return None, None


def add_coordinates_to_csv(
    input_csv: Path,
    output_csv: Path | None = None,
    *,
    link_column: str = "Link Maps",
) -> Path:
    if output_csv is None:
        output_csv = input_csv.with_name(f"{input_csv.stem}_with_coords.csv")

    with input_csv.open("r", newline="", encoding="utf-8") as in_handle:
        reader = csv.DictReader(in_handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV without header: {input_csv}")

        fieldnames = list(reader.fieldnames)
        if "Latitud" not in fieldnames:
            fieldnames.append("Latitud")
        if "Longitud" not in fieldnames:
            fieldnames.append("Longitud")

        rows = []
        for row in reader:
            lat, lon = extract_coordinates(row.get(link_column))
            row["Latitud"] = "" if lat is None else str(lat)
            row["Longitud"] = "" if lon is None else str(lon)
            rows.append(row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as out_handle:
        writer = csv.DictWriter(out_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return output_csv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add lat/lon columns from Google Maps links.")
    parser.add_argument("--input", required=True, type=Path, help="Path to source CSV.")
    parser.add_argument("--output", type=Path, help="Path to output CSV.")
    parser.add_argument(
        "--link-column",
        default="Link Maps",
        help="CSV column that stores Google Maps links (default: Link Maps).",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    output_csv = add_coordinates_to_csv(args.input, args.output, link_column=args.link_column)
    print(f"Coordinates saved to: {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
