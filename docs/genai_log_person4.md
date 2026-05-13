# VinhaGuard AI — GenAI Transparency Log (Frontend & Integration Lead)

## Overview

This log documents the use of AI tools in the Frontend & Integration Lead's contribution to VinhaGuard AI (Person 4 of 4). The scope of work covered is the full Streamlit application: initial repository structure, multi-page app scaffold, all five page implementations (Home, Risk Assessment, Climate Dashboard, Pricing Explainer, AI Chatbot), integration with the ML pricing backend, translation to English, and iterative UI refinement across multiple commits.

**Claude Code** (VS Code extension, powered by Claude Sonnet) was used as the primary AI tool throughout. Its role was to scaffold page layouts, draft component code, suggest styling approaches, debug integration errors with `model/predict.py`, and iterate on the UI based on direction given by the Frontend Lead. All architectural decisions, design choices, content decisions, and integration logic were reviewed and approved by the Frontend Lead before any commit.

---

## Tools and Roles

| Tool | Role in this work | Examples |
|---|---|---|
| **Claude Code** (VS Code extension) | Code generation, layout scaffolding, debugging, iterative UI refinement | Writing `app.py` navigation; drafting page layouts; debugging `predict_risk_and_premium()` integration; writing the Gemini chatbot wrapper; iterating on CSS styling |
| **Gemini 2.5 Flash Lite** (via Google GenAI SDK) | Production LLM powering the in-app AI assistant (`pages/4_Chatbot.py`) | Not a development tool; documented here because it is a core product component |

---

## Workflow by Contribution

### 1. Repository structure and initial scaffold (`6e9edc2`)

The Frontend Lead reviewed the existing repository state after the Data Lead (Person 2) had committed the pipeline scripts. Claude Code was asked to propose a clean folder structure separating `src/data/`, `data/`, `docs/`, `model/`, `pages/`, and `notebooks/`, and to scaffold an initial `app.py` with Streamlit multi-page navigation. The Frontend Lead approved the structure and directed the removal of any placeholder pages that duplicated Person 2's pipeline work.

### 2. Translation of app messages to English (`be50358`)

Early app messages and UI labels were in mixed languages. The Frontend Lead directed Claude Code to audit all user-facing strings across `app.py` and the `pages/` directory and translate them consistently to English, to allow the full team to read and review the interface during development. Claude Code produced a diff; the Frontend Lead reviewed every changed string before accepting.

### 3. UI cleanup and category improvements (`fff6292`)

The risk type categories and subregion labels were inconsistent across pages. The Frontend Lead identified the discrepancies and directed Claude Code to standardise the dropdown and radio button options, align them with the canonical subregion names in `model/predict.py`, and clean up the sidebar navigation labels. The decision to keep six location options (three IVDP profiles plus three familiar demo aliases) was made by the Frontend Lead in coordination with the ML Lead (Person 3), not suggested by Claude Code.

### 4. Chatbot — Gemini API integration and system prompt (`b938f45`)

The Frontend Lead decided to replace an earlier placeholder chatbot implementation with a production-quality FAQ assistant powered by the Gemini 2.5 Flash Lite API. Claude Code was used to:
- Write the `genai.Client` setup and `build_history()` conversation-formatting function
- Implement streaming response rendering with a live cursor
- Add a `@st.cache_resource` API client to avoid re-initialising on every rerun

The **system prompt** (`SYSTEM_PROMPT` in `pages/4_Chatbot.py`) was written by the Frontend Lead. Its content — product knowledge, guardrails, tone instructions, coverage types, pricing formula, model metrics, and basis-risk explanation — was specified and reviewed by the Frontend Lead drawing on the business report (Person 1) and ML handoff document (Person 3). Claude Code drafted an initial version; the Frontend Lead revised it substantially to ensure accuracy against the actual codebase figures (ROC-AUC 0.970, Brier score, trigger thresholds, 8–22% basis risk range). The decision to use `temperature=0.3` and `max_output_tokens=1024` was a human judgment call to keep responses focused and factual.

The guardrail design — restricting the assistant to VinhaGuard topics and declining off-topic questions with a single redirect sentence — was a human product decision, not an AI suggestion.

### 5. Risk Assessment and Dashboard alignment (`78b08f3`, `fc7b01e`)

After Person 3 (ML Lead) deployed the trained Random Forest backend and updated `model/predict.py`, the frontend needed to be realigned with the new trigger thresholds and risk type options. The Frontend Lead directed Claude Code to:
- Update the risk type radio buttons on the Risk Assessment page to use the options accepted by `_normalise_risk_type()`
- Add the trigger alignment diagnostic scatter chart to the Dashboard (Chart 3 in `pages/2_Dashboard.py`) to surface basis-risk mismatches visually
- Add the model performance figures section (ROC, PR curve, confusion matrix, calibration, feature importance tabs) to the Dashboard

