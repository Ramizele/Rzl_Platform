"""
Parsea links de Google Maps (rutas con múltiples paradas).

Input:  URL string (puede ser link corto maps.app.goo.gl o link largo)
Output: lista de dicts [{"nombre": str, "direccion": str, "barrio": str | None}, ...]

La primera parada se ignora (es el punto de partida del vendedor).
"""

import re
import urllib.parse
import urllib.request


def expand_short_url(url: str) -> str:
    """Sigue el redirect de maps.app.goo.gl y devuelve la URL larga."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.url


def parse_route_url(url: str) -> list[dict]:
    """
    Parsea una URL de Google Maps con múltiples paradas.
    Devuelve lista de paradas (sin la primera — punto de partida del vendedor).
    Lanza ValueError si la URL no es una ruta válida (< 2 paradas o sin /maps/dir/).
    """
    if "maps.app.goo.gl" in url:
        url = expand_short_url(url)

    match = re.search(r"/maps/dir/([^@?#]+)", url)
    if not match:
        raise ValueError("No es una URL de ruta de Google Maps")

    raw_stops = match.group(1).strip("/").split("/")

    if len(raw_stops) < 2:
        raise ValueError("La ruta tiene menos de 2 paradas")

    # Ignorar la primera parada (punto de partida del vendedor)
    stops = raw_stops[1:]

    result = []
    for stop in stops:
        if not stop:
            continue
        decoded = urllib.parse.unquote_plus(stop)
        parts = decoded.split(",", 1)
        nombre = parts[0].strip()
        direccion_raw = parts[1].strip() if len(parts) > 1 else ""

        barrio = _extract_barrio(decoded)
        direccion = _clean_direccion(direccion_raw)

        result.append({
            "nombre": nombre,
            "direccion": direccion,
            "barrio": barrio,
        })

    return result


_BARRIOS = [
    "Palermo", "Villa Crespo", "Chacarita", "Colegiales", "Almagro",
    "Caballito", "Flores", "San Telmo", "La Boca", "Recoleta",
    "Belgrano", "Núñez", "Saavedra", "Villa Urquiza", "Villa del Parque",
    "Balvanera", "Once", "Abasto", "Boedo", "Parque Patricios",
    "Barracas", "Nueva Pompeya", "Mataderos", "Liniers", "Versalles",
    "Monte Castro", "Villa Real", "Floresta", "Vélez Sársfield",
    "Villa Luro", "Parque Avellaneda", "Parque Chacabuco", "Villa Lugano",
    "Villa Soldati", "Villa Riachuelo", "Monserrat", "San Nicolás",
    "Retiro", "San Cristóbal", "Constitución", "Puerto Madero",
    "Olivos", "Vicente López", "San Isidro", "Martínez", "Tigre",
    "San Martín", "Ramos Mejía", "Lanús", "Avellaneda",
]


def _extract_barrio(text: str) -> str | None:
    text_lower = text.lower()
    for barrio in _BARRIOS:
        if barrio.lower() in text_lower:
            return barrio
    return None


def _clean_direccion(raw: str) -> str:
    """Limpia la dirección removiendo texto redundante de Argentina."""
    clean = re.sub(r"\bC\d{4}\b.*", "", raw)
    clean = re.sub(r"Cdad\.?\s*Aut[oó]noma\s*de\s*Buenos\s*Aires", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"Ciudad\s*Aut[oó]noma\s*de\s*Buenos\s*Aires", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"Buenos\s*Aires,?\s*Argentina", "", clean, flags=re.IGNORECASE)
    return clean.strip(" ,")
