# VinhaGuard AI — GenAI Transparency Log (Data Lead)

## Overview

This log documents the use of AI tools in the Data Lead's contribution to VinhaGuard AI (Person 2 of 4). The scope of work covered is the full data pipeline: defining the 36-site vineyard location list, fetching 30 years of daily weather from Open-Meteo, engineering 20 climate features at the location-year level, labelling climate stress years, writing reference documentation, and producing the exploratory data analysis notebook. Two AI tools were used throughout: **Claude Code** (the VS Code extension, powered by Claude Sonnet) for all file creation and code execution; and **Claude** (via claude.ai) for upstream planning tasks — repo structure design, prompt engineering for Claude Code, code review, debugging rate-limit issues, label-rule design, and validation interpretation. No other AI tools were used.

---

## Tools and Roles

| Tool | Role in this work | Examples |
|---|---|---|
| **Claude** (claude.ai web interface) | Strategic planning, design review, debugging, prompt engineering | Reviewing and approving the repo structure proposal; designing the per-location percentile labelling rule; diagnosing Open-Meteo 429 rate-limit errors; refining prompts before passing them to Claude Code |
| **Claude Code** (VS Code extension) | All file creation and code execution | Scaffolding the repo; writing `locations.py`, `fetch_weather.py`, `build_features.py`, `make_dataset.py`; generating `data_dictionary.md`, `data_sources.md`; building and executing the EDA notebook; staging and committing all changes |
| **Open-Meteo Historical Weather API** | Primary data source (ERA5-based daily weather, 1995–2024) | Not an AI tool; documented here for completeness. Provided `temperature_2m_max/min/mean` and `precipitation_sum` at daily resolution for each vineyard site |

---

## Workflow by Pipeline Stage

### 1. Repo structure review and reconciliation

Claude Code inspected the existing repository and proposed a reconciled folder structure — separating `src/data/`, `data/raw/`, `data/interim/`, `data/processed/`, `docs/`, and `notebooks/` — and explained the rationale for each choice. The Data Lead reviewed the full proposal before approving any file moves or writes, and rejected one suggested change (moving the Streamlit `pages/` directory) to avoid breaking the existing demo. Once approved, Claude Code executed all renames, updated `.gitignore` and `requirements.txt`, and rewrote `README.md`.

### 2. Location list (`data/locations.csv`, 36 → 32 sites)

The Data Lead specified the target sample: 36 vineyard sites distributed across the three IVDP Douro sub-regions (Baixo Corgo, Cima Corgo, Douro Superior), with realistic coordinates, elevation ranges, and ID conventions (`BC##`, `CC##`, `DS##`). Claude Code wrote `src/data/locations.py` and generated the CSV. The subregion split (BC 12, CC 14, DS 10) and the decision to use hand-curated representative coordinates — rather than real quinta locations — were human choices reflecting the project's insurance-prototype context. During the weather fetch phase, four sites (CC03, CC12, DS05, DS10) could not be retrieved within the project timeline; the Data Lead added a `weather_data_available` column and decided to proceed with the remaining 32 rather than delay the pipeline.

### 3. Weather data fetcher (Open-Meteo, with rate-limit handling)

Claude Code wrote `src/data/fetch_weather.py` to call the Open-Meteo Historical Weather API with exponential-backoff retry logic and a tqdm-safe logging handler. The initial sleep interval (1.2 s) triggered persistent HTTP 429 errors; after diagnosis via Claude on claude.ai, the interval was progressively increased to 20 s, yielding 32 successful fetches across multiple runs. The Data Lead monitored each run, interpreted the rate-limit failures, and made the call to stop retrying after four attempts and proceed with 32 locations. Output was spot-checked by reading `data/raw/weather/BC01.parquet` and confirming 10,958 rows, four columns, and zero missing values.

### 4. Feature engineering (20 climate features at location-year level)

