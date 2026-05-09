# VinhaGuard AI — Person 1: Business & Insurance Lead

> **Role:** Business & Insurance Lead  
> **Focus:** Problem framing, market logic, product concept, revenue model, unit economics, fairness & basis risk, go-to-market  
> **Output:** Business slides (2–3), financial logic, GTM strategy, market/problem sources

---

## Executive Summary

VinhaGuard AI is a **parametric climate insurance platform** for small and medium-sized wine producers in Portugal's Douro Valley (Trigo & Silva, 2022; Jones & Alves, 2012). The platform uses 30 years of daily ERA5 climate data from 32 Douro vineyard sites across three IVDP sub-regions to estimate climate risk exposure. When a severe, predefined climate threshold is breached, a liquidity payout is triggered automatically — no adjusters, no paperwork, no disputes.

The product is best understood as **fast climate-liquidity protection**, not full crop-loss compensation. VinhaGuard AI does not aim to replace indemnity insurance or cover every possible agricultural loss. Its promise is narrower and more credible: rules-based liquidity when a severe, measurable climate event occurs, helping small producers manage short-term cash-flow pressure after heat, drought, or frost shocks.

The strongest business setup is a **B2B2C model** — VinhaGuard AI operates as a data, pricing, and monitoring layer partnered with a licensed insurer or cooperative, avoiding the regulatory complexity of operating as an insurer directly.

---

## 1. Business Problem and Relevance

The Douro Valley encompasses nearly **45,000 hectares** of vineyards, ~22% of Portugal's total vineyard area, and over 40% of Portuguese wine exports (Santos et al., 2020). It is also highly exposed to climate variability.

The VinhaGuard dataset validates the problem empirically. Across 32 vineyard sites and 30 years (1995–2024), **39.8% of all location-years qualify as climate stress years** under the model's composite label. The validated extreme years illustrate the scale and recurrence of the problem:

| Year | % of 32 Douro sites classified as stress year | Known event |
|---|---|---|
| 2003 | 81% | European heatwave — hottest summer in 500 years |
| 2005 | 94% | Severe Iberian drought |
| 2017 | 94% | Record heat + Portugal wildfires |
| 2022 | **100%** | Exceptional pan-Iberian heat and drought |
| 2024 | 94% | Near-record Douro season |

Known cool and wet years (1999, 2002, 2008, 2014, 2019) register ≤ 3% of sites stressed, confirming the signal is clean and not noise. The insurance market has not adequately responded: traditional crop insurance is too slow, complex, and costly for smallholders who need liquidity quickly after a shock.

---

## 2. Target Customers and Market Logic

**Primary customers:** Small and medium-sized wine producers in the Douro Valley — particularly family farms and cooperative members. The region counts approximately **20,000 farmers** with an average holding of ~2 hectares (Trigo & Silva, 2022). This group combines high climate exposure with limited financial reserves.

The risk model reveals a clear sub-regional exposure gradient. Importantly, the probabilities below reflect the model's **climate stress classification** — a composite label capturing whether a year was anomalous for that location. The actual insurance payout trigger is calibrated more narrowly to severe events (see Section 3):

| Sub-region | Climate stress probability | Climate profile |
|---|---|---|
| Baixo Corgo | 45% | Cooler, wetter (~1,045 mm/year) |
| Cima Corgo | 55% | Intermediate |
| Douro Superior | 72% | Hottest and driest (~596 mm/year) — most exposed |

Smaller producers in Douro Superior face the highest exposure but the least capacity to absorb a bad year. They are the most underserved by traditional insurance.

**Go-to-market model:** Business-to-Business-to-Customer (B2B2C)

| Layer | Role |
|---|---|
| **VinhaGuard AI** | Risk model, premium engine, trigger monitoring, Portuguese-language customer dashboard |
| **Insurance partner** | Underwriting capacity, regulatory legitimacy, distribution network |
| **End customer** | Policy holder; receives automatic payout on trigger breach |

Secondary targets: insurers and cooperatives seeking lower claims administration costs and a scalable way to serve smaller agricultural clients.

---

## 3. Product Concept and Insurance Logic

