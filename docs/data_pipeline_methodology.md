# VinhaGuard AI - Data Pipeline Methodology

## Overview

The data pipeline builds the canonical VinhaGuard ML dataset:

- `data/processed/vinhaguard_dataset.parquet`
- `data/processed/vinhaguard_dataset.csv`

The final dataset has 960 rows and 29 columns: one row per vineyard location and
year, covering 32 Douro locations over 30 years from 1995 to 2024.

## Pipeline Steps

```text
locations
  -> fetch_weather
  -> build_features
  -> fetch_terraclimate
  -> make_dataset
```

| Step | Script | Purpose |
|---|---|---|
| 1 | `src/data/locations.py` | Generates representative Douro vineyard locations with subregion, coordinates, and elevation |
| 2 | `src/data/fetch_weather.py` | Fetches daily Open-Meteo / ERA5 temperature and precipitation data |
| 3 | `src/data/build_features.py` | Aggregates daily weather into annual heat, frost, drought, and precipitation features |
| 4 | `src/data/fetch_terraclimate.py` | Adds TerraClimate water-balance features for drought physiology |
| 5 | `src/data/make_dataset.py` | Creates the climate-stress target and writes the final ML-ready dataset |

## Final Dataset

| Attribute | Value |
|---|---|
| Rows | 960 |
| Columns | 29 |
| Locations | 32 |
| Years | 1995-2024 |
| Target | `climate_stress_year` |
| Positive class share | 39.8% |
| Missing values in final dataset | 0 |

Main feature groups:

- identifiers: `location_id`, `year`;
- geography: subregion, elevation, latitude, longitude;
- heat: hot-day counts, summer temperatures, heatwave streaks;
- frost: spring frost counts and minimum spring temperature;
- drought/rainfall: precipitation totals, dry-day counts, max dry-spell length;
- TerraClimate: vapor pressure deficit, climate water deficit, soil moisture,
  and precipitation.

Full column definitions are in `docs/data_dictionary.md`.

## Target Variable

`climate_stress_year` is a binary climate-trigger proxy:

- `1` = climate stress year;
- `0` = normal year.

A location-year is labelled stress if any of the following is true:

- `heat_days_35` is at or above that location's 80th percentile;
- `spring_severe_frost_days` is at least 3;
- `max_consecutive_dry_days` is at or above that location's 80th percentile.

Per-location percentiles are deliberate. Douro Superior is naturally hotter and
drier than Baixo Corgo, so a global threshold would confuse normal regional
climate differences with actual anomalies. The current rule detects whether a
year is unusual for that specific vineyard location.

## Coverage and Limitations

Weather data was retrieved for 32 of 36 planned locations. Four locations
could not be fetched within the project timeline because of free-tier API rate
limits:

- CC03
- CC12
- DS05
- DS10

Subregion coverage remains balanced enough for the prototype:

- Baixo Corgo: 10 of 12 planned locations;
- Cima Corgo: 12 of 14 planned locations;
- Douro Superior: 8 of 10 planned locations.

The fetch script is resumable: re-running it skips existing raw weather files
and retries missing locations.

## Validation

The label rule was checked against documented Iberian climate years:

| Year | Stress rate | Known event |
|---|---:|---|
| 1999 | 3% | Mild/wet reference year |
| 2003 | 81% | European heatwave |
| 2005 | 94% | Severe Iberian drought |
| 2017 | 94% | Record heat and Portugal wildfires |
| 2022 | 100% | Exceptional Iberian heat and drought |
| 2024 | 94% | Near-record Douro season |

This validation supports the target as a reasonable climate-trigger proxy for an
academic prototype. It does not prove actual crop-loss prediction.

## Reproducibility

From the repository root:

```bash
python -m src.data.locations
python -m src.data.fetch_weather
python -m src.data.build_features
python -m src.data.fetch_terraclimate
python -m src.data.make_dataset
```

Raw and interim files are gitignored because they are large or regenerable.
Processed datasets used by the app and model are committed under
`data/processed/`.

