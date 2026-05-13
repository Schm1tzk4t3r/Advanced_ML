# Business and Insurance Analysis

This folder contains the business and insurance work for VinhaGuard AI: market
framing, product logic, unit economics, go-to-market strategy, basis-risk
discussion, and safety/governance considerations.

## Files

| File | Description |
|---|---|
| `business_report.md` | Full business report covering problem, market, product workflow, AI necessity, unit economics, defensibility, basis risk, and safety |
| `unit_economics.ipynb` | Premium formula, pilot economics, revenue assumptions, break-even scenarios, and basis-risk simulation |
| `basis_risk.png` | Basis-risk simulation figure |
| `portfolio_economics.png` | Portfolio economics figure |
| `trigger_calibration.png` | Trigger calibration figure |

## Business Summary

VinhaGuard AI is a vineyard-specific climate-risk pricing and trigger-monitoring
infrastructure layer for insurers and cooperatives serving Portugal's Douro
Valley. It enables automatic parametric payouts when predefined climate
thresholds are breached.

The product is best understood as fast climate-liquidity protection, not full
crop-loss compensation.

## MVP Business Model

| Layer | Role |
|---|---|
| VinhaGuard AI | Data pipeline, ML risk scoring, pricing engine, trigger monitoring, customer dashboard |
| Insurance/cooperative partner | Underwriting capacity, regulatory legitimacy, distribution, payout execution |
| Producer | End customer receiving transparent climate-risk coverage |

Revenue assumptions:

- commission on gross written premium;
- annual platform fee per insured vineyard;
- insurer partner carries underwriting risk.

## Implemented Prototype

| Component | Status |
|---|---|
| ERA5 + TerraClimate dataset, 960 rows x 29 columns | Implemented |
| Weather and water-balance feature engineering | Implemented |
| Climate-stress target with per-location thresholds | Implemented |
| Logistic Regression baseline and Random Forest model | Implemented |
| Risk and premium backend | Implemented |
| Streamlit app with risk, dashboard, pricing, and chatbot pages | Implemented |
| Dynamic basis-risk diagnostic | Implemented as prototype indicator |
| Live insurer payout execution | Future partner integration |
| Formal actuarial tariff certification | Future validation required |

## Rubric Mapping

| Criterion | How the project addresses it |
|---|---|
| Real problem | Douro wine producers face heat, drought, and frost risk with limited fast-liquidity protection |
| AI necessity | ML estimates location-specific climate-trigger risk from weather, water-balance, and geography features |
| Deployable solution | Streamlit app plus trained model artifacts and source-code pipeline |
| Unit economics | Premium formula, revenue model, and break-even scenarios documented |
| Defensibility | Domain-specific data pipeline, local trigger calibration, insurance workflow, and basis-risk transparency |
| Safety | Clear prototype disclaimer, basis-risk disclosure, chatbot guardrails, and human insurer role |
| Transparency | Full premium formula and GenAI log included |