VinhaGuard AI is a parametric insurance platform. Unlike traditional indemnity insurance, parametric insurance pays out when a **predefined, objective threshold is breached** — not after an assessed loss.

### An Important Distinction: Stress Probability vs. Trigger Probability

The ML model estimates the probability that a location-year qualifies as a **climate stress year** under the composite label (heat, frost, or drought anomaly). This is a useful risk signal, but it is not directly equivalent to the payout trigger probability.

For the insurance product, the actual trigger is calibrated to **severe, commercially significant events** — a narrower subset of stress years. For example, a region with a 55% climate stress classification frequency may face only a 5–15% probability of triggering a severe-threshold payout in a given year. This calibration is essential: it keeps premiums affordable and aligns payouts with events that cause meaningful economic harm.

The model output therefore serves two distinct purposes:
1. **Risk dashboard** — showing producers their sub-regional climate exposure profile
2. **Trigger calibration input** — informing where to set severe-event thresholds that produce actuarially plausible premiums

### Parametric Triggers (MVP Product)

| Risk type | Trigger condition | Dataset feature |
|---|---|---|
| **Heat** | 14 consecutive days above 38°C during véraison (July–August) | `heat_days_38`, `heatwave_max_streak` |
| **Frost** | 3 or more days below −2°C during flowering (March–May) | `spring_severe_frost_days` |
| **Drought** | Max consecutive dry days ≥ location's own 80th-percentile threshold | `max_consecutive_dry_days` |

The **combined product** allows a payout if either the heat or frost trigger fires — it is a coverage option, not a separate climate variable. The three core indicators above are the building blocks; the combined option is a bundling of the first two.

**Product promise:** VinhaGuard AI does not aim to fully compensate every agricultural loss. It provides **fast, rules-based liquidity when severe climate thresholds are breached**, helping small producers manage short-term cash-flow pressure. The target payout time is under 72 hours after verified trigger confirmation.

---

## 4. Business Model and Revenue Mechanism

VinhaGuard AI operates as a **hybrid SaaS + insurance distribution layer**, not a regulated insurer:

| Revenue stream | Mechanism |
|---|---|
| Commission on gross written premium | ~12% of GWP, aligned with portfolio growth |
| Annual platform fee per insured vineyard | Fixed cost recovery for dashboard, data pipeline, and support |

**Main cost drivers:**
- ERA5/Open-Meteo data access and pipeline maintenance
- ML model retraining and monitoring
- Streamlit dashboard hosting and customer onboarding
- Compliance support and partner management
- Trigger verification (fully automated — no field inspection required)

The parametric design creates a structural cost advantage: automated trigger verification eliminates the field-assessment overhead that makes traditional crop insurance expensive to administer.

**MVP scope:** A focused pilot with 50–100 producers in Douro Superior, partnered with one cooperative or agricultural association, testing a heat-stress product with a small fixed payout structure (see Section 5).

---

## 5. Financial Logic and Unit Economics

### Key Assumptions

> These figures are **illustrative MVP assumptions**, not actuarial or investment-grade estimates. The risk probabilities reflect the current prototype model and will be refined when Person 3's trained model replaces the mock values.

| Assumption | MVP value | Note |
|---|---|---|
| Product type | Fixed-payout smallholder policy | EUR 5,000 payout on trigger breach |
| Calibrated trigger probability | ~8–12% per year | Severe events only — not the full stress classification rate |
| Loss Given Trigger | 55% | Avg. fraction of insured value lost when trigger fires |
| Risk Loading | 25% | Insurer buffer for uncertainty and reinsurance |
| Admin Margin | 15% | Platform and operational costs |
| Prototype basis-risk indicator | 12.5% | Illustrative model diagnostic — not a validated actuarial estimate |

### MVP Premium Formula

The annual premium follows the formula implemented in the Streamlit Pricing Explainer:

```
Expected Loss  = Insured Value × P(trigger) × Loss Given Trigger
Annual Premium = Expected Loss × (1 + Risk Loading) × (1 + Admin Margin)
```

### Smallholder Product — Illustrative Example

For the MVP pilot, the primary product is a **fixed-payout policy** designed for small producers:

