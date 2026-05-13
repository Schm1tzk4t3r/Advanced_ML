# VinhaGuard AI — Person 1: Business & Insurance Lead

> **Role:** Business & Insurance Lead  
> **Focus:** Problem framing, market logic, product concept, revenue model, unit economics, fairness & basis risk, go-to-market  
> **Output:** Business slides (2–3), financial logic, GTM strategy, market/problem sources

---

## Executive Summary

VinhaGuard AI is a **vineyard-specific climate-risk pricing and trigger-monitoring infrastructure layer** for insurers and cooperatives serving Portugal's Douro Valley. It is not a chatbot wrapper or a generic insurance platform. The system uses 30 years of daily ERA5 climate data from 32 Douro vineyard sites across three IVDP sub-regions to classify climate stress, calibrate payout trigger thresholds, and provide transparent premium pricing — reducing basis risk, the core failure mode of parametric insurance (Trigo & Silva, 2022; Jones & Alves, 2012).

When a predefined severe climate threshold is breached, a liquidity payout is triggered automatically — no adjusters, no paperwork, no disputes. The product is best understood as **fast climate-liquidity protection**, not full crop-loss compensation.

The strongest business setup is a **B2B2C model** — VinhaGuard AI operates as a data, pricing, and monitoring layer partnered with a licensed insurer or cooperative. **VinhaGuard AI does not carry underwriting risk.** The insurer partner remains the regulated risk carrier; VinhaGuard provides pricing infrastructure, trigger monitoring, and user-facing explainability.

**Why now:** VinhaGuard AI is viable today because three previously expensive inputs are now accessible at low cost: high-resolution ERA5 reanalysis climate data is freely available via Open-Meteo, lightweight classification models (Logistic Regression, Random Forest) can be trained on modest hardware in minutes, and Streamlit enables a production-quality web interface without a dedicated engineering team. Vineyard-level parametric pricing at this granularity was not feasible a decade ago.

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

Known cool and wet years (1999, 2002, 2008, 2014, 2019) register ≤ 3% of sites stressed, confirming the signal is clean and not noise. The pain is not only crop loss — it is post-event cash-flow pressure during the critical period before any compensation arrives. Traditional crop insurance is too slow, complex, and costly for smallholders who need liquidity quickly after a shock.

---

## 2. Target Customers and Market Logic

**Primary customers:** Small and medium-sized wine producers in the Douro Valley — particularly family farms and cooperative members. The region counts approximately **20,000 farmers** with an average holding of ~2 hectares (Trigo & Silva, 2022). This group combines high climate exposure with limited financial reserves.

The risk model reveals a clear sub-regional exposure gradient. Importantly, the probabilities below reflect the prototype's **climate stress classification** — a composite label capturing whether a year was anomalous for that location. The actual insurance payout trigger is calibrated more narrowly to severe events (see Section 3):

| Sub-region | Climate stress probability | Climate profile |
|---|---|---|
| Baixo Corgo | 45% | Cooler, wetter (~1,045 mm/year) |
| Cima Corgo | 55% | Intermediate |
| Douro Superior | 72% | Hottest and driest (~596 mm/year) — most exposed |

*Note: these probabilities reflect the prototype model (`model/predict.py`), grounded in the real dataset statistics from `data/processed/vinhaguard_dataset.parquet`. Person 3's trained Logistic Regression / Random Forest backend is now implemented and provides the ML backend for risk probability estimation.*

Smaller producers in Douro Superior face the highest exposure but the least capacity to absorb a bad year. They are the most underserved by traditional insurance.

**Go-to-market model:** Business-to-Business-to-Customer (B2B2C)

| Layer | Role |
|---|---|
| **VinhaGuard AI** | Risk model, premium engine, trigger monitoring, Portuguese-language customer dashboard |
| **Insurance partner** | Underwriting capacity, regulatory legitimacy, distribution network |
| **End customer** | Policy holder; receives automatic payout on trigger breach |

Secondary targets: insurers and cooperatives seeking lower claims administration costs and a scalable way to serve smaller agricultural clients.

---

