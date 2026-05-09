# Person 1 — Business & Insurance Lead

## Contribution Overview

This folder contains the business and insurance analysis for **VinhaGuard AI**, a parametric climate insurance platform for small and medium-sized wine producers in the Douro Valley, Portugal.

### Files

| File | Description |
|---|---|
| `business_report.md` | Full business report: problem framing, market logic, product concept, unit economics, go-to-market strategy, fairness & basis risk analysis |
| `unit_economics.ipynb` | Python notebook implementing the parametric premium formula, sensitivity tables, portfolio revenue model, and basis risk simulation |

---

## VinhaGuard AI — Business Summary

### The Problem
Small Douro wine producers face increasing climate-related income risk (heat stress, frost, drought) but existing insurance is too slow, complex, and costly for reliable post-event liquidity.

### The Solution
A **parametric insurance platform** that pays out automatically when predefined, observable climate triggers are breached — no field inspection, no claims negotiation.

### Business Model (B2B2C)
- **VinhaGuard AI** provides: data infrastructure, risk scoring, premium calculation, trigger monitoring, customer dashboard
- **Insurance partner** provides: underwriting capacity, regulatory legitimacy, distribution
- **Revenue**: Platform fee per vineyard + commission on gross written premium (12%)

### Unit Economics (Base Case)

| Parameter | Value |
|---|---|
| Insured payout | EUR 5,000 |
| Trigger probability | 8%/year |
| Commercial premium | EUR 550/year |
| Platform margin | EUR 50/policy |
| Break-even scale | ~175 producers |

### Key References
- Jones & Alves (2012) — climate change impacts on Douro wine production
- Santos et al. (2020) — seasonal forecasting for Douro and Port wine
- Gouveia et al. (2011) — NDVI-based Douro production modelling
- Trigo & Silva (2022) — Douro wine region sustainability and market structure
