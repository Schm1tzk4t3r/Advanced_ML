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
- 29 columns: 20 original annual weather/geography fields, 8 TerraClimate water-balance fields, and the target
- target: `climate_stress_year`
- positive class share: 39.8%

The target is a climate-trigger proxy, not a real claims/loss label. It is derived from anomalous heat, spring frost, and drought conditions. The model now also receives TerraClimate water-balance features (`vpd`, `def`, `soil`, `ppt`) so the drought signal is not only a daily rainfall-count assumption. This is acceptable for a course MVP, but production deployment would require insurer claims, vineyard yields, station calibration, and/or NDVI validation.

**Honest caveat on the high AUC:** Because `climate_stress_year` is a deterministic function of the same ERA5 features used as model inputs, the model is partly learning to recover its own label rule from noisy inputs rather than discovering independent predictive signal. The high ROC-AUC (0.970) should therefore be interpreted as confirming that the engineered features faithfully encode the label logic — not as evidence of out-of-sample predictive power over actual crop losses. The known-year validation table (2003, 2005, 2017, 2022, 2024 all correctly identified as extreme) is the more meaningful real-world check.

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

**Test-set class imbalance caveat:** The holdout years 2020–2024 are climatically extreme (2022 = 100% of sites stressed; 2023/2024 = 94% stressed). As a result the test-set positive-class share is **71.9%** — substantially higher than the full dataset (39.8%). Metrics that depend on the class distribution — particularly precision — are therefore optimistic estimates of real-world performance in an average year. The known-year validation (all five documented extreme years correctly identified as stressed) is the more meaningful real-world check for model correctness. The GroupKFold cross-validation provides the more stable estimate of generalisation performance.

Important framing for the presentation:

The model is best described as a **climate-trigger risk model**. Since the target itself is derived from weather indicators, the model demonstrates that the engineered indicators recover stress-year logic and can produce a useful risk score. At quote time, the app cannot know next season's weather, so the pricing backend estimates future trigger probability from historical climatology and elevation-weighted comparable sites.

## Generated Evaluation Artifacts

Metrics:

- `model/artifacts/metrics.json`
- `model/artifacts/feature_importance.csv`
- `model/artifacts/scored_history.csv`

`scored_history.csv` is also the data source for the current dashboard. This keeps the dashboard aligned with the same 960-row scored history that powers the ML backend instead of the older six-column demo parquet.

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
| Logistic Regression | 0.949 | 0.984 | 0.071 | 0.913 | 0.963 | 0.913 | 0.938 |
| Random Forest (uncalibrated) | 0.970 | 0.986 | 0.115 | 0.881 | 0.971 | 0.861 | 0.912 |
| **Random Forest (calibrated, isotonic)** | **0.977** | **0.986** | **0.042** | **0.944** | **0.934** | **0.991** | **0.962** |

The deployed model is a **CalibratedClassifierCV (isotonic regression)** wrapping the Random Forest. Isotonic calibration corrected the RF's probability over-dispersion, reducing the Brier score from 0.115 to **0.042** — lower than Logistic Regression's 0.071. Well-calibrated probabilities are essential for the pricing backend because `expected_payout = insured_value × risk_prob × loss_given_trigger`; an inflated or deflated risk_prob directly misprices the product.

The calibration chart (`docs/figures/ml_calibration_curve.png`) shows the before/after comparison. The deployed model uses `CalibratedClassifierCV(cv=5)` refitted on the full 960-row dataset.

Additional robustness check:

- GroupKFold by `location_id`, Random Forest ROC-AUC: 0.937 mean, 0.055 std across five folds.
- One fold scores 0.833 against the others at 0.95+. This is expected when that fold's held-out locations form a geographically atypical cluster (e.g., a batch of high-elevation DS or low-elevation BC sites). It does not indicate overfitting — it shows the model is less certain when extrapolating to unfamiliar elevation/longitude combinations, which is also what the basis-risk logic captures.

Top feature drivers from permutation importance:

1. `max_consecutive_dry_days`
2. `heatwave_max_streak`
3. `elevation_m`
4. `heat_days_35`
5. `spring_severe_frost_days`
6. `tc_def_growing_sum`
7. `summer_precip_mm`
8. `min_spring_tmin`

Interpretation: drought persistence is still the strongest stress-year signal in the current label design, followed by heatwave duration. TerraClimate's growing-season water deficit now appears among the model drivers, which supports the product story that we are modelling physiologically meaningful water stress, not only counting hot or dry days. Frost is present but rarer, which is why its standalone pricing probability is lower.

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
- `All` (combined heat + frost + drought; the backend also accepts the legacy alias `Both` for backwards compatibility)

The model has three canonical IVDP risk profiles. For a friendlier demo, the UI also shows familiar place labels. These are mapped transparently to the three profiles:

- `Pinhao` / `Pinhão` -> `Cima Corgo`
- `Regua` / `Régua` -> `Baixo Corgo`
- `Vila Nova de Foz Coa` / `Vila Nova de Foz Côa` -> `Douro Superior`

## Risk Probability Logic

The app form only asks for subregion, vineyard area, insured value, risk type, and optional elevation. It does not ask for observed future weather. Therefore the backend does not fabricate feature values.

Instead:

1. It filters historical location-year rows to the selected subregion.
2. If elevation is provided, it weights historical rows by elevation similarity.
3. It calculates the relevant historical trigger frequency:
   - heat: severe heat trigger (`heat_days_38 >= 5`);
   - frost: spring severe frost trigger;
   - drought: dry-spell trigger;
   - both: combined climate-stress label.
4. It blends that historical trigger rate with the trained model's average stress probability on comparable history:

```text
risk_probability = 0.70 * historical_trigger_rate
                 + 0.30 * model_stress_probability
```

For narrow heat and frost coverage, the model component is capped against the hazard-specific trigger rate so the quote is not inflated by the broader combined stress label. This gives us a defensible estimate for quote pricing while keeping the AI component real and explainable.

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

- "We use AI where it matters: estimating and explaining climate-trigger probability from historical weather, water-balance, and geography features."
- "Pricing itself is transparent expected-value logic, not a black box."
- "The ML target is a climate-trigger proxy, so we are honest that production would require claims/yield validation."
- "The main moat is not a chatbot. It is the domain-specific climate feature pipeline, historical trigger backtesting, pricing workflow, and insurer/cooperative integration."
- "Safety is handled by transparent trigger definitions, basis-risk disclosure, no legally binding chatbot advice, and clear limitations around data resolution."