## 3. Product Concept, Insurance Logic, and AI Necessity

VinhaGuard AI is a parametric insurance platform. Unlike traditional indemnity insurance, parametric insurance pays out when a **predefined, objective threshold is breached** — not after an assessed loss.

### Product Workflow

A typical user journey illustrates the deployable product:

> A cooperative registers its member vineyards with location and plot characteristics. VinhaGuard AI retrieves 30 years of ERA5 weather data for each site, estimates sub-regional trigger probability, and recommends a transparent payout-premium combination. During the growing season, the system monitors trigger indicators. If a threshold is breached — for example, 5 or more days above 38°C during the growing season — the system produces an automatic payout recommendation for the insurer partner and notifies the producer. The payout is transferred within a target of 72 hours. No field inspection. No claims negotiation.

This workflow is not well served by a static actuarial spreadsheet because it requires vineyard-level calibration, continuous seasonal monitoring, and explainable communication of uncertainty to non-technical users.

### Why AI Is Necessary

A sceptical reviewer might ask: can a fixed rule and a historical probability table replace this system? The answer is no, for three reasons.

**1. Trigger calibration requires location-specific learning.** A single regional threshold applied to all Douro sites would create systematic basis risk. The risk model uses site-level historical weather and per-location 80th-percentile thresholds to estimate the probability distribution of trigger breach at each vineyard — capturing relative climate anomalies, not just absolute temperatures. This per-location calibration is the core technical design choice, implemented in `src/data/make_dataset.py`.

**2. Basis-risk estimation requires a model, not a fixed constant.** The gap between when a trigger fires and when actual loss occurs — the basis risk — depends on how well the trigger threshold is matched to real vineyard conditions. In the deployed prototype, basis risk is estimated dynamically (8–22%) from subregion coverage depth and elevation distance from the historical median — not a static constant. In a production product, this would be further calibrated against historical trigger-vs-loss mismatches.

**3. Premium calibration depends on calibrated trigger probabilities.** The premium formula (`Expected Loss = IV × P(trigger) × LGT`) is only as credible as the P(trigger) estimate. Using the full stress classification rate (45–72%) as a direct proxy for trigger probability produces premiums that are commercially unviable (35–57% of insured value). The system's value is in calibrating P(trigger) to severe events only (~8–12%), informed by the dataset's learned threshold distributions and validated against known extreme years.

**Current prototype status:** The risk probability outputs come from Person 3's trained Random Forest classifier (ROC-AUC 0.970 on a chronological 2020–2024 holdout), blended 70/30 with historical trigger rates. The full pipeline — data, feature engineering, TerraClimate water-balance enrichment, ML model, premium formula, and Streamlit app — is implemented and deployed.

The Portuguese-language interface and explainability assistant are secondary features. The core AI value is risk calibration, vineyard-specific pricing, and basis-risk reduction.

### An Important Distinction: Stress Probability vs. Trigger Probability

The risk model estimates the probability that a location-year qualifies as a **climate stress year** under the composite label (heat, frost, or drought anomaly). This is a useful risk signal, but it is not directly equivalent to the payout trigger probability.

For the insurance product, the actual trigger is calibrated to **severe, commercially significant events** — a narrower subset of stress years. For example, a region with a 55% climate stress classification frequency may face only a 5–15% probability of triggering a severe-threshold payout in a given year. This calibration is essential: it keeps premiums affordable and aligns payouts with events that cause meaningful economic harm.

The model output therefore serves two distinct purposes:
1. **Risk dashboard** — showing producers their sub-regional climate exposure profile
2. **Trigger calibration input** — informing where to set severe-event thresholds that produce actuarially plausible premiums

### Parametric Triggers (MVP Product)

| Risk type | Trigger condition | Dataset feature |
|---|---|---|
| **Heat** | At least 5 days above 38°C during the growing season | `heat_days_38`, `heatwave_max_streak` |
| **Frost** | 3 or more days below −2°C during flowering (March–May) | `spring_severe_frost_days` |
| **Drought** | Max consecutive dry days ≥ location's own 80th-percentile threshold | `max_consecutive_dry_days` |

