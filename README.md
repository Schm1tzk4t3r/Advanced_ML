# VinhaGuard AI

VinhaGuard AI is a deployable prototype for parametric climate insurance in
Portugal's Douro Valley. It helps wine producers and insurer/cooperative
partners estimate climate-trigger risk, price coverage transparently, and
explain when automatic payouts would be activated.

The project was built for Nova SBE's Advanced Topics in Machine Learning final
project. It is an academic prototype, not a licensed insurance product.

## Why This Matters

Small and medium Douro wine producers face growing exposure to heatwaves,
drought, and spring frost. Traditional agricultural insurance is often too slow,
expensive, and paperwork-heavy for producers who need liquidity immediately
after a damaging climate event.

VinhaGuard uses parametric insurance logic: instead of sending an adjuster to
verify losses, the system pays when an objective weather trigger is breached
such as extreme heat days, severe spring frost, or an unusually long dry spell.
The result is a faster, more transparent workflow for climate-liquidity
protection.

## Product Overview

The Streamlit application exposes a full user-facing workflow:

- **Risk Assessment:** estimate climate-trigger risk and annual premium for a
  Douro vineyard profile.
- **Climate Dashboard:** inspect historical trigger behaviour, model drivers,
  basis-risk diagnostics, and model-performance charts.
- **Pricing Explainer:** show how expected payout, risk loading, admin cost, and
  margin form the premium.
- **AI Assistant:** answer product and methodology questions with guardrails and
  clear prototype limitations.

The intended business model is **B2B2C**. VinhaGuard provides the data pipeline,
ML risk engine, pricing workflow, dashboard, and trigger-monitoring layer. A
licensed insurer or cooperative would handle underwriting, regulation, and final
policy terms.

## Why AI Is Necessary

The payout trigger itself must remain rule-based because insurance needs
objective and auditable thresholds. The AI component creates value by learning
location-specific climate-risk patterns from 30 years of weather, water-balance,
and geography features. It supports:

- risk ranking across vineyards and subregions;
- trigger calibration for heat, frost, drought, and combined coverage;
- feature-importance explanations for producers and insurer partners;
- premium inputs grounded in historical trigger behaviour rather than a generic
  regional average.

This makes the product more than a chatbot wrapper: the moat is the
domain-specific climate feature pipeline, historical trigger backtesting,
pricing logic, basis-risk disclosure, and deployable insurance workflow.

## Technical Architecture

```text
Vineyard locations
      ↓
Open-Meteo / ERA5 daily weather fetch
      ↓
Annual heat, frost, drought feature engineering
      ↓
TerraClimate monthly water-balance enrichment
      ↓
Climate-stress labelling and ML-ready dataset
      ↓
Logistic Regression baseline + Random Forest risk model
      ↓
Pricing backend and Streamlit application
```

## Data Pipeline

Run the pipeline from the repository root:

| Step | Command | Output |
|---|---|---|
| 1 | `python -m src.data.locations` | `data/locations.csv` |
| 2 | `python -m src.data.fetch_weather` | `data/raw/weather/{location_id}.parquet` |
| 3 | `python -m src.data.build_features` | `data/interim/features_by_location_year.parquet` |
| 4 | `python -m src.data.fetch_terraclimate` | `data/processed/terraclimate_features.parquet` |
| 5 | `python -m src.data.make_dataset` | `data/processed/vinhaguard_dataset.parquet` |

Runtime is approximately 25-40 minutes on the first run, mostly due to network
calls. Weather downloads are resumable, and TerraClimate extracts are cached
under `data/raw/terraclimate/`, so reruns are much faster.

`data/raw/` and `data/interim/` are intentionally gitignored. The committed
submission includes the processed datasets required to run the model and app.

## Dataset

Canonical ML dataset:

- file: `data/processed/vinhaguard_dataset.csv` and `.parquet`
- 960 location-year rows
- 32 Douro vineyard locations
- 30 years: 1995-2024
- 29 columns
- target: `climate_stress_year`
- positive class share: 39.8%

Feature groups:

- geography: subregion, latitude, longitude, elevation;
- heat: heat-day counts, summer temperatures, heatwave streaks;
- frost: spring frost days and minimum spring temperature;
- drought: precipitation totals, dry days, maximum consecutive dry days;
- TerraClimate water balance: vapor pressure deficit, climate water deficit,
  soil moisture, and precipitation.

Thirty-two of 36 planned vineyard locations were fetched successfully. The four
missing locations are documented in `docs/data_sources.md`; subregion coverage
remains balanced enough for the prototype.

## Machine Learning

Training script:

```bash
python -m model.train
```

The training pipeline fits:

