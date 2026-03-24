# Scrapping Extension

Proyecto Python modular para scraping de bares en CABA desde Google Maps.

## Estructura

- `run_scrapping.py`: entrypoint local.
- `queries/cervecerias_por_localidad.txt`: consultas por barrio.
- `src/scrapping/`: modulos de scraping.
- `output/`: archivos de salida CSV.

## Setup rapido

```powershell
cd plugins/apps/extensions/scrapping
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar

```powershell
python run_scrapping.py
```

Flags utiles:

```powershell
python run_scrapping.py --max-workers 4 --headless-feed
python run_scrapping.py --visible-workers
python run_scrapping.py --queries-file queries/cervecerias_por_localidad.txt --output-csv output/caba_custom.csv
```

## Agregar coordenadas

```powershell
python -m scrapping.coords --input output/caba_scrapping.csv
```

## Notas

- El scraper limita concurrencia a 4 workers por defecto para reducir bloqueos.
- La deduplicacion se hace por `Nombre + Direccion` normalizados.
- Si cambian selectores de Maps, ajustar `src/scrapping/scraper_place.py`.