**Product promise:** VinhaGuard AI does not aim to fully compensate every agricultural loss. It provides **fast, rules-based liquidity when severe climate thresholds are breached**, helping small producers manage short-term cash-flow pressure. The payout timeline is defined in the policy with the insurer partner.

### AI Backend Architecture

| Layer | Components | Status |
|---|---|---|
| **Input** | Vineyard coordinates, sub-region, historical ERA5 features (heat, frost, drought) | ✅ Implemented |
| **Risk model** | Climate stress classification; trigger probability estimation; premium input generation | ✅ Person 3's trained LR/Random Forest classifier |
| **Business logic** | Expected loss formula; risk loading; admin margin; platform revenue | ✅ Implemented |
| **Frontend** | Risk dashboard; pricing explainer; trigger explanation; Portuguese assistant | ✅ Implemented |

---

## 4. Business Model and Revenue Mechanism

VinhaGuard AI operates as a **hybrid SaaS + insurance distribution layer**, not a regulated insurer.

**Platform vs. insurer risk — a critical distinction:** VinhaGuard AI does not carry underwriting risk in the MVP or at scale. The insurer partner holds the risk balance sheet and absorbs correlated loss exposure in extreme years. VinhaGuard earns software and commission revenue regardless of whether triggers fire. This distinction is essential: the platform economics are evaluated independently of insurer loss volatility, and it is what makes the B2B2C model commercially viable for a startup.

| Revenue stream | Mechanism |
|---|---|
| Commission on gross written premium | ~12% of GWP, aligned with portfolio growth |
| Annual platform fee per insured vineyard | EUR 50/year — fixed cost recovery for dashboard, data pipeline, and support |

**Main cost drivers:**
- ERA5/Open-Meteo data access and pipeline maintenance
- Risk model retraining and monitoring
- Streamlit dashboard hosting and customer onboarding
- Compliance support and partner management
- Trigger verification (fully automated — no field inspection required)

**MVP scope:** A focused pilot with 50–100 producers in Douro Superior, partnered with one cooperative or agricultural association, testing a heat-stress product with a small fixed payout structure (see Section 5).

---

## 5. Financial Logic and Unit Economics

### Key Assumptions

> These figures are **illustrative MVP assumptions**, not actuarial or investment-grade estimates. The risk probabilities are generated by Person 3's trained ML classifier; full actuarial calibration remains a pre-commercialisation step.

| Assumption | MVP value | Note |
|---|---|---|
| Product type | Fixed-payout smallholder policy | EUR 5,000 payout on trigger breach |
| Calibrated trigger probability | ~8–12% per year | Severe events only — not the full stress classification rate |
| Loss Given Trigger | 55% | Avg. fraction of insured value lost when trigger fires |
| Risk Loading | 25% | Insurer buffer for uncertainty and reinsurance |
| Admin Margin | 15% | Platform and operational costs |
| Basis-risk indicator | 8–22% (dynamic) | Estimated from subregion coverage depth and elevation distance from median |

### MVP Premium Formula

The annual premium follows the formula implemented in the Streamlit Pricing Explainer (`pages/3_Pricing_Explainer.py`):

```
Expected Loss  = Insured Value × P(trigger) × Loss Given Trigger
Risk Loading   = Expected Loss × Risk Loading %
Admin Cost     = EUR 50 (platform fee) + EUR 2 × Vineyard Area (ha)
Annual Premium = (Expected Loss + Risk Loading + Admin Cost) × (1 + Admin Margin)
```

### Smallholder Product — Illustrative Example

| Input | Value |
|---|---|
| Fixed payout on trigger | EUR 5,000 |
| Calibrated trigger probability | 8% (severe heat event) |
| Expected payout cost | EUR 220 (= 5,000 × 8% × 55%) |
| Risk Loading (25%) | EUR 55 |
| Admin Margin (15%) | EUR 41 |
| **Formula-based premium** | **EUR 316** |
| *(Fixed admin cost EUR 50 + EUR 2/ha excluded from this example for simplicity)* | |
| **Commercial pilot price** | **EUR 550** |

