"""Fetch TerraClimate water-balance features for VinhaGuard locations.

This step enriches the weather-only dataset with monthly drought physiology
signals from TerraClimate: vapor pressure deficit, climate water deficit,
soil moisture, and precipitation.

The script reads only the nearest TerraClimate grid cell for each project
location through the THREDDS OPeNDAP service. It does not download global
NetCDF files.

Run from the repository root:
    python -m src.data.fetch_terraclimate
"""

from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCATIONS_PATH = REPO_ROOT / "data" / "locations.csv"
BASE_DATASET_PATH = REPO_ROOT / "data" / "processed" / "vinhaguard_dataset.csv"
RAW_OUT = REPO_ROOT / "data" / "raw" / "terraclimate" / "terraclimate_monthly_points.parquet"
TASK_CACHE_DIR = REPO_ROOT / "data" / "raw" / "terraclimate" / "by_variable_year"
FEATURE_OUT_PARQUET = REPO_ROOT / "data" / "processed" / "terraclimate_features.parquet"
FEATURE_OUT_CSV = REPO_ROOT / "data" / "processed" / "terraclimate_features.csv"

START_YEAR = 1995
END_YEAR = 2024
MAX_WORKERS = 8

OPENDAP_URL = (
    "http://thredds.northwestknowledge.net:8080/thredds/dodsC/"
    "TERRACLIMATE_ALL/data/TerraClimate_{file_var}_{year}.nc"
)


@dataclass(frozen=True)
class TerraClimateVariable:
    file_var: str
    data_var: str
    prefix: str
    aggregation: str
    description: str


VARIABLES: tuple[TerraClimateVariable, ...] = (
    TerraClimateVariable("vpd", "vpd", "vpd", "mean", "vapor pressure deficit"),
    TerraClimateVariable("def", "def", "def", "sum", "climate water deficit"),
    TerraClimateVariable("soil", "soil", "soil", "min", "soil moisture"),
    TerraClimateVariable("ppt", "ppt", "ppt", "sum", "precipitation"),
)

OUTPUT_FEATURES = [
    "tc_vpd_summer_mean",
    "tc_vpd_growing_mean",
    "tc_def_summer_sum",
    "tc_def_growing_sum",
    "tc_soil_summer_min",
    "tc_soil_growing_min",
    "tc_ppt_summer_sum",
    "tc_ppt_growing_sum",
]


def _project_locations() -> pd.DataFrame:
    """Return the location rows used by the canonical project dataset."""
    locations = pd.read_csv(LOCATIONS_PATH)
    required = {"location_id", "subregion", "latitude", "longitude", "elevation_m"}
    missing = sorted(required.difference(locations.columns))
    if missing:
        raise ValueError(f"data/locations.csv is missing required columns: {missing}")

    if BASE_DATASET_PATH.exists():
        used_ids = pd.read_csv(BASE_DATASET_PATH, usecols=["location_id"])["location_id"].unique()
        locations = locations[locations["location_id"].isin(used_ids)].copy()
    else:
        raw_weather = REPO_ROOT / "data" / "raw" / "weather"
        available = {p.stem for p in raw_weather.glob("*.parquet")}
        if available:
            locations = locations[locations["location_id"].isin(available)].copy()

    if locations.empty:
        raise ValueError("No project locations available for TerraClimate extraction.")

    return locations.sort_values("location_id").reset_index(drop=True)


def _open_variable_year(var: TerraClimateVariable, year: int) -> xr.Dataset:
    url = OPENDAP_URL.format(file_var=var.file_var, year=year)
    return xr.open_dataset(url, engine="netcdf4")


def _task_cache_path(var: TerraClimateVariable, year: int) -> Path:
    return TASK_CACHE_DIR / f"{var.prefix}_{year}.parquet"


