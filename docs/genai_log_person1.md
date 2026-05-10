# VinhaGuard AI — GenAI Transparency Log (Business & Insurance Lead)

## Overview

This log documents the use of AI tools in the Business & Insurance Lead's contribution to VinhaGuard AI (Person 1 of 4). The scope of work covered is the full business case: problem framing, market analysis, parametric product concept, revenue model, unit economics, fairness and basis risk, and go-to-market strategy.

Claude (via the Cowork desktop app, powered by Claude Sonnet) was used as an AI support tool throughout this work. Its role was to assist with drafting, consistency checking, repository summarisation, and Python notebook development. The project concept, business logic, academic references, financial assumptions, and all final decisions were defined and reviewed by the Business Lead. No other AI tools were used.

---

## What AI Was Used For

**Repository synthesis.** The Business Lead asked Claude to read all existing project files — including the Streamlit app, pricing explainer, risk assessment page, model assumptions, data dictionary, and the data lead's handoff document — and summarise the technical state of the prototype. This was used to align the business report with what the team had actually built, particularly the premium formula, sub-regional risk probabilities, trigger conditions, and dataset statistics.

**Drafting and revision.** Claude produced initial drafts of the business report and unit economics notebook based on the Business Lead's source document and verbal direction. These drafts were reviewed, corrected, and revised multiple times. The most significant revision came after the Business Lead identified that an early draft did not adequately distinguish between the model's climate stress classification rate and the calibrated payout trigger probability — a conceptually important distinction that Claude had not handled correctly in the first version.

**Consistency checking.** Claude was used to cross-check that the premium formula in the report matched the Pricing Explainer page, that the break-even calculation used a single consistent average premium, and that basis risk was labelled correctly as a prototype indicator rather than an actuarial estimate.

**Python notebook development.** Claude generated the code for `unit_economics.ipynb` under the Business Lead's specification. The Business Lead defined the analytical structure (what to model and why), reviewed each cell, and identified corrections — including the trigger probability labelling, the break-even figure, and the basis risk simulation setup.

---

## What Humans Decided

The following were human-led decisions, not AI outputs:

- **Business thesis.** The framing of VinhaGuard AI as parametric climate *liquidity* protection (not full crop indemnity), the B2B2C model with a licensed insurer partner, and the positioning of fast payout as the core value proposition were all established by the Business Lead and the team prior to this session.

- **Target segment and pilot region.** The decision to focus on small and medium-sized Douro producers and to enter through Douro Superior was a team choice, informed by the literature and by the dataset findings reviewed by the Business Lead.

- **Academic references.** All four references (Gouveia et al. 2011; Jones & Alves 2012; Santos et al. 2020; Trigo & Silva 2022) were identified and sourced by the Business Lead from prior reading. Claude did not conduct independent literature review.

- **Financial assumptions.** The MVP product parameters (EUR 5,000 payout, ~8% calibrated trigger probability, 12% commission, EUR 80,000 fixed costs) were set by the Business Lead. Claude assisted with the arithmetic but did not choose these figures.

- **Corrections to AI drafts.** The Business Lead identified the premium logic inconsistency (pricing on the full stress rate rather than a calibrated severe-event trigger), the break-even contradiction between two different average premium assumptions, and the overconfident framing of the 12.5% basis-risk figure. These corrections shaped the final versions of all deliverables.

- **Review and approval.** All outputs — report, notebook, and this log — were reviewed by the Business Lead before being committed to the repository.

---

## What Was Checked

- Premium formula confirmed to match `pages/3_Pricing_Explainer.py`
- Sub-regional stress probabilities confirmed against `model/predict.py`
- Known-year validation table confirmed against `docs/data_dictionary.md`
- Break-even calculation verified to use a single consistent average premium (EUR 550) throughout
- Basis risk language confirmed to read as "prototype indicator," not actuarial estimate
- Payout time confirmed to read as a design target, not a guaranteed operational commitment

---

## Limitations

- The premium figures and break-even calculation are illustrative MVP assumptions. They depend on the mock risk probabilities currently in `model/predict.py` and will need to be revised once Person 3's trained model is available.
- The 12.5% basis-risk indicator is a prototype placeholder. Actual basis risk would require formal actuarial calibration based on trigger design and ERA5 grid resolution.
- The break-even scale (~833 producers) reflects full operating costs (EUR 80,000 fixed). A lean pilot could operate at lower fixed costs, but this has not been modelled here.
- All code in `unit_economics.ipynb` was generated with Claude as a drafting tool. The Business Lead reviewed and directed the analysis but did not write the code independently.

---

## References

Jones, G. V., & Alves, F. (2012). Impacts of climate change on wine production: A global overview and regional assessment in the Douro Valley of Portugal. *International Journal of Global Warming*, 4(3/4), 383–406.

Santos, J. A., Ceglar, A., Toreti, A., & Prodhomme, C. (2020). Performance of seasonal forecasts of Douro and Port wine production. *Agricultural and Forest Meteorology*, 291, 108095.

Gouveia, C., Liberato, M. L. R., DaCamara, C. C., Trigo, R. M., & Ramos, A. M. (2011). Modelling past and future wine production in the Portuguese Douro Valley. *Climate Research*, 48, 349–362.

Trigo, A., & Silva, P. (2022). Sustainable development directions for wine tourism in Douro Wine Region, Portugal. *Sustainability*, 14(7), 3949.