**Why the range EUR 316–550:** The formula at 8% trigger probability produces EUR 316. The EUR 550 commercial figure used in the revenue model reflects a rounded pilot price that incorporates frost and drought coverage add-ons (which modestly raise the effective trigger probability), conservative onboarding and support buffers, and standard rounding for smallholder policy pricing. Both figures are illustrative assumptions pending actuarial validation.

A premium in the EUR 316–550 range represents **6–11% of the insured payout value** — plausible for a smallholder parametric product. This is very different from full crop-value insurance: the product provides a defined liquidity buffer, not total loss coverage.

**Note on correlated risk:** Agricultural climate risks are often correlated — in an extreme year such as 2022 (100% of Douro sites stressed), many producers would trigger payouts simultaneously. This is precisely why VinhaGuard AI does not carry underwriting risk: the insurer partner manages the correlated loss exposure through reinsurance.

> The 37.5% combined loading ratio (Risk Loading + Admin Margin) is an illustrative assumption. Its commercial viability would need to be validated against Portuguese agricultural insurance pricing, reinsurance market costs, and cooperative willingness to pay before a real product launch.

### Platform Revenue and Break-even

Using the smallholder product (EUR 550 average premium) and 12% GWP commission:

**Scenario A — Student project baseline (EUR 80,000 fixed costs)**

| Producers | GWP (EUR) | VinhaGuard Revenue | Fixed Costs | EBIT |
|---|---|---|---|---|
| 50 (pilot) | ~27,500 | ~5,800 | ~80,000 | −74,200 |
| 200 | ~110,000 | ~23,200 | ~83,000 | −59,800 |
| 500 | ~275,000 | ~58,000 | ~90,000 | −32,000 |
| **~833 (break-even)** | ~457,000 | ~96,500 | ~96,500 | ~0 |
| 1,000 | ~550,000 | ~116,000 | ~100,000 | ~16,000 |
| 2,000 | ~1,100,000 | ~232,000 | ~120,000 | ~112,000 |

*(Fixed costs: EUR 80,000 base + EUR 20/producer variable; revenue: 12% commission + EUR 50 platform fee)*

**Scenario B — Regulated insurance infrastructure (EUR 350,000 fixed costs)**

A commercially viable insurance infrastructure layer requires an actuary (EUR 70–90k/year), a software engineer (EUR 50–70k/year), legal/regulatory advisory for the insurer partnership (EUR 30–50k/year), and customer success for Portuguese-speaking smallholders (EUR 30–50k/year). EUR 350,000 is a conservative estimate; EUR 400–500k is more realistic at scale.

| Producers | VinhaGuard Revenue | Fixed Costs | EBIT |
|---|---|---|---|
| 50 (pilot) | ~5,800 | ~351,000 | −345,200 |
| 500 | ~58,000 | ~360,000 | −302,000 |
| 1,000 | ~116,000 | ~370,000 | −254,000 |
| **~3,646 (break-even)** | ~420,000 | ~420,000 | ~0 |
| 5,000 | ~575,000 | ~450,000 | ~125,000 |

Break-even at roughly **833 producers** (Scenario A) assumes a lean student-project cost base. A commercially compliant insurance infrastructure product breaks even closer to **3,500–4,000 producers** — a Year 3–5 target requiring successful insurer partnership, actuarial sign-off, and geographic expansion beyond the MVP pilot.

> **Important:** Both scenarios represent **platform break-even only**, not insurance profitability. They exclude insurer loss ratio, reinsurance pricing, regulatory capital, and claims reserve requirements — because VinhaGuard does not carry underwriting risk. For the insurer partner, profitability requires separate actuarial validation of trigger frequency, loss correlation, and reinsurance cost.

**Open-Meteo data licensing note:** The free tier of the Open-Meteo Historical API is used for the prototype. Commercial deployment of a product that distributes weather-triggered financial payouts based on Open-Meteo data requires a commercial API agreement. At production scale (1,000+ sites × daily monitoring), a commercial plan is required and should be included in the cost model. Current pricing starts at approximately EUR 30/month for commercial use.

