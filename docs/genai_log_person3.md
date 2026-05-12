# VinhaGuard AI - GenAI Transparency Log (ML and Pricing Lead)

## Overview

This log documents how we used GenAI tools for the ML and pricing part of VinhaGuard AI. The scope was the Person 3 contribution: model training, evaluation, feature importance, premium logic, and the `predict_risk_and_premium()` backend used by the Streamlit app.

We used Codex/ChatGPT as a coding and review assistant. The tool helped inspect the repository, design the training workflow, write Python code, generate documentation drafts, and run verification checks. The final modelling choices, pricing assumptions, limitations, and acceptance of the implementation were reviewed by us.

## What GenAI Was Used For

**Repository review.** Codex was asked to inspect the existing project structure, the data pipeline, the Streamlit app, and the project brief. This helped identify the main gap: the data pipeline was ready, but `model/predict.py` was still a mock backend and there was no trained model artifact.

**Model pipeline implementation.** Codex helped write `model/train.py`, including the chronological holdout split, Logistic Regression baseline, Random Forest main model, metrics export, feature importance, and evaluation charts.

**Pricing backend implementation.** Codex helped replace the mock `predict_risk_and_premium()` function with a backend that loads the trained model artifacts, uses historical trigger rates, applies elevation-weighted comparable sites, estimates basis risk, and returns a transparent premium breakdown.

**Documentation.** Codex helped draft `docs/ml_pricing_handoff.md`, including the evaluation results, model framing, risk-probability logic, and premium formula.

**Debugging and verification.** Codex helped run the training script, inspect generated artifacts, compile the Python modules, and smoke-test inference calls for different subregions and risk types.

## What We Decided

- We used **Logistic Regression** as the baseline because it is transparent, stable, and easy to explain.
- We used **Random Forest** as the deployed model because it gave the strongest ROC-AUC on the chronological holdout and captures non-linear interactions between heat, drought, frost, and geography.
- We did **not** add XGBoost because it would add another dependency shortly before the deadline. Random Forest is strong enough for the course MVP and easier to reproduce.
- We used a **chronological split** (train 1995-2019, test 2020-2024) because it is more honest than a random split for a climate-risk problem.
- We added a **GroupKFold by location** robustness check to test whether the model generalizes across vineyard sites.
- We framed the target honestly as a **climate-trigger proxy**, not a real claims/loss label.
- We designed the quote-time backend so it does not pretend to know future weather. It estimates risk from historical trigger rates and model scores on comparable historical rows.
- During final review, we corrected the heat payout trigger so the backend, dashboard, and FAQ use the same severe-event definition: at least 5 days above 38 C. This keeps the trigger close to the business case's ~8% severe-event calibration instead of pricing heat coverage from the broader climate-stress label.

## What Was Checked

- `python -m model.train` runs and writes the model artifacts.
- `model/artifacts/risk_model.joblib` loads through `model/predict.py`.
- `model/artifacts/metrics.json` contains both baseline and deployed-model metrics.
- `docs/figures/` contains ROC, precision-recall, confusion matrix, calibration, and feature-importance charts.
- `predict_risk_and_premium()` returns positive premiums, valid risk probabilities, basis-risk estimates, hazard rates, and feature importance.
- `python -m compileall model src pages` passes.

## Limitations

- The model predicts a climate-stress label derived from weather indicators. It does not predict actual vineyard yield loss or insurance claims because those data are not available in the current project.
- The current quote-time risk estimate is based on historical climatology and comparable vineyard sites. A production model would need insurer claims, local weather-station validation, plot-level vineyard data, and ideally NDVI or yield data.
- The premium formula is an MVP pricing formula, not an actuarially certified tariff.
- Basis risk is estimated as a transparent prototype indicator. It should not be presented as a formally validated actuarial basis-risk metric.

## Files Produced

- `model/train.py`
- `model/predict.py`
- `model/artifacts/risk_model.joblib`
- `model/artifacts/metrics.json`
- `model/artifacts/feature_importance.csv`
- `model/artifacts/feature_columns.json`
- `model/artifacts/scored_history.csv`
- `docs/figures/ml_confusion_matrix.png`
- `docs/figures/ml_roc_curve.png`
- `docs/figures/ml_precision_recall_curve.png`
- `docs/figures/ml_feature_importance.png`
- `docs/figures/ml_calibration_curve.png`
- `docs/ml_pricing_handoff.md`
