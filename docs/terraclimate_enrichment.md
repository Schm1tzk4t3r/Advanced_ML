# TerraClimate Enrichment - What Changed

## Why We Added It

The original ML dataset used daily weather-derived features only: heat days,
frost days, rainfall totals, and dry-spell length. That is useful for a
parametric insurance prototype, but it makes drought stress depend heavily on
rainfall assumptions.

TerraClimate adds monthly water-balance variables that are closer to how vines
actually experience stress:

- vapor pressure deficit (`vpd`) = atmospheric drying demand;
- climate water deficit (`def`) = unmet evaporative demand;
- soil moisture (`soil`) = grid-cell soil water availability;
- precipitation (`ppt`) = independent monthly precipitation source.

This strengthens the ML story for the course: VinhaGuard now combines weather
thresholds, drought physiology, geography, and historical trigger behaviour
instead of only counting hot or dry days.

## Data Source

Source: TerraClimate, accessed through the University of Idaho/Northwest
Knowledge Network THREDDS OPeNDAP service.

Citation:

Abatzoglou, J. T., Dobrowski, S. Z., Parks, S. A., & Hegewisch, K. C. (2018).
TerraClimate, a high-resolution global dataset of monthly climate and climatic
water balance from 1958-2015. *Scientific Data*, 5, 170191.
https://doi.org/10.1038/sdata.2017.191

Project URLs:

- Dataset overview: https://www.climatologylab.org/terraclimate.html
- Variables: https://www.climatologylab.org/terraclimate-variables.html
- THREDDS archive: http://thredds.northwestknowledge.net:8080/thredds/catalog/TERRACLIMATE_ALL/data/catalog.html

## Implementation

New script:

```bash
python -m src.data.fetch_terraclimate
```

The script:

1. Reads the 32 location IDs used in `data/processed/vinhaguard_dataset.csv`.
2. Opens TerraClimate variable-year files remotely through OPeNDAP.
3. Extracts the nearest TerraClimate grid cell for each vineyard location.
4. Caches each variable-year extraction under `data/raw/terraclimate/by_variable_year/`.
5. Writes monthly point data to `data/raw/terraclimate/terraclimate_monthly_points.parquet`.
6. Aggregates monthly values into annual ML features.
7. Writes `data/processed/terraclimate_features.parquet` and `.csv`.

New dependencies:

- `xarray`
- `netCDF4`

## Features Added

The final ML dataset now includes 8 TerraClimate features:

| Feature | Meaning |
|---|---|
| `tc_vpd_summer_mean` | Mean vapor pressure deficit, June-August |
| `tc_vpd_growing_mean` | Mean vapor pressure deficit, April-October |
| `tc_def_summer_sum` | Climate water deficit sum, June-August |
| `tc_def_growing_sum` | Climate water deficit sum, April-October |
| `tc_soil_summer_min` | Minimum soil moisture, June-August |
| `tc_soil_growing_min` | Minimum soil moisture, April-October |
| `tc_ppt_summer_sum` | Precipitation sum, June-August |
| `tc_ppt_growing_sum` | Precipitation sum, April-October |

Final dataset:

- `data/processed/vinhaguard_dataset.csv`
- 960 rows
- 29 columns
- 32 locations x 30 years
- 0 missing TerraClimate values

## ML Changes

`model/train.py` now includes the 8 TerraClimate columns in
`NUMERIC_FEATURES`. The model architecture did not change:

- Logistic Regression baseline;
- 500-tree Random Forest main model;
- chronological holdout: 1995-2019 train, 2020-2024 test;
- GroupKFold robustness check by `location_id`;
- model artifacts regenerated in `model/artifacts/`;
- figures regenerated in `docs/figures/`.

Current chronological holdout metrics:

| Model | ROC-AUC | PR-AUC | Brier | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.949 | 0.984 | 0.071 | 0.913 | 0.963 | 0.913 | 0.938 |
| Random Forest | 0.970 | 0.986 | 0.115 | 0.881 | 0.971 | 0.861 | 0.912 |
| Random Forest, calibrated | 0.977 | 0.986 | 0.042 | 0.944 | 0.934 | 0.991 | 0.962 |

The calibrated Random Forest remains the deployed model because it combines the
Random Forest's strong ranking performance with a better Brier score for pricing.
The uncalibrated Random Forest remains useful for feature-importance diagnostics.

Top feature drivers still start with the original trigger logic, as expected,
because the target is a climate-trigger proxy. Importantly,
`tc_def_growing_sum` now appears among the top drivers, showing that the added
water-balance data contributes real signal.

## Important Limitations

TerraClimate improves the model, but it does not turn the target into real
claims or yield loss. The label is still a proxy derived from climate stress
rules. For production, we would still want:

- IVDP parish-level yield data;
- insurer claims or payout history;
- vineyard parcel boundaries;
- Sentinel-2 NDVI/NDMI validation;
- local station calibration.

For the course project, this is a good tradeoff: the dataset is credible,
public, reproducible, and materially improves the ML explanation without making
the repo unmanageable.

## Verification Performed

Commands run:

```bash
python -m src.data.fetch_terraclimate
python -m src.data.make_dataset
python -m model.train
python -m compileall model src pages
```

Additional checks:

- verified `vinhaguard_dataset.csv` shape is 960 x 29;
- verified all 8 TerraClimate columns have 0 missing values;
- verified `model/artifacts/scored_history.csv` shape is 960 x 33;
- smoke-tested `predict_risk_and_premium()` across all region/risk combinations;
- launched the Streamlit app and verified the Risk Assessment and Dashboard pages.
