# VinhaGuard AI — Person 1: Business & Insurance Lead

> **Role:** Business & Insurance Lead  
> **Focus:** Problem framing, market logic, product concept, revenue model, unit economics, fairness & basis risk, go-to-market  
> **Output:** Business slides (2–3), financial logic, GTM strategy, market/problem sources

---

## Executive Summary

VinhaGuard AI is a data-driven **parametric climate insurance** product for small and medium-sized wine producers in the Douro Valley (Trigo & Silva, 2022; Jones & Alves, 2012). The product addresses a clear protection gap: climate shocks are increasingly relevant to vineyard economics, while traditional crop insurance is often too slow, complex, and costly for smaller producers.

The core innovation is converting climate risk into **predefined, transparent weather or vegetation triggers**. When a trigger is breached, the payout is made automatically — no post-loss field inspection required. The strongest business setup is not to position VinhaGuard AI as a fully regulated insurer, but as a **digital pricing and monitoring layer** partnered with a licensed insurer (e.g., Fidelidade, MAPFRE, or a cooperative insurance structure).

---

## 1. Business Problem and Relevance

The Douro Valley is one of Portugal's most economically important wine regions — nearly **45,000 hectares** of vineyards, ~22% of Portugal's vineyard area, and over 40% of Portuguese wine exports (Santos et al., 2020). Yet it is also highly exposed to weather variability and climate change.

The region is not homogeneous. Steep hillside vineyards, strong sub-regional differences, and a pronounced east–west precipitation gradient (Trigo & Silva, 2022; Santos et al., 2020) make it difficult to insure through a single standardised product.

Climate change intensifies the urgency. Research already documents higher growing-season temperatures, more extreme heat events, and declining precipitation — with the greatest pressure in the warmer, drier **Douro Superior** (Jones & Alves, 2012). For producers, these are not only agronomic problems: heat stress, frost, drought, or rainfall anomalies reduce yield, damage quality, disrupt cash flow, and create acute liquidity needs.

**Central problem:** Small and medium-sized Douro wine producers face increasing climate-related income risk, but existing insurance solutions are too slow, complex, or costly to provide reliable post-event liquidity. VinhaGuard AI closes this gap.

---

## 2. Target Customers and Market Logic

**Primary customers:** Small and medium-sized wine producers in the Douro Valley — particularly family farms and cooperative members. The Douro Demarcated Region counts approximately **20,000 farmers** with an average vineyard holding of ~2 hectares (Trigo & Silva, 2022). This group combines high climate exposure with limited financial buffers.

**Why this segment?**
- Large producers can diversify across plots, varieties, and reserves; small farms cannot.
- Smallholders are more exposed to single-location climate events.
- A delayed payout after a climate shock forces producers to fund labour, vineyard recovery, debt service, and possibly replanting entirely from their own pocket.

**Go-to-market model:** Business-to-Business-to-Customer (B2B2C)

| Layer | Role |
|---|---|
| **VinhaGuard AI** | Data infrastructure, risk scoring, premium calculation, trigger monitoring, Portuguese-language customer dashboard |
| **Insurance partner** (insurer / cooperative / association) | Underwriting capacity, regulatory legitimacy, distribution network |
| **End customer** (wine producer) | Policy holder; receives automatic payout on trigger |

**Secondary customers:** Insurers and cooperatives seeking operational efficiency — lower claims administration costs, clearer trigger rules, and a scalable way to serve smaller agricultural clients.

---

## 3. Product Concept and Insurance Logic

VinhaGuard AI is a **parametric insurance platform**. Unlike traditional indemnity insurance (which compensates after an assessed loss), parametric insurance pays out when a **predefined external trigger** is breached.

### Example Trigger Products

| Product | Trigger condition | Key data source |
|---|---|---|
| Heat-stress | ≥14 consecutive days above 38°C during veraison | Weather grid / ERA5 |
| Frost | Temperature below threshold during budbreak | Ground station / satellite |
| Drought | Rainfall deficit or soil-moisture anomaly over growth period | SNIRH / ERA5 / NDVI |
| Vegetation stress | Abnormal NDVI decline relative to historical baseline | Sentinel-2 / MODIS |

**Key design principle:** Triggers must be simple enough for producers to understand, yet precise enough to reduce mismatch between the measured event and the actual economic loss (basis risk — see Section 7).

**Technical foundation:** Research confirms that temperature, precipitation, and NDVI-based vegetation indicators can model Douro wine production and vineyard behaviour (Gouveia et al., 2011). Seasonal forecast models have also been validated for Douro and Port wine production (Santos et al., 2020).

**Product promise:** VinhaGuard AI does not eliminate climate risk, nor guarantee full loss compensation. Its promise is narrower and more credible: **fast, transparent, rules-based liquidity when a measurable climate shock occurs**.

---

## 4. Business Model and Revenue Mechanism

VinhaGuard AI operates as a **hybrid SaaS + insurance distribution layer**:

| Revenue stream | Description |
|---|---|
| Annual platform fee per vineyard | Covers dashboard, data integrations, customer support |
| Commission on gross written premium | Typically 10–15% of GWP, aligned with portfolio growth |

**Main cost drivers:**

- Weather and satellite data access
- ML model development and maintenance
- Dashboard hosting and customer onboarding
- Compliance support and partnership management
- (Lower) claims handling — no field inspection required

**MVP launch strategy:** Narrow pilot with 50–100 producers in the Douro Superior, focused on heat-stress and drought-risk triggers. This is sufficient to validate: willingness to pay, trigger clarity, basis risk perception, and trust in the payout mechanism.

---

## 5. Financial Logic and Unit Economics

The parametric model allows transparent, explainable pricing. The **simplified technical premium formula** is:

