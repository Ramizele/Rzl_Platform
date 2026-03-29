"""
Google Sheets integration via gspread.

Column order is derived dynamically from config/fields.yaml so that
adding a new field only requires editing the YAML.

Sheet structure:
  Row 1: headers (field keys in YAML order, metadata fields last)
  Row 2+: bar data
"""

import logging
from datetime import datetime
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from config import config

logger = logging.getLogger(__name__)

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Internal helpers ───────────────────────────────────────────────────────────


def _get_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(config.credentials_json, scopes=_SCOPES)
    return gspread.authorize(creds)


def _get_headers() -> list[str]:
    """Non-metadata fields first (YAML order), then metadata fields."""
    regular = [f["key"] for f in config.fields if f["priority"] != "metadata"]
    metadata = [f["key"] for f in config.fields if f["priority"] == "metadata"]
    return regular + metadata


def _get_sheet() -> gspread.Worksheet:
    gc = _get_client()
    spreadsheet = gc.open_by_key(config.sheets_id)
    tab_name: str = config.bot.get("sheets_tab", "bares_prospectos")

    try:
        sheet = spreadsheet.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=50)
        logger.info(f"Created worksheet '{tab_name}'")

    _ensure_headers(sheet)
    return sheet


def _ensure_headers(sheet: gspread.Worksheet):
    """Write headers if row 1 is empty. Logs a warning if they don't match."""
    expected = _get_headers()
    existing = sheet.row_values(1)
    if not existing:
        sheet.append_row(expected, value_input_option="RAW")
        logger.info("Headers written to sheet.")
    elif existing != expected:
        logger.warning(
            "Sheet headers differ from fields.yaml. "
            "Consider updating the sheet manually or clearing row 1."
        )


def _row_from_bar(bar_data: dict[str, Any], headers: list[str]) -> list[str]:
    return [str(bar_data.get(h) or "") for h in headers]


# ── Public API ─────────────────────────────────────────────────────────────────


def append_bar(bar_data: dict[str, Any]) -> int:
    """
    Append a bar as a new row. Fills metadata fields automatically.
    Returns the 1-based row index of the new row.
    """
    bar_data = dict(bar_data)
    bar_data["id"] = str(int(datetime.now().timestamp()))
    bar_data["fecha_visita"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not bar_data.get("estado"):
        bar_data["estado"] = "prospecto"

    sheet = _get_sheet()
    headers = _get_headers()
    row = _row_from_bar(bar_data, headers)
    sheet.append_row(row, value_input_option="USER_ENTERED")
    return len(sheet.get_all_values())  # approximate — gspread has no direct row count return


def update_bar(row: int, bar_data: dict[str, Any]):
    """Overwrite an existing row (1-based index) with new bar data."""
    bar_data = dict(bar_data)
    if not bar_data.get("fecha_visita"):
        bar_data["fecha_visita"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not bar_data.get("estado"):
        bar_data["estado"] = "prospecto"

    sheet = _get_sheet()
    headers = _get_headers()
    row_values = _row_from_bar(bar_data, headers)
    end_col = chr(ord("A") + len(headers) - 1)
    sheet.update(f"A{row}:{end_col}{row}", [row_values])


def find_bar_by_name(name: str) -> int | None:
    """
    Case-insensitive search for a bar by name column.
    Returns 1-based row index (including header row), or None if not found.
    """
    sheet = _get_sheet()
    headers = _get_headers()
    if "nombre" not in headers:
        return None

    col_idx = headers.index("nombre")  # 0-based
    all_rows = sheet.get_all_values()
    name_lower = name.strip().lower()

    for row_idx, row in enumerate(all_rows[1:], start=2):  # skip header, 1-based
        if len(row) > col_idx and row[col_idx].strip().lower() == name_lower:
            return row_idx
    return None


def get_last_n_bars(n: int) -> list[dict[str, str]]:
    """Returns the last n bars as list of dicts (newest first)."""
    sheet = _get_sheet()
    headers = _get_headers()
    all_rows = sheet.get_all_values()
    data_rows = all_rows[1:]  # skip header row

    last_n = data_rows[-n:] if len(data_rows) >= n else data_rows
    result = []
    for row in reversed(last_n):
        d = {h: (row[i] if i < len(row) else "") for i, h in enumerate(headers)}
        result.append(d)
    return result
