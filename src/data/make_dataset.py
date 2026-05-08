"""
Pipeline step 4 — label climate stress years and write the final ML dataset.

Reads:
    data/interim/features_by_location_year.parquet

Writes:
    data/processed/vinhaguard_dataset.parquet
    data/processed/vinhaguard_dataset.csv

The synthetic placeholder data/processed/douro_climate.parquet (used by the
Streamlit demo) is left untouched — new files are written alongside it.

Run:
    python -m src.data.make_dataset
"""

import pathlib

import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_INPUT = _REPO_ROOT / "data" / "interim" / "features_by_location_year.parquet"
_OUT_DIR = _REPO_ROOT / "data" / "processed"
_OUT_PARQUET = _OUT_DIR / "vinhaguard_dataset.parquet"
_OUT_CSV = _OUT_DIR / "vinhaguard_dataset.csv"


# ── Labelling ─────────────────────────────────────────────────────────────────
def label_stress_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add binary column ``climate_stress_year`` (1 = stress, 0 = normal) to df.

    A year is labelled **stress = 1** if ANY of the following holds:

        (a) heat_days_35 >= 80th percentile of that *location's own* historical
            heat_days_35 distribution
        (b) spring_severe_frost_days >= 3
        (c) max_consecutive_dry_days >= 80th percentile of that *location's own*
            historical max_consecutive_dry_days distribution

    **Why per-location percentiles, not global ones:**
    Douro Superior sits 8–12 °C hotter than Baixo Corgo in summer.  A global
    80th-percentile heat threshold would be set by the hottest sub-region and
    would label almost every Baixo Corgo year as normal, and almost every
    Douro Superior year as stressed — regardless of whether that year was
    anomalous *for that site*.  By computing thresholds within each location,
    the model learns relative climate anomalies (how unusual was this year for
    this vineyard) rather than absolute climate, which is the ecologically
    meaningful signal for parametric insurance trigger calibration.

    **Tuning:**
    All threshold logic lives in this single function.  Person 3 (ML Lead) can
    adjust the percentile cutoffs or add conditions here without touching the
    rest of the pipeline.
    """
    df = df.copy()

    # ── Per-location 80th-percentile thresholds via transform ─────────────────
    # transform broadcasts the per-group scalar back to every row in that group,
    # so the comparison df[col] >= threshold works row-wise without any merge.
    p80_heat = (
        df.groupby("location_id")["heat_days_35"]
        .transform(lambda x: x.quantile(0.80))
    )
    p80_dry = (
        df.groupby("location_id")["max_consecutive_dry_days"]
        .transform(lambda x: x.quantile(0.80))
    )

    cond_a = df["heat_days_35"] >= p80_heat                  # (a) anomalous heat
    cond_b = df["spring_severe_frost_days"] >= 3             # (b) spring frost event
    cond_c = df["max_consecutive_dry_days"] >= p80_dry       # (c) anomalous drought

    df["climate_stress_year"] = (cond_a | cond_b | cond_c).astype(int)
    return df


# ── Console summary ───────────────────────────────────────────────────────────
def _print_summary(df: pd.DataFrame) -> None:
    total = len(df)
    n_stress = int(df["climate_stress_year"].sum())
    pct_overall = 100 * n_stress / total

    print(f"\nTotal rows : {total:,}  ({df['location_id'].nunique()} locations × {df['year'].nunique()} years)")
    print(f"Stress = 1 : {n_stress:,}  ({pct_overall:.1f}% overall)")

    # ── By subregion ──────────────────────────────────────────────────────────
    print("\nPositive-class share by subregion:")
    print("─" * 46)
    by_sr = (
        df.groupby("subregion")["climate_stress_year"]
        .agg(n_stress="sum", n_total="count")
        .assign(pct=lambda x: (100 * x["n_stress"] / x["n_total"]).round(1))
    )
    print(by_sr.to_string())

    # ── Year-by-year stress count ─────────────────────────────────────────────
    print("\nYear-by-year stress count across all locations")
    print("(known hot/dry Iberian years: 2003, 2005, 2017, 2022 — expect elevated counts)")
    print("─" * 52)
    by_year = (
        df.groupby("year")["climate_stress_year"]
        .agg(n_stress="sum", n_locations="count")
        .assign(pct=lambda x: (100 * x["n_stress"] / x["n_locations"]).round(1))
        .rename(columns={"n_stress": "n_stress", "n_locations": "n_locs", "pct": "pct_%"})
    )
    print(by_year.to_string())


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    df = pd.read_parquet(_INPUT)
    print(f"Loaded {len(df):,} rows from {_INPUT.name}")

    df = label_stress_year(df)

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(_OUT_PARQUET, index=False)
    df.to_csv(_OUT_CSV, index=False)
    print(f"Saved → {_OUT_PARQUET.name}")
    print(f"Saved → {_OUT_CSV.name}")

    _print_summary(df)


if __name__ == "__main__":
    main()