The Data Lead specified the feature set — heat-day counts at three thresholds (30/35/38 °C), summer temperature statistics (JJA window), heatwave streak length, growing degree days (base 10 °C, April–October), spring frost indicators (March–May window at 0 °C and −2 °C), and drought metrics (annual and summer precipitation, dry-day count, max consecutive dry days) — drawing on standard viticultural climate-indicator conventions. Claude Code translated these specifications into `src/data/build_features.py`, implementing the `_max_streak()` run-length helper and the `_year_features()` quality-control check (drop year if < 90% daily completeness). The Data Lead validated the output by confirming the expected sub-regional heat gradient (Douro Superior 12.3 > Cima Corgo 5.7 > Baixo Corgo 3.3 mean heat days ≥ 35 °C) against published Douro climatology, and confirmed 0 QC drops.

### 5. Label design (`climate_stress_year`, per-location 80th-percentile rule)

The labelling rule — a binary `climate_stress_year = 1` flag triggered by any of: (a) anomalous heat (heat_days_35 ≥ per-location 80th percentile), (b) spring frost event (spring_severe_frost_days ≥ 3), or (c) anomalous drought (max_consecutive_dry_days ≥ per-location 80th percentile) — was designed by the Data Lead in discussion with Claude on claude.ai. The critical design decision was **per-location percentiles rather than global thresholds**: Douro Superior vineyards regularly record 8–12 °C higher summer temperatures than Baixo Corgo, so a globally-computed threshold would systematically over-label Douro Superior and under-label Baixo Corgo regardless of whether a year was anomalous for that site. The per-location approach encodes relative climate anomaly — the ecologically and actuarially meaningful signal for parametric insurance trigger calibration. This was a deliberate methodological choice, not a default. Claude Code implemented the rule in `src/data/make_dataset.py` using `groupby().transform()` to broadcast per-location quantiles without a merge. The Data Lead validated the output against ten independently documented Iberian extreme and mild years (see [Human Validation and Oversight](#human-validation-and-oversight)).

### 6. Documentation (`data_dictionary.md`, `data_sources.md`)

Claude Code drafted both documentation files based on specifications provided by the Data Lead: a 21-column reference table covering every field in `vinhaguard_dataset.parquet` (including units, source, and derivation), and a four-source citation document covering Open-Meteo, ERA5/ECMWF, IVDP, and IPMA, with a limitations section on rate-limited fetch coverage, ERA5 grid basis risk, NDVI exclusion, and the legacy synthetic placeholder. The Data Lead reviewed both files for accuracy, confirmed that the DOIs and API URLs were correct, and added the caveat about the `douro_climate.parquet` synthetic file to prevent Person 3 from accidentally using it for model training.

### 7. EDA notebook (`notebooks/01_data_exploration.ipynb`)

The Data Lead specified the nine sections of the exploratory analysis — dataset load, shape and dtypes, missing-value check, distribution histograms by sub-region, heat-trend time series with known extreme-year markers, class-balance bar chart, year-level stress count, correlation heatmap, and a written summary with data-quality and red-flag tables. Claude Code wrote the builder script (`_build_nb.py` using `nbformat`) and executed the notebook via `jupyter nbconvert --execute`. All plots use the IVDP sub-region colour palette (Baixo Corgo: `#1976D2`, Cima Corgo: `#F57C00`, Douro Superior: `#C62828`) specified by the Data Lead. The Data Lead visually confirmed that the rendered outputs matched the expected patterns described in the section headers (e.g., DS shifted right on heat histograms; clear 2003/2005/2017/2022/2024 peaks in the year-level stress chart).

---

## Human Validation and Oversight

The following validation steps were performed by the Data Lead, not the AI:

- Reviewed Claude Code's structural proposal in full before approving any file moves or writes; rejected one change that would have broken the existing Streamlit demo.
- Verified weather data quality after the first 16 successful location fetches by inspecting `data/raw/weather/BC01.parquet` directly (10,958 rows, 4 columns, 0 missing values).
- Diagnosed the root cause of Open-Meteo 429 errors (burst rate limit on free tier) and directed the fix — progressively increasing `SLEEP_BETWEEN` from 1.2 s to 20 s.
- Decided to proceed with 32/36 locations rather than waiting for a rate-limit reset, based on confirming that sub-region coverage remained balanced (BC 10/12, CC 12/14, DS 8/10).
- Validated the per-subregion feature gradient against published Douro climatology: heat days increasing west-to-east (BC 3.3 < CC 5.7 < DS 12.3) and annual precipitation decreasing west-to-east (BC ~1,045 mm > CC ~717 mm > DS ~596 mm).
- Validated `climate_stress_year` against ten independently documented years:
  - **Known extreme years:** 2003 European heatwave (81% locations stressed), 2005 Iberian drought (94%), 2017 Portugal wildfires and record heat (94%), 2022 exceptional pan-Iberian drought and heat (100%), 2024 near-record Douro heat (94%).
  - **Known cool/wet years:** 1999, 2002, 2008, 2014, 2019 — all at ≤ 3% locations stressed.
- Reviewed every generated file for accuracy before committing; reviewed every commit before it was finalised.

---

## What Was NOT Outsourced to AI

- **Choice of data source** (Open-Meteo vs direct ERA5 CDS vs IPMA station data): human decision based on a tradeoff between data authority, API accessibility, and prototype-development speed. Open-Meteo was chosen because it provides ERA5 data via a simple REST API with no registration, making the pipeline reproducible by any team member.
- **Subregion split and target sample size** (36 sites: 12 BC, 14 CC, 10 DS): based on the IVDP's own regional structure and the proportional importance of each sub-region to Douro Port wine production; not an AI suggestion.
- **Label-rule philosophy** (per-location vs global percentiles): a deliberate design decision to support the project's "relative anomaly" framing — what constitutes a stress year for *this vineyard*, not for the Douro in aggregate. This has direct implications for the insurance product's trigger calibration.
- **Decision to proceed with 32/36 locations**: a human judgement call weighing balanced coverage (achieved) against project timeline constraints.
- **Final approval of every script and every commit**: no file was written and no commit was created without explicit human review and approval.
- **Interpretation of validation results**: the Data Lead assessed whether the known-year outputs were climatologically coherent; the AI produced numbers but did not evaluate their meaning.

---

## Limitations and Honest Disclosures

- Roughly **95%+ of the code in `src/data/`** was generated by Claude Code, not handwritten by the author. The author's contribution was specification (writing precise, detailed prompts), review, validation, and directional decisions. The author could reproduce the logic described above but did not type the implementation from scratch.
- Some **prompts were iteratively refined** with help from Claude on claude.ai before being passed to Claude Code — the final Claude Code prompts were more precise and complete than the author's initial formulations.
- The author **did not independently re-derive the climate features** from primary literature but verified that the implemented indicators (heat days, growing degree days base 10 °C, spring frost windows, consecutive dry days) match standard viticultural climate metrics as described in the cited sources (Fraga et al. 2025; Barriguinha et al. 2022).
- The **EDA notebook structure** was specified by the author but the prose, code, and section commentary were generated by Claude Code. The author reviewed the rendered outputs and confirmed they matched the expected patterns, but did not write the analysis independently.
- This log itself was written with Claude Code as a drafting tool, under detailed specification from the author. The factual content — tool choices, validation steps, design decisions — reflects the author's genuine record of the session.

---

## References to Project Sources

Methodological choices in the data pipeline follow standard viticultural climate-indicator conventions documented in the project's research proposal reference list:

- **Heat thresholds** (30 °C, 35 °C, 38 °C) and **growing-degree-day base temperature** (10 °C, April–October growing season) follow conventions in **Fraga et al. (2025)** and **Jones et al.** cited in the proposal.
- **Spring frost risk window** (March–May, −2 °C tissue-damage threshold) follows **Barriguinha et al. (2022)**.
- **Consecutive dry-day metric** and annual precipitation aggregation follow standard drought-index conventions cited in the proposal's climate-indicator sources.
- **IVDP sub-region definitions** (Baixo Corgo, Cima Corgo, Douro Superior) follow the regulatory classification at [ivdp.pt](https://www.ivdp.pt/en/page/caracteristicas-da-regiao/169).
- **ERA5 reanalysis data** is accessed via Open-Meteo (Zippenfenig 2023, DOI: 10.5281/zenodo.7970649); the underlying dataset is Hersbach et al. (2020), DOI: 10.1002/qj.3803.

Full citations are in `docs/data_sources.md`.
