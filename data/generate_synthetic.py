"""
Run this script once to generate douro_climate.parquet from synthetic data.
Replace with Person 2's real dataset when available.

Expected schema:
    year        int   1990–2023
    subregion   str   one of six Douro sub-regions
    heat_days_38 int  number of days >= 38°C
    frost_days  int   number of frost days (< 0°C)
    ndvi        float normalised difference vegetation index
    label       int   1 = climate stress event, 0 = normal season
"""

import numpy as np
import pandas as pd

SUBREGIONS = [
    "Baixo Corgo",
    "Cima Corgo",
    "Douro Superior",
    "Pinhão",
    "Régua",
    "Vila Nova de Foz Côa",
]

YEARS = list(range(1990, 2024))

rng = np.random.default_rng(42)

rows = []
for sr in SUBREGIONS:
    for yr in YEARS:
        heat = int(rng.integers(0, 25))
        frost = int(rng.integers(0, 10))
        ndvi = round(float(rng.uniform(0.3, 0.8)), 3)
        label = 1 if heat >= 14 else 0
        rows.append(
            {
                "year": yr,
                "subregion": sr,
                "heat_days_38": heat,
                "frost_days": frost,
                "ndvi": ndvi,
                "label": label,
            }
        )

df = pd.DataFrame(rows)
out_path = "douro_climate.parquet"
df.to_parquet(out_path, index=False)
print(f"Saved {len(df)} rows to {out_path}")
