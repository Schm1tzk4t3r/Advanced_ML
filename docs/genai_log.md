# VinhaGuard AI - GenAI Transparency Log

## Purpose

This document records how generative AI tools were used during the VinhaGuard AI
project. It is included to satisfy the project requirement that external and AI
assistance be acknowledged transparently.

The final product decisions, business logic, modelling choices, pricing
assumptions, limitations, and submitted files were reviewed and accepted by the
team. GenAI tools were used as assistants for ideation, drafting, coding,
debugging, and consistency checking; they were not treated as autonomous
decision-makers.

## Tools Used

| Tool | Used for |
|---|---|
| Claude / Claude Code | Early project structuring, business drafting, data-pipeline scaffolding, frontend scaffolding, notebook/code generation, debugging, and documentation drafts |
| ChatGPT / Codex | Repository review, TerraClimate research and integration, ML training workflow, pricing backend review, documentation cleanup, final consistency pass |
| Gemini 2.5 Flash Lite | In-app AI assistant for product/support questions inside the Streamlit prototype |

## Business and Insurance Work

GenAI assisted with:

- synthesising the business problem and target customer;
- drafting and revising the business report;
- checking that the premium formula was consistent across the report and app;
- developing the unit-economics notebook structure;
- clarifying the distinction between climate-stress probability and payout
  trigger probability;
- documenting basis risk, go-to-market logic, and regulatory limitations.

Human decisions included:

- positioning VinhaGuard as a B2B2C infrastructure layer rather than a regulated
  insurer;
- selecting parametric insurance as the product format;
- defining the MVP as fast climate-liquidity protection, not full crop-loss
  compensation;
- choosing the revenue model and pilot assumptions;
- reviewing and correcting affordability, basis-risk, and underwriting claims.

## Data Pipeline Work

GenAI assisted with:

- repository structure recommendations;
- scripts for location generation, weather fetching, feature engineering, and
  target labelling;
- API debugging for Open-Meteo rate limits;
- data dictionary and data-source documentation;
- exploratory notebook generation and validation summaries.

Human decisions included:

- choosing the Douro Valley and IVDP subregions as the domain;
- using representative vineyard locations rather than real private quinta data;
- accepting 32 of 36 fetched locations because subregion coverage remained
  balanced;
- using per-location percentile thresholds to avoid unfair global trigger
  thresholds across naturally different subregions;
- validating known extreme years such as 2003, 2005, 2017, 2022, and 2024.

## ML and Pricing Work

GenAI assisted with:

- reviewing the existing data and app state;
- implementing `model/train.py`;
- training a Logistic Regression baseline and Random Forest main model;
- adding TerraClimate water-balance features through
  `src/data/fetch_terraclimate.py`;
- replacing mock pricing logic with a backend that loads trained model
  artifacts;
- generating evaluation charts and model metrics;
- documenting model limitations and pricing logic.

Human-reviewed modelling choices included:

- using a chronological split: 1995-2019 for training, 2020-2024 for testing;
- adding GroupKFold by location as a robustness check;
- deploying the Random Forest because it had the strongest ranking performance;
- retaining Logistic Regression as an interpretable baseline;
- avoiding heavier dependencies such as XGBoost shortly before submission;
- framing the target honestly as a climate-trigger proxy, not real claims or
  yield loss;
- avoiding fake future-weather inputs at quote time.

## Frontend and Integration Work

GenAI assisted with:

- Streamlit page scaffolding;
- UI copy and layout iteration;
- integration with `model.predict.predict_risk_and_premium()`;
- pricing explainer charts;
- dashboard charts and model-performance displays;
- chatbot system-prompt drafting and guardrail refinement.

Human decisions included:

- the final page structure and product workflow;
- the decision to show three canonical IVDP risk profiles plus familiar demo
  location aliases;
- the wording of key disclaimers and basis-risk explanations;
- the choice to keep the chatbot constrained to VinhaGuard-related topics;
- final review of user-facing claims and model metrics.

## In-App AI Assistant

The Streamlit app includes a Gemini-powered assistant. It is intentionally scoped
to:

- VinhaGuard product questions;
- parametric insurance explanations;
- Douro climate-risk context;
- app usage guidance.

Guardrails instruct it not to answer unrelated topics, not to make binding policy
promises, and to state clearly that VinhaGuard is an academic prototype rather
than a licensed insurance product. It cannot change premiums, triggers, policy
terms, or payout decisions.

## Important Corrections Made During Review

The team used GenAI to identify and correct several issues before submission:

- replaced early mock risk outputs with a trained model backend;
- added TerraClimate water-balance data so drought risk was not based only on
  rainfall-count assumptions;
- aligned heat-trigger wording around the severe-event threshold of at least 5
  days above 38 C;
- removed unprofessional role-numbered references from public documentation;
- aligned documentation with the actual calibrated Random Forest artifact used
  by the pricing backend;
- updated README and documentation to match the final deployable architecture.

## Verification Assisted by GenAI

The final consistency pass included:

- Python syntax compilation for `model`, `src`, and `pages`;
- dataset shape and missing-value checks;
- TerraClimate feature checks;
- model training verification;
- inference smoke tests across regions and risk types;
- Streamlit smoke testing for the Risk Assessment and Dashboard pages;
- repository text scans for stale role-numbered references and outdated model
  claims.

## Limitations of GenAI Use

GenAI-generated drafts required human review. The most important risks were:

- overconfident wording around model accuracy;
- confusion between climate-stress probability and payout-trigger probability;
- stale documentation after model and data changes;
- possible hallucinated implementation details if documentation was not checked
  against code.

The final repository mitigates these risks by documenting assumptions, exposing
the premium formula, citing data sources, preserving reproducible scripts, and
stating the prototype limitations explicitly.
