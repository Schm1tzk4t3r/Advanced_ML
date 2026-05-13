# Person 1 — Business & Insurance Lead

## Contribution Overview

This folder contains the business and insurance analysis for **VinhaGuard AI** — a vineyard-specific climate-risk pricing and trigger-monitoring infrastructure layer for insurers and cooperatives, enabling automatic parametric payouts when predefined climate thresholds are breached.

### Files

| File | Description |
|---|---|
| `business_report.md` | Full business report: problem framing, market logic, product workflow, AI necessity, unit economics, go-to-market, basis risk, AI safety/governance |
| `unit_economics.ipynb` | MVP premium formula, smallholder pricing logic, platform revenue model, break-even analysis (~833 producers), and illustrative basis-risk simulation |

---

## How to Run the Demo

```bash
# 1. Clone and set up
git clone https://github.com/Schm1tzk4t3r/Advanced_ML.git
cd Advanced_ML
pip install -r requirements.txt

# 2. Run the data pipeline (generates real ERA5 dataset)
python -m src.data.locations
python -m src.data.fetch_weather      # ~5–15 min, Open-Meteo rate-limited
python -m src.data.build_features
python -m src.data.make_dataset

# 3. Launch the Streamlit app
streamlit run app.py
```

## Demo Workflow

1. Open the **Risk Assessment** page → select vineyard sub-region, area, risk type
2. View the **climate-risk score** and trigger condition (in Portuguese)
3. See the **premium breakdown** — expected payout cost, risk loading, admin margin
4. Open the **Pricing Explainer** → adjust trigger probability and payout sliders
5. Read the **basis-risk warning** shown alongside every result
6. Try the **Portuguese chatbot** for policy explanations

---

## What Is Implemented vs. Simulated

| Component | Status |
|---|---|
| ERA5 + TerraClimate dataset (32 sites × 30 years, 960 rows × 29 cols) | ✅ Implemented |
| Weather + water-balance feature engineering pipeline | ✅ Implemented |
| Climate stress classification (rule-based, per-location percentiles) | ✅ Implemented |
| Premium calculator (matching `pages/3_Pricing_Explainer.py`) | ✅ Implemented |
| Streamlit app — 4 pages: Risk, Dashboard, Pricing, Chatbot | ✅ Implemented |
| Portuguese-language interface | ✅ Implemented |
| Trained ML risk model (LR / Random Forest) | ✅ Implemented — Person 3 |
| Risk probability outputs | ✅ Person 3's trained classifier |
| Basis-risk estimation | ✅ Dynamic prototype diagnostic (8–22%) — actuarial calibration pending |
| Live seasonal trigger monitoring | 🔄 Simulated in demo |
| Insurer payout integration | 🔄 Future partner integration |
| Real payout execution | 🔄 Future partner integration |

---

## VinhaGuard AI — Business Summary

### The Problem
Small Douro wine producers face increasing climate-related income risk (heat stress, frost, drought) but existing insurance is too slow, complex, and costly for reliable post-event liquidity.

### The Solution
A **vineyard-specific climate-risk pricing and monitoring layer** that pays out automatically when predefined, observable climate triggers are breached — no field inspection, no claims negotiation. VinhaGuard AI does not carry underwriting risk; the licensed insurer partner remains the regulated risk carrier.

### Business Model (B2B2C)
- **VinhaGuard AI** provides: data infrastructure, risk scoring, premium calculation, trigger monitoring, Portuguese-language customer dashboard
- **Insurance partner** provides: underwriting capacity, regulatory legitimacy, distribution
- **Revenue**: EUR 50 platform fee per vineyard + 12% commission on gross written premium

### Unit Economics (Base Case)

| Parameter | Value |
|---|---|
| Insured payout | EUR 5,000 |
| Calibrated trigger probability | ~8% per year (severe events only) |
| Formula-based premium | EUR 316 |
| Commercial pilot price | EUR 550 |
| Break-even scale | ~833 producers (Year 2–3 target) |

*Break-even refers to platform economics only — VinhaGuard does not carry underwriting risk.*

---

## Professor Criteria Mapping

| Criterion | How VinhaGuard AI addresses it |
|---|---|
| **Real problem** | 39.8% of Douro location-years are climate stress years; 2022 = 100% sites stressed; smallholders lack fast post-shock liquidity |
| **AI necessity** | Per-location percentile calibration reduces basis risk; trigger probability must be distinguished from raw stress rate to produce viable premiums; rule-based thresholds alone create systematic unfairness |
| **Deployable solution** | Streamlit app running (4 pages); real ERA5 + TerraClimate dataset (960 rows); pricing engine implemented; trained ML model (LR/Random Forest) integrated by Person 3 |
| **Unit economics** | Platform break-even at ~833 producers; EUR 550 avg premium; 12% commission + EUR 50 fee; insurer carries underwriting risk separately |
| **Moat** | Localized Douro calibration data; trigger-performance history over time; insurer/cooperative workflow integration; domain-specific explainability |
| **Safety / privacy** | Human underwriting approval required; LLM cannot modify policy terms; basis-risk disclosed in app; data minimisation; no free-form payout promises |
| **Transparency** | Full premium formula visible to user; all model inputs logged; basis-risk indicator shown alongside every result |
| **Honesty about limits** | Basis-risk indicator is a model diagnostic, not an actuarial estimate; insurer partnership required; payout execution is future integration |

---

## Key References
- Jones & Alves (2012) — climate change impacts on Douro wine production
- Santos et al. (2020) — seasonal forecasting for Douro and Port wine
- Gouveia et al. (2011) — NDVI-based Douro production modelling
- Trigo & Silva (2022) — Douro wine region sustainability and market structure