---

## 6. Competitive Positioning and Defensibility

| Alternative | Key weakness |
|---|---|
| Self-insurance | Requires reserves small producers typically lack |
| Public disaster aid | Uncertain timing, often delayed by months |
| Bank credit | Increases debt precisely under the worst financial conditions |
| Traditional crop insurance | Field assessment: slow, expensive, not designed for smallholders |
| **Cooperative emergency support** | **Limited funds, uneven availability, not systematic** |

VinhaGuard AI must position itself as a complement to cooperative solidarity — the formal, insured structure is more reliable and transparent than informal emergency funds.

**Differentiation:**
1. **Speed** — payout triggered by verified ERA5 data; timeline defined in policy with insurer partner (target under 72 hours, subject to insurer integration)
2. **Transparency** — triggers defined pre-purchase using objective, publicly sourced data
3. **Local precision** — risk model calibrated at sub-regional level on 30 years of site-specific data
4. **Basis-risk reduction** — per-location percentile thresholds reduce false negatives vs. uniform regional triggers
5. **Language & accessibility** — Portuguese-language interface; trigger conditions displayed in Portuguese in the app

**Defensibility — the real moat:** The durable moat is not speed or language — it is:
- **Localized Douro calibration data** — 30 years of site-specific ERA5 records validated against known extreme vintages. Over time, the system accumulates trigger-performance history: records of when triggers fired, whether actual losses occurred, and where basis-risk mismatch was highest. This dataset becomes more valuable with each season. *Note: ERA5 data itself is public; the moat accrues only after operating seasons generate proprietary trigger-vs-loss records.*
- **Insurance and cooperative workflow integration** — plugging into insurer underwriting and payout processes creates switching costs. Once an insurer's workflow depends on VinhaGuard's pricing engine and monitoring layer, replacement requires re-integration, re-validation, and re-training. *Note: this integration does not yet exist; the moat is a roadmap item, not a current asset.*
- **Per-location percentile threshold calibration** — the core technical design choice. Each vineyard's trigger is calibrated to its own 30-year baseline, capturing relative anomaly rather than absolute temperature. This is the one moat element that exists in the current codebase and is non-trivial to replicate without the same design insight.
- **Domain-specific explainability** — not a generic LLM answer, but a transparent premium derivation and trigger explanation tied to actual ERA5 data for a specific vineyard location.

**Honest moat assessment:** At the time of the prototype, ERA5 data is public, the trigger-performance history does not exist, and the insurer workflow integration has not been built. The protection today is geographic and relational — no large platform is targeting Douro Valley smallholder insurance. That window is real but time-limited.

*Traditional crop insurance tries to estimate actual loss after the event. VinhaGuard avoids that bottleneck by paying based on objective climate data, making it faster and cheaper to administer — but less complete because it introduces basis risk. That trade-off must be disclosed clearly.*

---

## 7. Fairness, Basis Risk, and Technical Evidence

### Basis Risk as Core Value Proposition

Basis-risk reduction is not merely a limitation to disclose — it is the primary reason the system matters over a simple actuarial spreadsheet.

**The core technical value:** A single regional trigger threshold applied uniformly across all Douro sites would produce systematic unfairness — producers in a cool valley microclimate might face the same threshold as those on a sun-exposed slope. The prototype uses per-location 80th-percentile distributions to design vineyard-specific triggers that reduce false negatives: cases where a producer suffers damage but receives no payout.

**Residual basis risk:** Even with localized triggers, the trigger may not perfectly match a producer's actual loss. The deployed prototype estimates basis risk dynamically at **8–22%** depending on subregion coverage depth and how far the entered elevation diverges from the historical site median. Actual basis risk depends on trigger design, grid resolution, and local micro-climate variability.

**ERA5 grid limitation:** The ERA5 data has a ~9 km grid resolution. Two vineyard sites within the same grid cell receive identical weather values regardless of micro-climate differences in slope, aspect, or altitude. This must be disclosed clearly to policyholders.

