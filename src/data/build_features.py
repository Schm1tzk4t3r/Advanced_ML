"""
Pipeline step 3 — engineer per-location-year climate features from daily weather.

Reads:
    data/raw/weather/{location_id}.parquet   (one file per location)
    data/locations.csv                       (subregion / elevation metadata)

Writes:
    data/interim/features_by_location_year.parquet

Only locations with weather_data_available=True in locations.csv are processed.
Locations missing a parquet file are silently skipped.

Quality control: location-year rows with fewer than 90% of expected daily
observations are dropped before output.

Run:
    python -m src.data.build_features
"""

import calendar
import pathlib

import pandas as pd
from tqdm import tqdm

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_LOCATIONS_CSV = _REPO_ROOT / "data" / "locations.csv"
_RAW_DIR = _REPO_ROOT / "data" / "raw" / "weather"
_INTERIM_DIR = _REPO_ROOT / "data" / "interim"
OUTPUT_PATH = _INTERIM_DIR / "features_by_location_year.parquet"

_OUTPUT_COLS = [
    "location_id", "year", "subregion", "elevation_m", "latitude", "longitude",
    # heat
    "heat_days_30", "heat_days_35", "heat_days_38",
    "max_summer_tmax", "mean_summer_tmax", "heatwave_max_streak",
    "gdd_growing_season",
    # spring frost
    "spring_frost_days", "spring_severe_frost_days", "min_spring_tmin",
    # drought / rainfall
    "annual_precip_mm", "summer_precip_mm", "dry_days", "max_consecutive_dry_days",
]


# ── Feature helpers ───────────────────────────────────────────────────────────
def _max_streak(mask: pd.Series) -> int:
    """Longest run of consecutive True values in a boolean Series."""
    if not mask.any():
        return 0
    groups = mask.ne(mask.shift()).cumsum()
    return int(mask.groupby(groups).sum().max())


def _year_features(df: pd.DataFrame, year: int) -> dict | None:
    """
    Compute all features for one (location, year) slice.
    Returns None if the year has fewer than 90% valid daily observations.
    """
    days_expected = 366 if calendar.isleap(year) else 365
    n_valid = int(df["tmax"].notna().sum())
    if n_valid < int(0.9 * days_expected):
        return None

    month = df["date"].dt.month
    summer = df[month.isin([6, 7, 8])]
    spring = df[month.isin([3, 4, 5])]
    growing = df[month.between(4, 10)]

    return {
        # ── Heat ──────────────────────────────────────────────────────────────
        "heat_days_30": int((df["tmax"] >= 30).sum()),
        "heat_days_35": int((df["tmax"] >= 35).sum()),
        "heat_days_38": int((df["tmax"] >= 38).sum()),
        "max_summer_tmax": float(summer["tmax"].max()),
        "mean_summer_tmax": float(summer["tmax"].mean()),
        "heatwave_max_streak": _max_streak(df["tmax"] >= 35),
        "gdd_growing_season": float(growing["tmean"].sub(10).clip(lower=0).sum()),
        # ── Spring frost (March–May) ───────────────────────────────────────────
        "spring_frost_days": int((spring["tmin"] < 0).sum()),
        "spring_severe_frost_days": int((spring["tmin"] < -2).sum()),
        "min_spring_tmin": float(spring["tmin"].min()),
        # ── Drought / rainfall ────────────────────────────────────────────────
        "annual_precip_mm": float(df["precip_mm"].sum()),
        "summer_precip_mm": float(summer["precip_mm"].sum()),
        "dry_days": int((df["precip_mm"] < 1).sum()),
        "max_consecutive_dry_days": _max_streak(df["precip_mm"] < 1),
    }


# ── Main build ────────────────────────────────────────────────────────────────
def build_features() -> pd.DataFrame:
    locations = pd.read_csv(_LOCATIONS_CSV)
    # Coerce the bool column robustly (CSV stores "True"/"False" strings)
    locations["weather_data_available"] = (
        locations["weather_data_available"].astype(str).str.strip().str.lower() == "true"
    )
    available = locations[locations["weather_data_available"]].reset_index(drop=True)

    _INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    dropped: list[str] = []

    with tqdm(total=len(available), unit="loc", desc="Building features") as pbar:
        for _, loc in available.iterrows():
            loc_id: str = loc["location_id"]
            parquet_path = _RAW_DIR / f"{loc_id}.parquet"
            pbar.set_postfix(loc=loc_id)

            if not parquet_path.exists():
                pbar.update(1)
                continue

            df = pd.read_parquet(parquet_path)
            df["date"] = pd.to_datetime(df["date"])

            for year, df_year in df.groupby(df["date"].dt.year):
                feats = _year_features(df_year.copy(), int(year))
                if feats is None:
                    n_valid = int(df_year["tmax"].notna().sum())
                    days_expected = 366 if calendar.isleap(int(year)) else 365
                    dropped.append(
                        f"{loc_id}/{year}  ({n_valid}/{days_expected} valid days)"
                    )
                    continue

                rows.append(
                    {
                        "location_id": loc_id,
                        "year": int(year),
                        "subregion": loc["subregion"],
                        "elevation_m": int(loc["elevation_m"]),
                        "latitude": float(loc["latitude"]),
                        "longitude": float(loc["longitude"]),
                        **feats,
                    }
                )

            pbar.update(1)

    # ── QC report ──────────────────────────────────────────────────────────────
    if dropped:
        print(f"\nQC: dropped {len(dropped)} location-year rows (< 90% daily completeness):")
        for d in dropped:
            print(f"  {d}")
    else:
        print("\nQC: 0 rows dropped — all location-years ≥ 90% complete.")

    out = (
        pd.DataFrame(rows, columns=_OUTPUT_COLS)
        .sort_values(["location_id", "year"])
        .reset_index(drop=True)
    )
    return out


# ── Summary / sanity check ────────────────────────────────────────────────────
def _print_summary(df: pd.DataFrame) -> None:
    print("\nSubregion summary (means across all location-years):")
    print("─" * 66)
    summary = (
        df.groupby("subregion")
        .agg(
            loc_years=("year", "count"),
            heat_days_35=("heat_days_35", "mean"),
            spring_frost_days=("spring_frost_days", "mean"),
            annual_precip_mm=("annual_precip_mm", "mean"),
        )
        .round(1)
    )
    print(summary.to_string())

    print("\nHeat-days-35 ranking (expected: Douro Superior > Cima Corgo > Baixo Corgo):")
    ranking = summary["heat_days_35"].sort_values(ascending=False)
    for subregion, val in ranking.items():
        print(f"  {subregion}: {val:.1f} days")

    ds_heat = summary.loc["Douro Superior", "heat_days_35"] if "Douro Superior" in summary.index else None
    bc_heat = summary.loc["Baixo Corgo", "heat_days_35"] if "Baixo Corgo" in summary.index else None
    if ds_heat is not None and bc_heat is not None:
        if ds_heat > bc_heat:
            print("  Sanity check PASSED — Douro Superior hotter than Baixo Corgo.")
        else:
            print("  WARNING — unexpected ranking; inspect data.")


def main() -> None:
    print(f"Input:  {_RAW_DIR}")
    print(f"Output: {OUTPUT_PATH}")
    df = build_features()
    df.to_parquet(OUTPUT_PATH, index=False)
    n_loc = df["location_id"].nunique()
    n_yr = df["year"].nunique()
    print(f"\nSaved {len(df):,} rows × {len(df.columns)} columns ({n_loc} locations × {n_yr} years)")
    print(f"Years: {df['year'].min()} – {df['year'].max()}")
    _print_summary(df)


if __name__ == "__main__":
    main()