The trigger alignment diagnostic — comparing when the specific trigger fires vs. when the broader climate-stress proxy is active — was a design idea from the Frontend Lead, intended to make basis risk concrete and visual rather than just a stated percentage. Claude Code implemented the scatter chart using Plotly; the Frontend Lead wrote the explanatory text in the sidebar column.

The Frontend Lead also directed that the Dashboard should include a note distinguishing the trigger alignment chart from true basis risk (which would require yield or claims data not available in the prototype). This honest framing was a human decision.

### 6. Pricing calculations and dashboard diagnostics (`fc7b01e`)

The Frontend Lead directed Claude Code to add a waterfall chart to the Pricing Explainer page to make the premium build-up steps concrete and visual. The Frontend Lead specified which components to include (expected payout, risk loading, admin cost, margin), reviewed the Plotly `go.Waterfall` implementation, and confirmed the values matched the formula in `pages/3_Pricing_Explainer.py`. The parametric vs. traditional insurance comparison table was written by the Frontend Lead.

### 7. Risk type options and dashboard styling (`2bbe1a7`)

After integration testing revealed that the "All" risk type label shown in the UI was being passed through correctly to the backend (which normalises it to "Both"), the Frontend Lead directed Claude Code to audit the label consistency across all pages and fix any cases where dropdown options and backend-expected strings were misaligned. Sidebar CSS, metric card styling, and colour consistency were also refined in this commit.

---

## What Was Decided by the Frontend Lead

- **Choice of Gemini 2.5 Flash Lite** as the chatbot LLM: selected for its speed, cost, and availability via the Google GenAI SDK. The Frontend Lead evaluated the API against the project's prototype constraints.
- **System prompt content and guardrails**: the full text of `SYSTEM_PROMPT` was specified by the Frontend Lead using the business report, data dictionary, and ML handoff as source material. Claude Code drafted; the Frontend Lead revised for accuracy.
- **Temperature (0.3) and token limit (1024)**: human judgment calls for a factual FAQ assistant.
- **Trigger alignment diagnostic chart**: the idea and the explanatory framing ("model-level diagnostic, not a direct measure of basis risk") were human decisions.
- **Six location options in dropdowns**: the decision to show three IVDP profiles plus three familiar demo aliases, with transparent profile-mapping notes, was made in coordination with the ML Lead.
- **Parametric vs. traditional comparison table content**: written by the Frontend Lead, not generated by AI.
- **Professional tone without emojis**: a deliberate product positioning choice.
- **All page structure, section ordering, and UX flow**: the Frontend Lead specified what each page should contain and in what order; Claude Code implemented.

---

## What Was Checked

- All six subregion inputs were tested against `_normalise_subregion()` to confirm no `ValueError` is raised.
- The risk type options ("Heat", "Frost", "Drought", "All") were confirmed to round-trip correctly through `_normalise_risk_type()`.
- The premium breakdown figures displayed on the Risk Assessment page were spot-checked against manual calculations using the formula in the Pricing Explainer.
- The chatbot system prompt figures (ROC-AUC 0.970, 0.949; Brier scores; trigger thresholds; 8–22% basis risk) were verified against `model/artifacts/metrics.json` and `model/predict.py`.
- The dashboard trigger alignment chart was confirmed to load correctly for all three canonical subregions and all four risk types.
- The app was run end-to-end (`streamlit run app.py`) after each major commit to confirm no import errors or page crashes.
- `python -m compileall pages app.py` was run to verify syntax before final commits.

---

## Limitations

- Approximately **90%+ of the implementation code** in `pages/` and `app.py` was generated by Claude Code under detailed specification from the Frontend Lead. The Frontend Lead's contribution was specification, direction, review, content decisions, and integration judgment — not typing code from scratch.
- The **system prompt** is the most human-authored artefact in the Frontend Lead's deliverable. Its accuracy depends on the business report and ML handoff being correct; errors in those upstream documents propagate into the chatbot's product knowledge.
- The chatbot uses Gemini, not a retrieval-augmented system. There is no live connection to the dataset or model artifacts at inference time — product knowledge is baked into the system prompt. This means the chatbot cannot answer questions about a specific user's quote or real-time trigger status.
- The **trigger alignment diagnostic** compares trigger firing against the climate-stress proxy label, not against actual farm losses. As noted explicitly in the chart explanation, this is a model-level diagnostic, not a validated basis-risk measure.
- The **"All" / "Both" label inconsistency** identified in the project review (the UI shows "All" while the backend uses "Both" internally) was partially addressed in `2bbe1a7` but may still surface in edge cases across pages. A future cleanup should standardise the user-facing label to "All (Heat + Frost + Drought)" throughout.

---

## Files Produced

- `app.py`
- `pages/home.py`
- `pages/1_Risk_Assessment.py`
- `pages/2_Dashboard.py`
- `pages/3_Pricing_Explainer.py`
- `pages/4_Chatbot.py`
- `.streamlit/config.toml`
