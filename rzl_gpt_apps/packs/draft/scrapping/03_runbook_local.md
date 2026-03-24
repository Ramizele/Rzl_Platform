# Runbook Local - Scrapping

## 1. Instalar dependencias

```powershell
cd plugins/apps/extensions/scrapping
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Ajustar queries

Editar:
- `queries/cervecerias_por_localidad.txt`

## 3. Ejecutar scraper

```powershell
python run_scrapping.py
```

Opciones utiles:

```powershell
python run_scrapping.py --max-workers 4 --headless-feed
python run_scrapping.py --queries-file queries/cervecerias_por_localidad.txt --output-csv output/caba_custom.csv
```

## 4. Agregar coordenadas

```powershell
python -m scrapping.coords --input output/caba_scrapping.csv
```

## 5. Salidas

- CSV principal: `output/caba_scrapping.csv`
- Duplicados: `output/duplicados.csv`
- CSV con coordenadas: `output/caba_scrapping_with_coords.csv`
