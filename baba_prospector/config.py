import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_BASE = Path(__file__).parent


class Config:
    def __init__(self):
        self.telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "")
        self.sheets_id: str = os.getenv("GOOGLE_SHEETS_ID", "")
        self.credentials_json: str = os.getenv("GOOGLE_CREDENTIALS_JSON", "./credentials.json")

        yaml_path = _BASE / "config" / "fields.yaml"
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.fields: list[dict] = data["fields"]
        self.segments: dict = data["segments"]
        self.bar_states: list[dict] = data["bar_states"]
        self.bot: dict = data["bot"]

    # ── Field helpers ──────────────────────────────────────────────────────

    def get_fields_by_priority(self, priority: str) -> list[dict]:
        return [f for f in self.fields if f["priority"] == priority]

    def get_fields_ordered_by_ask_priority(self) -> list[dict]:
        """Returns fields that have ask_priority, sorted ascending."""
        fields_with_ask = [f for f in self.fields if "ask_priority" in f]
        return sorted(fields_with_ask, key=lambda f: f["ask_priority"])

    # ── Segment helpers ────────────────────────────────────────────────────

    def get_segment_for_brand(self, brand_name: str) -> str | None:
        """Returns segment key for an exact brand name, or None."""
        brand_lower = brand_name.strip().lower()
        for seg_key, seg_data in self.segments.items():
            if any(b.lower() == brand_lower for b in seg_data.get("brands", [])):
                return seg_key
        return None

    def get_all_brand_aliases(self) -> dict[str, str]:
        """Returns {brand_name_lower: segment_key} for fast lookup."""
        result: dict[str, str] = {}
        for seg_key, seg_data in self.segments.items():
            for brand in seg_data.get("brands", []):
                result[brand.lower()] = seg_key
        return result

    def infer_segment_from_text(self, text: str) -> str | None:
        """Scans free text for known brand names and returns the inferred segment."""
        if not text:
            return None
        text_lower = text.lower()
        brand_map = self.get_all_brand_aliases()
        found_segments: set[str] = set()
        for brand_lower, seg_key in brand_map.items():
            if brand_lower in text_lower:
                found_segments.add(seg_key)
        if not found_segments:
            return None
        if len(found_segments) == 1:
            return found_segments.pop()
        return "mixto"


# Singleton — imported by all modules
config = Config()