| Input | Value |
|---|---|
| Fixed payout on trigger | EUR 5,000 |
| Calibrated trigger probability | 8% (severe heat event) |
| Expected payout cost | EUR 220 (= 5,000 × 8% × 55%) |
| Risk Loading (25%) | EUR 55 |
| Admin Margin (15%) | EUR 41 |
| **Indicative annual premium** | **~EUR 316–550** |

A premium in the EUR 316–550 range represents **6–11% of the insured payout value** — affordable for a smallholder and credible for a parametric product. This is very different from full crop-value insurance: the product provides a defined liquidity buffer, not total loss coverage.

### Commercial Tier (for larger estates — illustrative only)

Larger producers with higher insured values would face proportionally higher premiums. Using the same formula on a EUR 40,000 insured value at sub-regional stress probabilities (which represent the full stress classification rate, not the calibrated severe trigger) produces premiums of EUR 14,000–22,000 — approximately 35–57% of insured value. This illustrates why the stress-probability-to-trigger-probability distinction matters: pricing on the full stress rate is not commercially viable. The commercial product would require careful actuarial calibration to a lower severe-event trigger probability before it could be offered to producers.

### Platform Revenue and Break-even

Using the smallholder product (EUR 550 average premium) and 12% GWP commission:

| Producers | GWP (EUR) | VinhaGuard Revenue | Fixed Costs | EBIT |
|---|---|---|---|---|
| 50 (pilot) | ~27,500 | ~5,800 | ~80,000 | −74,200 |
| 200 | ~110,000 | ~23,200 | ~83,000 | −59,800 |
| 500 | ~275,000 | ~58,000 | ~90,000 | −32,000 |
| **~833 (break-even)** | ~457,000 | ~96,500 | ~96,500 | ~0 |
| 1,000 | ~550,000 | ~116,000 | ~100,000 | ~16,000 |
| 2,000 | ~1,100,000 | ~232,000 | ~120,000 | ~112,000 |

*(Fixed costs: EUR 80,000 base + EUR 20/producer variable; revenue: 12% commission + EUR 50 platform fee)*

Break-even at roughly **833 producers** is a realistic **Year 2–3 target**, not a Year 1 expectation. The pilot phase (50–100 producers) is explicitly a validation exercise — testing trigger trust, willingness to pay, and cooperative partnership — not a profitable operation.

---

## 6. Competitive Positioning

| Alternative | Key weakness |
|---|---|
| Self-insurance | Requires reserves small producers typically lack |
| Public disaster aid | Uncertain timing, often delayed by months |
| Bank credit | Increases debt precisely under the worst financial conditions |
| Traditional crop insurance | Field assessment: slow, expensive, not designed for smallholders |
| **Cooperative emergency support** | **Limited funds, uneven availability, not systematic** |

The cooperative row is worth noting specifically: the go-to-market plan relies on cooperatives as distribution partners, but cooperatives also provide informal financial support to members in crisis. VinhaGuard AI must position itself as a complement to cooperative solidarity, not a replacement — and the formal, insured structure should be presented as more reliable and transparent than informal emergency funds.

**VinhaGuard AI differentiates through:**
1. **Speed** — payout triggered by verified ERA5 data, target under 72 hours after trigger confirmation
2. **Transparency** — triggers defined pre-purchase using objective, publicly sourced data
3. **Local precision** — risk model trained at sub-regional level on 30 years of site-specific data
4. **Language & accessibility** — Portuguese-language interface; trigger conditions displayed in Portuguese in the app

The strongest competitive message: *not necessarily the cheapest option, but faster, more explainable, and better matched to the cash-flow needs of smallholders after a climate shock.*

---

## 7. Fairness, Trust, and Basis Risk

**Basis risk** is the principal limitation of parametric insurance: the trigger may not perfectly match a producer's actual loss. A producer could suffer real damage without receiving a payout if the trigger threshold is not crossed, or receive a payout in a year with limited actual loss.

The current prototype reports a **12.5% basis-risk indicator**. This should be interpreted as an illustrative model diagnostic rather than a validated actuarial estimate. Actual basis risk depends on trigger design, grid resolution, and local micro-climate variability — factors that would require formal actuarial calibration in a real product.