- **Logistic Regression** as an interpretable baseline;
- **Random Forest** as the deployed main model.

Evaluation design:

- chronological holdout: train on 1995-2019, test on 2020-2024;
- GroupKFold by `location_id` to test generalisation across vineyard sites;
- feature-importance, ROC, precision-recall, calibration, and confusion-matrix
  artifacts exported to `docs/figures/`.

Current holdout metrics:

| Model | ROC-AUC | PR-AUC | Brier | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.949 | 0.984 | 0.071 | 0.913 | 0.963 | 0.913 | 0.938 |
| Random Forest | 0.970 | 0.986 | 0.115 | 0.881 | 0.971 | 0.861 | 0.912 |
| Random Forest, calibrated | 0.977 | 0.986 | 0.042 | 0.944 | 0.934 | 0.991 | 0.962 |

Additional robustness check:

- Random Forest GroupKFold ROC-AUC by location: 0.937 mean, 0.055 standard
  deviation.

The deployed artifact is the calibrated Random Forest. Calibration improves the
Brier score and makes the risk scores more suitable for pricing, while the
uncalibrated Random Forest remains useful for ranking and feature-importance
diagnostics.

Important interpretation: the target is a climate-trigger proxy derived from
weather rules, not real claims or vineyard yield loss. The high AUC confirms
that the engineered features recover the trigger-risk logic; production use
would require claims, yield, parcel, and/or satellite validation.

## Pricing Backend

The deployable backend lives in `model/predict.py`:

```python
predict_risk_and_premium(
    subregion: str,
    area_ha: float,
    insured_value: float,
    risk_type: str,
    elevation: float | None = None,
) -> dict
```

At quote time, next season's weather is unknown. The backend therefore estimates
future trigger probability from historical comparable rows rather than
fabricating future weather features:

```text
risk_probability = 0.70 * historical_trigger_rate
                 + 0.30 * model_stress_probability
```

Premium formula:

```text
expected_payout = insured_value * risk_probability * loss_given_trigger
risk_loading    = expected_payout * uncertainty_loading
admin_cost      = 50 EUR + 2 EUR * vineyard_area_ha
premium         = (expected_payout + risk_loading + admin_cost) * (1 + admin_margin)
```

The app also reports basis risk, estimated dynamically from subregion coverage
and elevation distance from the historical median.

## Unit Economics

The business model combines:

- a commission on gross written premium through an insurer/cooperative partner;
- an annual platform fee per insured vineyard;
- low marginal software costs because the ML model runs locally and the chatbot
  is guardrailed to product-support use.

All premium and unit-economics figures are illustrative MVP assumptions. A
commercial launch would require actuarial validation, insurer partnership,
regulatory review, and reinsurance analysis.

## Safety, Reliability, and Privacy

Safety and reliability measures:

- transparent trigger definitions instead of opaque payout decisions;
- explicit basis-risk disclosure on quotes;
- chronological and location-group validation for the ML model;
- chatbot guardrails limiting answers to VinhaGuard, parametric insurance, and
  Douro climate-risk topics;
- no claim that the prototype is a licensed insurance product;
- no use of personally identifiable customer data in the committed dataset.

Known limitations:

- the ML target is a proxy label, not actual claims or yield loss;
- gridded climate data cannot fully capture parcel-level microclimates;
- premiums are illustrative and not actuarially certified;
- the app is a prototype demonstration, not a production policy system.

## How To Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To retrain the model:

```bash
python -m model.train
```

To rebuild the processed dataset from committed/intermediate data:

```bash
python -m src.data.fetch_terraclimate
python -m src.data.make_dataset
```

## Repository Guide

| Path | Purpose |
|---|---|
| `app.py`, `pages/` | Streamlit frontend |
| `model/train.py` | Model training, evaluation, artifact generation |
| `model/predict.py` | Risk and premium backend used by the app |
| `src/data/` | Data generation, fetch, feature engineering, and labelling scripts |
| `data/processed/` | Committed processed datasets used by the app and model |
| `model/artifacts/` | Trained model, metrics, feature importance, scored history |
| `docs/data_dictionary.md` | Column definitions and target rule |
| `docs/data_sources.md` | Data citations, licenses, and limitations |
| `docs/ml_pricing_methodology.md` | Detailed ML and pricing methodology |
| `docs/terraclimate_enrichment.md` | TerraClimate enrichment explanation |
| `docs/genai_log_*.md` | GenAI transparency logs required by the project brief |
| `business/` | Business case, unit economics notebook, and figures |

## GenAI Transparency

The project used GenAI tools for ideation, coding support, documentation
drafting, and consistency checking. The final repository includes transparency
logs under `docs/genai_log_*.md`, as required by the project description.
