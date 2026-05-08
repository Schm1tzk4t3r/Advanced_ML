"""
Pipeline step 2 — fetch daily weather from the Open-Meteo Historical Weather API.

Reads data/locations.csv (36 Douro sites) and downloads daily weather for the
period 1995-01-01 → 2024-12-31, saving one Parquet file per location at:
    data/raw/weather/{location_id}.parquet

Output columns:
    date       datetime64[ns]   calendar date
    tmax       float64          daily max temperature 2 m (°C)
    tmin       float64          daily min temperature 2 m (°C)
    tmean      float64          daily mean temperature 2 m (°C)
    precip_mm  float64          daily precipitation sum (mm)

Behaviour:
    - Skips locations whose Parquet already exists (resumable).
    - Retries up to 3 times on HTTP 429 / 5xx with exponential backoff
      (2 s, 4 s, 8 s).
    - Sleeps 1.2 s between location requests (free-tier rate limit).
    - Logs progress to stdout and data/raw/weather/_fetch.log.

Run:
    python -m src.data.fetch_weather
"""

import logging
import pathlib
import time
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_LOCATIONS_CSV = _REPO_ROOT / "data" / "locations.csv"
RAW_DIR = _REPO_ROOT / "data" / "raw" / "weather"
_LOG_FILE = RAW_DIR / "_fetch.log"

# ── API constants ─────────────────────────────────────────────────────────────
START_DATE = "1995-01-01"
END_DATE = "2024-12-31"
API_URL = "https://archive-api.open-meteo.com/v1/archive"
SLEEP_BETWEEN = 20.0         # seconds between location requests (free-tier: ~3 req/min max)
MAX_RETRIES = 3
BACKOFF_SECONDS = [2, 4, 8]  # sleep before retry 1, 2, 3

_DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
]


# ── Logging ───────────────────────────────────────────────────────────────────
class _TqdmHandler(logging.StreamHandler):
    """Route log lines through tqdm.write so they don't clobber the progress bar."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            tqdm.write(self.format(record))
        except Exception:
            self.handleError(record)


def _setup_logger() -> logging.Logger:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("fetch_weather")
    if logger.handlers:
        return logger  # idempotent — don't add duplicate handlers
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    for handler in (_TqdmHandler(), logging.FileHandler(_LOG_FILE)):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


# ── HTTP with retry ───────────────────────────────────────────────────────────
def _call_api(lat: float, lon: float, logger: logging.Logger) -> dict[str, Any]:
    params = [
        ("latitude", lat),
        ("longitude", lon),
        ("start_date", START_DATE),
        ("end_date", END_DATE),
        ("timezone", "Europe/Lisbon"),
    ] + [("daily", v) for v in _DAILY_VARS]

    for attempt in range(MAX_RETRIES + 1):  # attempts 0–3
        try:
            resp = requests.get(API_URL, params=params, timeout=30)
        except requests.RequestException as exc:
            if attempt < MAX_RETRIES:
                wait = BACKOFF_SECONDS[attempt]
                logger.warning(f"Connection error (attempt {attempt + 1}): {exc} — retry in {wait}s")
                time.sleep(wait)
                continue
            raise

        if resp.status_code == 200:
            payload = resp.json()
            if payload.get("error"):
                raise ValueError(f"API error: {payload.get('reason', payload)}")
            return payload

        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt < MAX_RETRIES:
                wait = BACKOFF_SECONDS[attempt]
                logger.warning(
                    f"HTTP {resp.status_code} (attempt {attempt + 1}/{MAX_RETRIES + 1})"
                    f" — retry in {wait}s"
                )
                time.sleep(wait)
                continue

        resp.raise_for_status()

    raise RuntimeError("All retries exhausted")  # unreachable, but satisfies type checkers


# ── Parse API response ────────────────────────────────────────────────────────
def _parse(payload: dict[str, Any]) -> pd.DataFrame:
    daily = payload["daily"]
    return pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]),
            "tmax": pd.to_numeric(daily["temperature_2m_max"], errors="coerce"),
            "tmin": pd.to_numeric(daily["temperature_2m_min"], errors="coerce"),
            "tmean": pd.to_numeric(daily["temperature_2m_mean"], errors="coerce"),
            "precip_mm": pd.to_numeric(daily["precipitation_sum"], errors="coerce"),
        }
    )[["date", "tmax", "tmin", "tmean", "precip_mm"]]


# ── Summary helpers ───────────────────────────────────────────────────────────
def _summarize_file(loc_id: str, path: pathlib.Path) -> dict:
    df = pd.read_parquet(path)
    return {
        "location_id": loc_id,
        "n_days": len(df),
        "n_missing_tmax": int(df["tmax"].isna().sum()),
        "n_missing_precip": int(df["precip_mm"].isna().sum()),
        "date_range": f"{df['date'].min().date()} → {df['date'].max().date()}",
    }


def _print_summary(summary: pd.DataFrame) -> None:
    print("\n" + "─" * 76)
    print("FETCH SUMMARY")
    print("─" * 76)
    print(summary.to_string(index=False))
    n_ok = (summary["date_range"] != "ERROR").sum()
    print(f"\n{n_ok}/{len(summary)} locations OK")
    if n_ok < len(summary):
        failed = summary.loc[summary["date_range"] == "ERROR", "location_id"].tolist()
        print(f"Failed: {', '.join(failed)}")
    print("─" * 76)


# ── Main fetch loop ───────────────────────────────────────────────────────────
def fetch_all(logger: logging.Logger | None = None) -> pd.DataFrame:
    logger = logger or _setup_logger()
    locations = pd.read_csv(_LOCATIONS_CSV)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    summary: list[dict] = []
    first_fetch = True

    with tqdm(total=len(locations), unit="loc", desc="Fetching weather") as pbar:
        for _, row in locations.iterrows():
            loc_id: str = row["location_id"]
            out_path = RAW_DIR / f"{loc_id}.parquet"
            pbar.set_postfix(loc=loc_id)

            if out_path.exists():
                logger.info(f"{loc_id}: already exists — skipping")
                summary.append(_summarize_file(loc_id, out_path))
                pbar.update(1)
                continue

            if not first_fetch:
                time.sleep(SLEEP_BETWEEN)
            first_fetch = False

            logger.info(f"{loc_id}: fetching '{row['name']}'")
            try:
                payload = _call_api(float(row["latitude"]), float(row["longitude"]), logger)
                df = _parse(payload)
                df.to_parquet(out_path, index=False)
                logger.info(
                    f"{loc_id}: saved {len(df)} rows"
                    f" (missing tmax={df['tmax'].isna().sum()}"
                    f", precip={df['precip_mm'].isna().sum()})"
                )
                summary.append(_summarize_file(loc_id, out_path))
            except Exception as exc:
                logger.error(f"{loc_id}: FAILED — {exc}")
                summary.append(
                    {
                        "location_id": loc_id,
                        "n_days": 0,
                        "n_missing_tmax": -1,
                        "n_missing_precip": -1,
                        "date_range": "ERROR",
                    }
                )

            pbar.update(1)

    return pd.DataFrame(summary)


def main() -> None:
    logger = _setup_logger()
    n_locations = len(pd.read_csv(_LOCATIONS_CSV))
    logger.info(f"Starting fetch — {n_locations} locations, {START_DATE} → {END_DATE}")
    summary = fetch_all(logger)
    _print_summary(summary)
    logger.info("Fetch complete")


if __name__ == "__main__":
    main()
