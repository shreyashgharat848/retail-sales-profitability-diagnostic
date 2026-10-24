"""Shared paths and constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "Superstore.csv"
DB_PATH = ROOT / "data" / "superstore.db"
SQL_DIR = ROOT / "sql"
CHARTS = ROOT / "outputs" / "charts"
TABLES = ROOT / "outputs" / "tables"
POWERBI = ROOT / "powerbi" / "data"

for p in (CHARTS, TABLES, POWERBI):
    p.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
N_CLUSTERS = 4          # number of RFM segments
FORECAST_MONTHS = 12    # 12 months = 4 quarters

# consistent chart colours
GREEN, RED, BLUE, GREY, ORANGE = "#2E7D32", "#C62828", "#1565C0", "#757575", "#EF6C00"