def _extract_monthly_for_variable(
    var: TerraClimateVariable,
    year: int,
    locations: pd.DataFrame,
    force: bool = False,
) -> pd.DataFrame:
    cache_path = _task_cache_path(var, year)
    if cache_path.exists() and not force:
        return pd.read_parquet(cache_path)

    ds = _open_variable_year(var, year)
    try:
        rows: list[dict] = []
        for loc in locations.itertuples(index=False):
            values = ds[var.data_var].sel(
                lat=float(loc.latitude),
                lon=float(loc.longitude),
                method="nearest",
            )
            nearest_lat = float(values["lat"].item())
            nearest_lon = float(values["lon"].item())
            for time_value, value in zip(values["time"].to_numpy(), values.to_numpy(), strict=True):
                timestamp = pd.Timestamp(time_value)
                rows.append(
                    {
                        "location_id": loc.location_id,
                        "year": int(timestamp.year),
                        "month": int(timestamp.month),
                        "variable": var.prefix,
                        "value": float(value) if pd.notna(value) else np.nan,
                        "tc_grid_lat": nearest_lat,
                        "tc_grid_lon": nearest_lon,
                    }
                )
        out = pd.DataFrame(rows)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_parquet(cache_path, index=False)
        return out
    finally:
        ds.close()


def fetch_monthly(
    variables: Iterable[TerraClimateVariable] = VARIABLES,
    years: Iterable[int] = range(START_YEAR, END_YEAR + 1),
    force: bool = False,
) -> pd.DataFrame:
    if RAW_OUT.exists() and not force:
        return pd.read_parquet(RAW_OUT)

    locations = _project_locations()
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    TASK_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    tasks = [(var, year) for var in variables for year in years]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_extract_monthly_for_variable, var, year, locations, force): (var, year)
            for var, year in tasks
        }
        with tqdm(total=len(futures), desc="Fetching TerraClimate", unit="file") as pbar:
            for future in as_completed(futures):
                var, year = futures[future]
                try:
                    frames.append(future.result())
                except Exception as exc:
                    raise RuntimeError(f"TerraClimate fetch failed for {var.prefix} {year}") from exc
                pbar.set_postfix(variable=var.prefix, year=year)
                pbar.update(1)

    monthly = pd.concat(frames, ignore_index=True)
    monthly = monthly.sort_values(["location_id", "year", "month", "variable"]).reset_index(drop=True)
    monthly.to_parquet(RAW_OUT, index=False)
    return monthly


def build_features(monthly: pd.DataFrame) -> pd.DataFrame:
    wide = monthly.pivot_table(
        index=["location_id", "year", "month"],
        columns="variable",
        values="value",
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None

    rows: list[dict] = []
    for (location_id, year), group in wide.groupby(["location_id", "year"]):
        growing = group[group["month"].between(4, 10)]
        summer = group[group["month"].between(6, 8)]

        record = {
            "location_id": location_id,
            "year": int(year),
            "tc_vpd_summer_mean": summer["vpd"].mean(),
            "tc_vpd_growing_mean": growing["vpd"].mean(),
            "tc_def_summer_sum": summer["def"].sum(),
            "tc_def_growing_sum": growing["def"].sum(),
            "tc_soil_summer_min": summer["soil"].min(),
            "tc_soil_growing_min": growing["soil"].min(),
            "tc_ppt_summer_sum": summer["ppt"].sum(),
            "tc_ppt_growing_sum": growing["ppt"].sum(),
        }
        rows.append(record)

    features = pd.DataFrame(rows)
    features = features[["location_id", "year", *OUTPUT_FEATURES]]
    return features.sort_values(["location_id", "year"]).reset_index(drop=True)


def main() -> None:
    monthly = fetch_monthly()
    features = build_features(monthly)

    FEATURE_OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(FEATURE_OUT_PARQUET, index=False)
    features.to_csv(FEATURE_OUT_CSV, index=False)

    print(f"Saved monthly TerraClimate points: {RAW_OUT}")
    print(f"Saved features: {FEATURE_OUT_PARQUET}")
    print(f"Rows: {len(features):,}; locations: {features['location_id'].nunique()}; years: {features['year'].min()}-{features['year'].max()}")
    print("Missing values:", int(features[OUTPUT_FEATURES].isna().sum().sum()))
    print(features[OUTPUT_FEATURES].describe().round(2).T[["mean", "min", "max"]].to_string())


if __name__ == "__main__":
    main()
