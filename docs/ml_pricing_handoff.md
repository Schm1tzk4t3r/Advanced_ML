# VinhaGuard AI - ML and Pricing Handoff

## Scope

This document explains our ML and pricing work for the Advanced Topics in Machine Learning project. The goal was to turn the climate dataset into:

- a trained climate-stress model;
- evaluation metrics and charts;
- feature-importance outputs;
- a deployable `predict_risk_and_premium()` backend;
- a transparent premium formula.

We kept the implementation explainable and reproducible. It uses scikit-learn models already supported by `requirements.txt`, avoiding a new XGBoost dependency that could make the demo harder to run.

## Dataset

Input file: `data/processed/vinhaguard_dataset.csv`

Shape:

- 960 location-year rows
- 32 vineyard locations
- 30 years, 1995-2024
- target: `climate_stress_year`
- positive class share: 39.8%

The target is a climate-trigger proxy, not a real claims/loss label. It is derived from anomalous heat, spring frost, and drought conditions. This is acceptable for a course MVP, but production deployment would require insurer claims, vineyard yields, station calibration, and/or NDVI validation.

## Models

The training pipeline lives in `model/train.py`.

Two models are trained:

| Model | Role | Notes |
|---|---|---|
| Logistic Regression | Baseline | Standardized numeric features, one-hot subregion, class-balanced. |
| Random Forest | Main model | Captures non-linear trigger interactions, class-balanced, shallow enough to avoid an opaque black box. |

The deployed artifact is the Random Forest, saved as:

`model/artifacts/risk_model.joblib`

## Leakage and Evaluation Design

The main holdout is chronological:

- train: 1995-2019
- test: 2020-2024

This is harder and more honest than a random split because the test set contains recent high-stress climate years. The script also reports GroupKFold ROC-AUC by `location_id` to test whether the model generalizes across vineyard sites instead of memorizing one location.

Important framing for the presentation:

The model is best described as a **climate-trigger risk model**. Since the target itself is derived from weather indicators, the model demonstrates that the engineered indicators recover stress-year logic and can produce a useful risk score. At quote time, the app cannot know next season's weather, so the pricing backend estimates future trigger probability from historical climatology and elevation-weighted comparable sites.

## Generated Evaluation Artifacts

Metrics:

- `model/artifacts/metrics.json`
- `model/artifacts/feature_importance.csv`
- `model/artifacts/scored_history.csv`

Charts:

- `docs/figures/ml_confusion_matrix.png`
- `docs/figures/ml_roc_curve.png`
- `docs/figures/ml_precision_recall_curve.png`
- `docs/figures/ml_feature_importance.png`
- `docs/figures/ml_calibration_curve.png`

These are ready to use in the final slides.

## Current Results

Chronological holdout, trained on 1995-2019 and tested on 2020-2024:

| Model | ROC-AUC | PR-AUC | Brier | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.956 | 0.986 | 0.071 | 0.906 | 0.981 | 0.887 | 0.932 |
| Random Forest | 0.974 | 0.987 | 0.094 | 0.900 | 0.971 | 0.887 | 0.927 |

Random Forest was selected as the deployed model because it gives the strongest ranking performance on the recent chronological holdout and captures non-linear interactions between drought, heat, frost, and geography. Logistic Regression remains a strong baseline and has the better Brier score, which should be mentioned honestly if discussing calibration.

Additional robustness check:

- GroupKFold by `location_id`, Random Forest ROC-AUC: 0.936 mean, 0.053 std across five folds.

Top feature drivers from permutation importance:

1. `max_consecutive_dry_days`
2. `heatwave_max_streak`
3. `heat_days_35`
4. `min_spring_tmin`
5. `elevation_m`
6. `longitude`
7. `annual_precip_mm`
8. `spring_severe_frost_days`

Interpretation: drought persistence is the strongest stress-year signal in the current label design, followed by heatwave duration and anomalous heat. Frost is present but rarer, which is why its standalone pricing probability is lower.

## Pricing Backend

The backend lives in `model/predict.py`.

Public function:

```python
predict_risk_and_premium(
    subregion: str,
    area_ha: float,
    insured_value: float,
    risk_type: str,
    elevation: float | None = None,
) -> dict
```

Supported risk types:

- `Heat`
- `Frost`
- `Drought`
- `Both`

For backward compatibility with the current app, legacy demo regions are mapped to the three IVDP regions:

- `Pinhao` / `Pinhão` -> `Cima Corgo`
- `Regua` / `Régua` -> `Baixo Corgo`
- `Vila Nova de Foz Coa` / `Vila Nova de Foz Côa` -> `Douro Superior`

## Risk Probability Logic

The app form only asks for subregion, vineyard area, insured value, risk type, and optional elevation. It does not ask for observed future weather. Therefore the backend does not fabricate feature values.

Instead:

1. It filters historical location-year rows to the selected subregion.
2. If elevation is provided, it weights historical rows by elevation similarity.
3. It calculates the relevant historical trigger frequency:
   - heat: anomalous heat trigger;
   - frost: spring severe frost trigger;
   - drought: dry-spell trigger;
   - both: combined climate-stress label.
4. It blends that historical trigger rate with the trained model's average stress probability on comparable history:

```text
risk_probability = 0.70 * historical_trigger_rate
                 + 0.30 * model_stress_probability
```

This gives us a defensible estimate for quote pricing while keeping the AI component real and explainable.

## Premium Formula

```text
expected_payout = insured_value * risk_probability * loss_given_trigger
risk_loading    = expected_payout * uncertainty_loading
admin_cost      = 50 EUR + 2 EUR * vineyard_area_ha
subtotal        = expected_payout + risk_loading + admin_cost
premium         = subtotal * (1 + admin_margin)
```

Default pricing assumptions:

| Risk type | Loss given trigger | Base risk loading | Admin margin |
|---|---:|---:|---:|
| Heat | 50% | 25% | 15% |
| Frost | 40% | 25% | 15% |
| Drought | 45% | 25% | 15% |
| Both | 55% | 30% | 15% |

Basis risk is also returned to the UI. It starts at 10%, increases when subregion coverage is thinner, and increases when the entered elevation is far from the historical subregion median. This reflects the real limitation that ERA5/Open-Meteo grid data does not capture plot-level slope, aspect, or microclimate.

## How To Reproduce

From the repo root:

```bash
python -m model.train
```

Then smoke-test inference:

```bash
python -c "from model.predict import predict_risk_and_premium; print(predict_risk_and_premium('Cima Corgo', 12, 40000, 'Heat', 250))"
```

## Presentation Talking Points

- "We use AI where it matters: estimating and explaining climate-trigger probability from historical weather-derived features."
- "Pricing itself is transparent expected-value logic, not a black box."
- "The ML target is a climate-trigger proxy, so we are honest that production would require claims/yield validation."
- "The main moat is not a chatbot. It is the domain-specific climate feature pipeline, historical trigger backtesting, pricing workflow, and insurer/cooperative integration."
- "Safety is handled by transparent trigger definitions, basis-risk disclosure, no legally binding chatbot advice, and clear limitations around data resolution."
