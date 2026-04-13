"""
Builds the LLM extraction prompt dynamically from config/fields.yaml.

The prompt is regenerated each call so it always reflects the current YAML
without requiring a process restart.
"""

import json

from config import config


def build_extraction_prompt(
    transcription: str, ruta_paradas: list[dict] | None = None
) -> str:
    parts = [
        _HEADER,
        _build_aliases_section(),
        "\n\n",
        _build_segments_section(),
    ]
    if ruta_paradas:
        parts.append("\n\n")
        parts.append(_build_ruta_section(ruta_paradas))
    parts.append("\n\nJSON a completar:\n")
    parts.append(_build_json_schema())
    parts.append("\n\nTexto transcripto:\n")
    parts.append(f'"{transcription}"')
    return "".join(parts)


# ── Static header ──────────────────────────────────────────────────────────────

_HEADER = """\
Sos un asistente de campo para Baba Cervecería, una cervecería artesanal argentina.
Extraé la información del siguiente texto sobre un bar visitado.
Devolvé SOLO un JSON válido con la estructura exacta de abajo.
Usá null para campos no mencionados. No agregues texto fuera del JSON.

El texto está en español rioplatense. Interpretá el lenguaje informal con criterio:
- "chopera", "tirador", "grifo", "canilla" → formato_venta: "Tirada"
- "lata", "latas" → formato_venta: "Lata"
- Precios en ARS: "$3000 la pinta" → precio_pinta: 3000
- "el encargado", "el chabón", "el dueño" → contacto_cargo: "encargado"
- Emociones/actitud: "re copado", "buena onda" → interes_encargado: "receptivo"

"""

# ── Dynamic sections ───────────────────────────────────────────────────────────


def _build_aliases_section() -> str:
    lines = ["Aliases adicionales a reconocer:"]
    found_any = False
    for field in config.fields:
        aliases = field.get("aliases")
        if not aliases:
            continue
        found_any = True
        lines.append(f"  Campo '{field['key']}' ({field['label']}):")
        for value, exprs in aliases.items():
            expr_list = ", ".join(f'"{e}"' for e in exprs)
            lines.append(f"    Si escuchás {expr_list} → \"{value}\"")
    return "\n".join(lines) if found_any else ""


def _build_segments_section() -> str:
    lines = ["Segmentos de birra — inferí según las marcas mencionadas:"]
    for seg_key, seg_data in config.segments.items():
        brands = seg_data.get("brands", [])
        brand_str = ", ".join(brands) if brands else "(se asigna automáticamente)"
        lines.append(f"  {seg_key} ({seg_data['label']}): {brand_str}")
    lines.append("  → Si hay marcas de más de un segmento → segmento_inferido: \"mixto\"")
    lines.append("  → Si no se mencionan marcas → segmento_inferido: null")
    return "\n".join(lines)


def _build_ruta_section(paradas: list[dict]) -> str:
    lines = [
        "Ruta activa del vendedor — paradas disponibles:",
        "Si el vendedor menciona uno de estos lugares (por nombre completo, apodo o referencia parcial),",
        "identificá cuál es y completá nombre, direccion y barrio automáticamente con los valores exactos de abajo.",
        "Si no hay referencia clara a ninguna parada, dejá esos campos en null.",
        "",
    ]
    for i, p in enumerate(paradas, 1):
        lines.append(
            f'  {i}. nombre: "{p["nombre"]}" | '
            f'direccion: "{p.get("direccion", "")}" | '
            f'barrio: "{p.get("barrio", "")}"'
        )
    return "\n".join(lines)


def _build_json_schema() -> str:
    """Build the JSON schema comment from fields, excluding metadata fields."""
    schema: dict[str, str] = {}
    for field in config.fields:
        if field["priority"] == "metadata":
            continue
        ftype = field.get("type", "string")
        options = field.get("options")
        if options:
            opts = " | ".join(f'"{o}"' for o in options)
            schema[field["key"]] = f"{opts} | null"
        elif ftype == "integer":
            schema[field["key"]] = "integer | null"
        elif ftype == "boolean":
            schema[field["key"]] = "true | false | null"
        else:
            schema[field["key"]] = "string | null"
    return json.dumps(schema, ensure_ascii=False, indent=2)