**Why basis risk is especially significant in the Douro:** The ERA5 data used in the pipeline has a ~9 km grid resolution. Two vineyard sites within the same grid cell receive identical weather values regardless of micro-climate differences in slope, aspect, or altitude. This is a known limitation and must be disclosed clearly to policyholders.

**Mitigation strategies built into the product:**
- **Per-location percentile thresholds** — the stress label uses each site's own 30-year distribution, capturing relative anomalies rather than absolute temperatures
- **Sub-regional risk segmentation** — three distinct profiles rather than a single Douro-wide rate
- **Transparent disclosure** — the Streamlit Risk Assessment page shows the basis-risk indicator alongside every result

**On trust:** Producers must know the exact trigger, the data source, the payout amount, the waiting period after trigger confirmation, and what is not covered. Transparent disclosure of limitations — including basis risk — is more professionally credible than promising perfect protection.

---

## 8. Go-to-Market Recommendation

| Phase | Focus | Target | Key milestone |
|---|---|---|---|
| **Pilot (Year 1)** | Heat-stress trigger, Douro Superior | 50–100 producers via 1 cooperative | Validate trigger trust, willingness to pay, and payout experience |
| **Expand (Year 2)** | Add frost and drought modules; extend to Cima Corgo | 200–500 producers | Second insurance partner; approach break-even |
| **Scale (Year 3+)** | Full Douro coverage; insurer white-label option | 800–1,000+ producers | Cross break-even; explore replication in Alentejo |

**Entry rationale:** Douro Superior has the highest documented climate exposure (72% stress classification rate; 94–100% of sites stressed in documented extreme years) and the clearest climate narrative for the sales pitch. However, higher exposure also means higher technical premiums, so **affordability must be tested carefully in the pilot**: the product must be priced at a level smallholders in Douro Superior can genuinely sustain, not just a level that looks reasonable on paper.

**Pilot framing:** The year-one pilot is not a revenue exercise. It is a trust-building exercise. The questions it must answer are: Do producers understand the trigger? Do they trust the data source? Does a payout feel fair? Is the cooperative willing to co-market the product? Those answers are worth more at this stage than the GWP.

**Commercial narrative:** *VinhaGuard AI gives Douro wine producers fast, automatic liquidity when severe climate conditions cross a pre-agreed threshold — priced transparently by an AI model trained on 30 years of local ERA5 data.*

---

## 9. Slide Structure for Final Presentation

| Slide | Action title | Key content |
|---|---|---|
| **Slide 1** | Small Douro producers face rising climate shocks without fast, trusted liquidity protection | 39.8% of location-years are stress years; 2022 = 100% of sites stressed; traditional alternatives fail smallholders |
| **Slide 2** | VinhaGuard converts local climate data into simple, automatic payout rules | Trigger conditions; stress vs. payout probability distinction; B2B2C model; illustrative EUR 550 premium |
| **Slide 3** | Trust depends on transparent triggers, realistic pricing, and clear basis-risk disclosure | Prototype basis-risk indicator; per-location calibration; cooperative GTM; pilot roadmap to break-even |

*Person 1 owns the business case. The data pipeline (Person 2), ML model (Person 3), and Streamlit demo (Person 4) provide the technical foundation these slides reference.*

---

## References

Gouveia, C., Liberato, M. L. R., DaCamara, C. C., Trigo, R. M., & Ramos, A. M. (2011). Modelling past and future wine production in the Portuguese Douro Valley. *Climate Research*, 48, 349–362.

Jones, G. V., & Alves, F. (2012). Impacts of climate change on wine production: A global overview and regional assessment in the Douro Valley of Portugal. *International Journal of Global Warming*, 4(3/4), 383–406.

Santos, J. A., Ceglar, A., Toreti, A., & Prodhomme, C. (2020). Performance of seasonal forecasts of Douro and Port wine production. *Agricultural and Forest Meteorology*, 291, 108095.

Trigo, A., & Silva, P. (2022). Sustainable development directions for wine tourism in Douro Wine Region, Portugal. *Sustainability*, 14(7), 3949.
