"""Run the full pipeline end to end:  python src/run_all.py"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["01_load_to_sqlite.py", "02_sql_diagnostics.py", "03_rfm_kmeans.py",
         "04_holt_winters_forecast.py", "05_export_powerbi.py", "06_validate_results.py"]
for s in STEPS:
    print(f"\n{'=' * 70}\n>>> {s}\n{'=' * 70}")
    subprocess.run([sys.executable, str(HERE / s)], check=True, cwd=HERE)
print("\nPipeline complete. See outputs/ and powerbi/data/.")
