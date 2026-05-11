# VinhaGuard AI

> **Requires Python 3.10+** (`model/predict.py` uses union-type syntax introduced in 3.10)

## Description

VinhaGuard AI is a parametric climate insurance prototype for small wine producers in the Douro Valley, built for the Advanced Topics in Machine Learning course at Nova SBE. The platform uses 30+ years of historical climate data from 32 Douro vineyard sites to train a risk model (Logistic Regression baseline and Random Forest main model) that estimates the probability of a climate stress event — heat stress, spring frost, or drought — in a given location-year. Payouts are triggered automatically by objective climate thresholds, with no adjusters and no paperwork. A Streamlit app exposes the risk assessment, dashboard, pricing explainer, and FAQ chatbot.

## Data pipeline

Run the four steps in order from the repo root:

```
locations      →  fetch_weather  →  build_features  →  make_dataset
```

| Step | Command | Output | Notes |
|---|---|---|---|
| 1 | `python -m src.data.locations` | `data/locations.csv` | 36 Douro vineyard sites with IVDP subregion metadata |
| 2 | `python -m src.data.fetch_weather` | `data/raw/weather/{location_id}.parquet` | 30 years × 32 locations of daily ERA5 weather via Open-Meteo; resumable (skips files already downloaded) |
| 3 | `python -m src.data.build_features` | `data/interim/features_by_location_year.parquet` | 20 engineered climate features per location-year; rows with <90% daily completeness are dropped |
| 4 | `python -m src.data.make_dataset` | `data/processed/vinhaguard_dataset.parquet` `.csv` | Adds `climate_stress_year` binary label; final ML-ready dataset |

**Runtime:** ~5–15 minutes end-to-end, dominated by Step 2. Open-Meteo's free tier allows approximately 3–4 requests per minute; the fetch script sleeps 20 s between requests to stay within rate limits. Step 3 and Step 4 each complete in under 10 seconds.

**Coverage:** 32 of 36 planned locations have weather data. Four sites — **CC03, CC12, DS05, DS10** — could not be fetched within the project timeline due to API rate limits. Sub-region coverage remains balanced (BC 10/12, CC 12/14, DS 8/10). Re-running `python -m src.data.fetch_weather` will skip the 32 existing files and retry only the 4 missing ones.

`data/raw/` and `data/interim/` are gitignored. Only `data/locations.csv` and `data/processed/` are committed.

**Reference docs:**
- Column definitions and labelling rule → [`docs/data_dictionary.md`](docs/data_dictionary.md)
- API citations, licenses, and known limitations → [`docs/data_sources.md`](docs/data_sources.md)

### Handoff

| Artifact | For | Notes |
|---|---|---|
| `data/processed/vinhaguard_dataset.parquet` | Person 3 (ML training), Person 4 (Streamlit demo) | Canonical dataset — 960 rows × 21 columns (32 locations × 30 years). Target column: `climate_stress_year` (39.8% positive class). |
| `model/artifacts/scored_history.csv` | Person 3 (ML backend), Person 4 (dashboard) | Rich scored history used by the current dashboard — 960 rows x 25 columns, including trigger indicators and model stress probabilities. |
| `data/processed/douro_climate.parquet` | Legacy demo archive only | **Legacy synthetic placeholder.** Do not use for model training, evaluation, or the final dashboard. |

## How to reproduce

```bash
# 1. Clone and set up environment (Python 3.10+)
git clone <repo-url>
cd Advanced_ML
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Run the data pipeline
python -m src.data.locations
python -m src.data.fetch_weather
python -m src.data.build_features
python -m src.data.make_dataset

# 3. Launch the Streamlit app
streamlit run app.py
```

## ML and pricing backend

Person 3's ML deliverable is implemented in `model/train.py` and `model/predict.py`.

```bash
python -m model.train
```

This trains the Logistic Regression baseline and Random Forest main model, writes `model/artifacts/risk_model.joblib`, exports metrics to `model/artifacts/metrics.json`, and creates evaluation charts in `docs/figures/`. The deployable `predict_risk_and_premium()` backend uses the trained model plus historical trigger rates to return risk probability, premium, basis-risk estimate, feature importance, and pricing breakdown.

The trained model has three canonical IVDP risk profiles: Baixo Corgo, Cima Corgo, and Douro Superior. The demo labels Pinhao, Regua, and Vila Nova de Foz Coa are mapped transparently to those profiles in the backend and dashboard.

Reference docs:
- [`docs/ml_pricing_handoff.md`](docs/ml_pricing_handoff.md)
- [`docs/genai_log_person3.md`](docs/genai_log_person3.md)