**Mitigation strategies built in:**
- Per-location percentile thresholds — relative anomaly, not absolute temperature
- Sub-regional risk segmentation — three distinct profiles
- Transparent disclosure — the Streamlit Risk Assessment page shows the basis-risk indicator alongside every result

### Data and Model Evidence

All quantitative claims in this report are traceable to the codebase:

| Claim | Source | How calculated |
|---|---|---|
| 32 Douro vineyard sites | `data/locations.csv` | Hand-curated, IVDP-classified; 32 of 36 planned sites with complete ERA5 data |
| 30 years ERA5 data (1995–2024) | Open-Meteo Historical API | Daily weather fetched per site via `src/data/fetch_weather.py` |
| 960 rows × 29 columns | `data/processed/vinhaguard_dataset.parquet` | Verifiable: `pd.read_parquet('...').shape` → (960, 29) |
| 39.8% stress years | `climate_stress_year` column | Share of rows with label = 1 across all 32 sites × 30 years |
| 2022 = 100% sites stressed | Known-year validation table | All 32 sites labelled stress = 1 in 2022 (`docs/data_dictionary.md`) |
| 72% Douro Superior stress rate | Dataset sub-regional analysis | Average stress classification rate for DS sites (DS01–DS10) |
| 45%, 55%, 72% sub-regional rates | Historical scored dataset / `model/predict.py` | Risk-profile examples grounded in model artifacts and historical trigger rates |
| 8–22% basis-risk indicator | `model/predict.py` → `_basis_risk_pct()` | Dynamic estimate from subregion coverage depth and elevation distance |
| ~8–12% trigger probability | Illustrative calibration | Narrower subset of stress years; exact value to be set by Person 3 + actuarial review |

### Implementation Status

| Component | Status |
|---|---|
| ERA5 climate dataset (32 sites × 30 years, 960 rows) | ✅ Implemented |
| 20-feature engineering pipeline | ✅ Implemented (`src/data/build_features.py`) |
| TerraClimate water-balance enrichment | ✅ Implemented (`src/data/fetch_terraclimate.py`) |
| Climate stress classification (rule-based, per-location) | ✅ Implemented (`src/data/make_dataset.py`) |
| Premium calculator (matching app formula) | ✅ Implemented (`pages/3_Pricing_Explainer.py`) |
| Streamlit app (4 pages: Risk, Dashboard, Pricing, Chatbot) | ✅ Implemented |
| Portuguese-language interface | ✅ Implemented |
| Trained ML risk model (LR / Random Forest) | ✅ Deployed — `model/artifacts/risk_model.joblib` |
| Risk probability outputs | ✅ Live — Random Forest ROC-AUC 0.970, blended 70/30 with historical trigger rates |
| Basis-risk estimation | ✅ Dynamic (8–22%) — `_basis_risk_pct()` in `model/predict.py` |
| Live seasonal trigger monitoring | 🔄 Simulated in demo |
| Insurer payout integration | 🔄 Future partner integration |
| Real payout execution | 🔄 Future partner integration |

---

## 8. AI Safety, Transparency, and Insurance Governance

| Risk | Why it matters | Safeguard |
|---|---|---|
| Hallucinated policy explanation | Producer may misunderstand coverage terms | Retrieval-grounded assistant; all policy terms fixed in contract text; no free-form payout promises from LLM |
| Basis risk | Real loss may not trigger payout | Explicit pre-purchase disclosure; basis-risk indicator shown in app alongside every result |
| Data privacy | Vineyard location and production data are commercially sensitive | Data minimisation; role-based access; no training on individual user data |
| Overreliance on AI premium | Insurer may accept model output without review | Human underwriting approval required before policy issuance in MVP |
| Unfair trigger calibration | Some sub-regions may be systematically undercovered | Sub-regional validation and false-negative monitoring per vintage |
| Correlated payout exposure | Extreme years may trigger mass simultaneous payouts | Insurer/reinsurer carries underwriting risk; VinhaGuard earns platform/commission revenue only |
| Regulatory misclassification | VinhaGuard may be interpreted as an unlicensed insurer | Product explicitly positioned as infrastructure layer; insurer partner holds the regulated risk carrier role |