```
Technical Premium = P(trigger) × Payout Amount
Commercial Premium = Technical Premium + Admin & Data Costs + Risk Margin + Platform Margin
```

### Illustrative Premium Calculation

| Input | Illustrative assumption |
|---|---|
| Insured payout | EUR 5,000 |
| Estimated trigger probability | 8% |
| Expected payout cost | EUR 400 |
| Administration & data cost | EUR 40 |
| Risk margin | EUR 60 |
| Platform margin | EUR 50 |
| **Final annual premium** | **EUR 550** |

**Loading ratio:** 37.5% above expected loss (competitive for parametric agricultural insurance)

**Why this works economically:**
- As the portfolio grows across locations, geographic diversification reduces concentration of payout risk.
- Because payouts are deterministic, the insurer can model portfolio risk using historical weather data, seasonal forecasts, satellite indicators, and vineyard location data.
- Claims handling costs are substantially lower than traditional crop insurance (no field assessment).

### Sensitivity Analysis

| Trigger probability | Payout (EUR) | Technical premium | Commercial premium |
|---|---|---|---|
| 5% | 5,000 | 250 | 400 |
| 8% | 5,000 | 400 | 550 |
| 12% | 5,000 | 600 | 750 |
| 8% | 8,000 | 640 | 790 |
| 8% | 3,000 | 240 | 390 |

---

## 6. Competitive Positioning

| Alternative | Key weakness |
|---|---|
| Self-insurance | Requires reserves small producers typically lack |
| Public disaster aid | Uncertain timing, often delayed |
| Bank credit | Increases debt precisely when financial pressure is highest |
| Traditional crop insurance | Complex underwriting, slow claims, less suited to small farms |

**VinhaGuard AI differentiates through:**
1. **Speed** — payout triggered by verified data, not a field inspector's schedule
2. **Transparency** — trigger defined before purchase; producer knows exactly what is covered
3. **Local relevance** — premium and trigger calibrated to vineyard location, sub-region, and climate exposure
4. **Language & accessibility** — Portuguese-language onboarding and claims assistant

The strongest competitive message: *not necessarily cheaper, but easier to understand, easier to administer, and better suited to climate-driven liquidity needs.*

---

## 7. Fairness, Trust, and Basis Risk

**Basis risk** is the principal limitation of parametric insurance: the trigger may not perfectly match the producer's actual loss. A producer could experience real damage without receiving a payout (trigger not breached), or receive a payout when actual damage was limited.

**Why basis risk is especially significant in the Douro:**
- Vineyard conditions vary sharply across sub-regions, elevations, slopes, and microclimates (Trigo & Silva, 2022; Santos et al., 2020).
- A single regional trigger would create systematically unfair outcomes.

**Mitigation strategies:**
- Location-specific weather grids and satellite indicators
- Sub-regional trigger calibration (Douro Superior vs. Cima Corgo vs. Baixo Corgo)
- Transparent basis risk disclosure in onboarding — hiding this limitation would damage long-term credibility

**Social fairness:**
- Product designed for smallholders via cooperatives and modular coverage levels
- Low minimum coverage, simple enrollment, group distribution
- Strengthens the ESG narrative: supports climate adaptation for smaller agricultural actors

**Trust by design:** Producers must know the exact trigger, data source, payout amount, waiting period, and what is *not* covered. Transparency about limitations is more professional than promising perfect protection.

---

## 8. Go-to-Market Recommendation

| Phase | Focus | Target |
|---|---|---|
| **Pilot (Year 1)** | Heat-stress + drought triggers in Douro Superior | 50–100 producers via 1 cooperative partner |
| **Expand (Year 2)** | Add frost and rainfall-deficit modules; extend to Cima Corgo | 200–500 producers |
| **Scale (Year 3+)** | Full Douro coverage; explore replication in Alentejo / Vinho Verde | 1,000+ producers; insurer white-label |

**Pilot entry rationale:** Douro Superior is the most exposed sub-region to warming and precipitation decline (Jones & Alves, 2012). The value proposition is easiest to demonstrate where the climate pressure is most intuitive.

**Commercial narrative:** *VinhaGuard AI provides fast climate-risk liquidity for Douro wine producers, paid automatically when predefined weather conditions cross an agreed threshold.*

---

## 9. Slide Structure for Final Presentation

| Slide | Action title | Key content |
|---|---|---|
| **Slide 1** | Climate volatility creates a protection gap for small Douro wine producers | Problem, market size, existing alternatives and their failures |
| **Slide 2** | Parametric insurance turns climate data into automatic, transparent payouts | Trigger-to-payout flow, premium formula, B2B2C model |
| **Slide 3** | The product wins only if triggers are local, explainable, and trusted | Basis risk, fairness, go-to-market, pilot plan |

*Person 1 owns these 3 slides. Technical modelling details (data pipeline, ML architecture, pricing engine) belong to Persons 2, 3, and 4.*

---

## References

Gouveia, C., Liberato, M. L. R., DaCamara, C. C., Trigo, R. M., & Ramos, A. M. (2011). Modelling past and future wine production in the Portuguese Douro Valley. *Climate Research*, 48, 349–362.

Jones, G. V., & Alves, F. (2012). Impacts of climate change on wine production: A global overview and regional assessment in the Douro Valley of Portugal. *International Journal of Global Warming*, 4(3/4), 383–406.

Santos, J. A., Ceglar, A., Toreti, A., & Prodhomme, C. (2020). Performance of seasonal forecasts of Douro and Port wine production. *Agricultural and Forest Meteorology*, 291, 108095.

Trigo, A., & Silva, P. (2022). Sustainable development directions for wine tourism in Douro Wine Region, Portugal. *Sustainability*, 14(7), 3949.