All premium recommendations show the full formula and inputs. The system logs model inputs and pricing outputs for auditability. The app includes a clear disclaimer: policy terms are set at purchase; the LLM assistant is for explanation only and cannot modify policy conditions.

---

## 9. Go-to-Market Recommendation

| Phase | Focus | Target | Key milestone |
|---|---|---|---|
| **Pilot (Year 1)** | Heat-stress trigger, Douro Superior | 50–100 producers via 1 cooperative | Validate trigger trust, willingness to pay, and payout experience |
| **Expand (Year 2)** | Add frost and drought modules; extend to Cima Corgo | 200–500 producers | Second insurance partner; approach break-even |
| **Scale (Year 3+)** | Full Douro coverage; insurer white-label option | 800–1,000+ producers | Cross break-even; explore replication in Alentejo |

**Entry rationale:** Douro Superior has the highest documented climate exposure (72% stress classification rate; 94–100% of sites stressed in documented extreme years) and the clearest climate narrative. However, higher exposure means higher technical premiums — **affordability must be tested carefully in the pilot**.

**Pilot framing:** The year-one pilot is not a revenue exercise. It is a trust-building exercise. The questions it must answer: Do producers understand the trigger? Do they trust the data source? Does a payout feel fair? Is the cooperative willing to co-market the product?

### Go/No-Go Pilot Metrics

| Metric | Go threshold | Redesign threshold |
|---|---|---|
| Producer understanding of trigger | ≥70% correctly describe trigger after onboarding | <50% |
| Willingness to pay | ≥40% interested at target premium | <20% |
| Basis-risk complaints | <20% of payout events disputed | >35% |
| Cooperative support | Written expansion interest for Year 2 | No partner commitment |
| Technical reliability | ≥95% trigger-monitoring uptime | Frequent data gaps |

**Commercial narrative:** *VinhaGuard AI gives Douro wine producers fast, automatic liquidity when severe climate conditions cross a pre-agreed threshold — priced transparently by a model trained on 30 years of local ERA5 data, and monitored automatically throughout the growing season.*

---

## 10. Slide Structure for Final Presentation

| Slide | Action title | Key content |
|---|---|---|
| **Slide 1** | Small Douro producers face rising climate shocks without fast, trusted liquidity protection | 39.8% of location-years are stress years; 2022 = 100% of sites stressed; traditional alternatives fail smallholders; the gap is post-event liquidity, not just crop loss |
| **Slide 2** | VinhaGuard converts vineyard climate data into automatic, transparent payouts | Product workflow (vineyard → ERA5 → risk score → trigger + premium → monitoring → payout); why AI is necessary; B2B2C model; EUR 550 illustrative premium |
| **Slide 3** | The product only works if triggers are local, explainable, and commercially scalable | Local calibration / partner distribution / basis-risk transparency; platform break-even at ~833 producers; AI safety safeguards; moat = trigger-performance data + cooperative workflow integration |

*We are not building an insurance company. We are building the AI pricing and monitoring layer that helps insurers offer parametric climate-liquidity protection to small producers.*

*Person 1 owns the business case. The data pipeline (Person 2), ML model (Person 3), and Streamlit demo (Person 4) provide the technical foundation these slides reference.*

---

## References

Gouveia, C., Liberato, M. L. R., DaCamara, C. C., Trigo, R. M., & Ramos, A. M. (2011). Modelling past and future wine production in the Portuguese Douro Valley. *Climate Research*, 48, 349–362.

Jones, G. V., & Alves, F. (2012). Impacts of climate change on wine production: A global overview and regional assessment in the Douro Valley of Portugal. *International Journal of Global Warming*, 4(3/4), 383–406.

Santos, J. A., Ceglar, A., Toreti, A., & Prodhomme, C. (2020). Performance of seasonal forecasts of Douro and Port wine production. *Agricultural and Forest Meteorology*, 291, 108095.

Trigo, A., & Silva, P. (2022). Sustainable development directions for wine tourism in Douro Wine Region, Portugal. *Sustainability*, 14(7), 3949.
