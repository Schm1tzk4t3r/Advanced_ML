# VinhaGuard AI — Data Pipeline Handoff

## TL;DR

- **Dataset is ready:** `data/processed/vinhaguard_dataset.parquet` (CSV mirror alongside it)
- **960 rows × 21 columns** — one row per (vineyard location, year), 32 locations × 30 years (1995–2024)
- **Target column:** `climate_stress_year` — binary, **39.8% positive class**, well balanced out of the box
- **Zero missing values**, zero QC drops; label validated against documented Iberian extreme years

---

## What's in the Dataset

**File:** `data/processed/vinhaguard_dataset.parquet` (CSV mirror: `vinhaguard_dataset.csv`)  
**Shape:** 960 rows × 21 columns — each row is one (location, year) observation.

| Group | Column | Units | Meaning |
|---|---|---|---|
| **Identifiers** | `location_id` | — | Site ID, format `BC##` / `CC##` / `DS##` |
| | `year` | year | Calendar year, 1995–2024 |
| **Geography** | `subregion` | — | IVDP zone: Baixo Corgo, Cima Corgo, or Douro Superior |
| | `elevation_m` | m a.s.l. | Site elevation (range 88–695 m) |
| | `latitude` | decimal degrees | WGS84, 4 d.p. |
| | `longitude` | decimal degrees | WGS84, west-negative |
| **Heat** | `heat_days_30` | days | Days per year with tmax ≥ 30 °C |
| | `heat_days_35` | days | Days per year with tmax ≥ 35 °C (used in label rule) |
| | `heat_days_38` | days | Days per year with tmax ≥ 38 °C (véraison trigger) |
| | `max_summer_tmax` | °C | Peak daily max temp, June–August |
| | `mean_summer_tmax` | °C | Mean daily max temp, June–August |
| | `heatwave_max_streak` | days | Longest consecutive run of tmax ≥ 35 °C days |
| | `gdd_growing_season` | °C·days | Growing degree days (base 10 °C), April–October |
| **Spring frost** | `spring_frost_days` | days | Days in Mar–May with tmin < 0 °C |
| | `spring_severe_frost_days` | days | Days in Mar–May with tmin < −2 °C (used in label rule) |
| | `min_spring_tmin` | °C | Most extreme cold event in Mar–May |
| **Drought / precip** | `annual_precip_mm` | mm | Total precipitation, Jan–Dec |
| | `summer_precip_mm` | mm | Total precipitation, June–August |
| | `dry_days` | days | Days per year with precip < 1 mm |
| | `max_consecutive_dry_days` | days | Longest dry spell (used in label rule) |
| **Target** | `climate_stress_year` | 0 / 1 | **1 = climate stress year. 39.8% positive.** |

Full column definitions with source and derivation notes: `docs/data_dictionary.md`.

---

## Coverage and Caveats

- **32 of 36 planned locations** have weather data. Missing: **CC03, CC12, DS05, DS10** — couldn't be fetched within the project timeline due to Open-Meteo free-tier rate limits. Sub-region balance is fine: BC 10/12, CC 12/14, DS 8/10.
- **Period:** 1995-01-01 to 2024-12-31, daily weather aggregated to annual features.
- **Source:** Open-Meteo Historical Weather API, backed by ERA5 reanalysis at ~9 km grid resolution. Worth flagging in any user-facing demo: two vineyard sites within the same grid cell get identical raw weather values regardless of micro-climate differences. This is a known basis-risk caveat for the parametric product.
- **Data quality:** zero rows dropped by QC (all location-years had ≥ 90% daily coverage), zero missing values in the final dataset.

---

## Target Column: `climate_stress_year`

A year at a given location is labelled **stress = 1** if **any** of these holds:

- `heat_days_35` ≥ 80th percentile of **that location's own** 30-year distribution, **or**
- `spring_severe_frost_days` ≥ 3 days, **or**
- `max_consecutive_dry_days` ≥ 80th percentile of **that location's own** 30-year distribution

**Why per-location percentiles?** Douro Superior runs 8–12 °C hotter than Baixo Corgo in summer. A global threshold would label almost every DS year as stressed and almost every BC year as normal — just because of geography, not because the year was unusual for that site. Per-location percentiles make the label about *relative anomaly*, which is the right signal for an insurance product.

The label rule is one function — `label_stress_year()` in `src/data/make_dataset.py` — and is easy to tune if needed.

**Validation against documented climate events:**

| Year | Stress rate | Known event |
|---|---|---|
| 2003 | 81% | European heatwave (hottest summer in 500 years) |
| 2005 | 94% | Severe Iberian drought |
| 2017 | 94% | Portugal wildfires + record heat |
| 2022 | 100% | Exceptional pan-Iberian heat and drought |
| 2024 | 94% | Recent near-record Douro season |

Cool/wet reference years (1999, 2002, 2008, 2014, 2019): all ≤ 3% stress. The signal is clean.

---

## For Person 3 (ML & Pricing Lead)

**Class balance:** 39.8% positive — no SMOTE or class-weight tricks needed; Logistic Regression and XGBoost will both train stably.

**Suggested approach:**
- Baseline: Logistic Regression on standardized features (`StandardScaler` on all numeric columns)
- Main model: Random Forest or XGBoost (no scaling needed)
- Don't train on both and test on the same years — use either a **chronological holdout** (e.g., train 1995–2019, test 2020–2024) or **stratified-by-subregion** splits to avoid leakage

**Feature notes:**
- `subregion` is categorical — one-hot encode it (3 classes → 2 dummies, drop one)
- `location_id`, `latitude`, `longitude`, `elevation_m` are available but may not be appropriate as model features depending on your generalization goal — worth a deliberate choice
- `year` is a temporal index; using it as a raw feature risks the model just learning "later years are hotter" without generalization

**Pricing engine link (proposal Section 7):**  
The model's predicted `P(stress=1)` feeds directly into expected payout:

```
expected_payout = P(trigger) × payout_amount
annual_premium  = expected_payout + loading
```

The three label conditions (heat, spring frost, drought) align with the proposal's parametric trigger types, so the label probability is directly interpretable as trigger probability.

**To tune the label rule:** edit `label_stress_year()` in `src/data/make_dataset.py` and re-run `python -m src.data.make_dataset`. It overwrites only the processed files, not the raw or interim data.

---

## For Person 4 (Product & Demo Lead)

**Nothing is broken:** `data/processed/douro_climate.parquet` (the synthetic placeholder the existing Dashboard page reads) is still there. Your demo will work as-is.

**When you're ready to migrate to real data:**  
Point the Dashboard at `data/processed/vinhaguard_dataset.parquet`. Key differences from the old file:
- 32 individual site rows instead of 6 subregion aggregates
- Real `climate_stress_year` label you can plot or filter on
- `latitude` and `longitude` columns — `st.map()` works out of the box, no pre-processing needed

**For the trigger-history chart** (proposal Section 6, step 3):

```python
df = pd.read_parquet("data/processed/vinhaguard_dataset.parquet")
site = df[df["location_id"] == selected_location_id]
# plot site[["year", "climate_stress_year"]] or the underlying features
```

**For maps:** pass the whole dataset (or a per-year slice) to `st.map(df[["latitude", "longitude"]])`.

**Useful demo talking points:**
- "Each row is a year of climate exposure for one Douro vineyard site."
- "The label captures three real parametric triggers: extreme heat, spring frost, and drought — the same triggers as the insurance product."
- "The model output is a probability — feed it to the pricing engine to get an expected payout and premium."
- The known-year validation table above is a strong story for a live demo: show 2022 at 100% and 2019 at 3%.

---

## Reproducing the Pipeline

```bash
python -m src.data.locations && \
python -m src.data.fetch_weather && \
python -m src.data.build_features && \
python -m src.data.make_dataset
```

Step 2 (fetch) takes ~5–15 minutes due to Open-Meteo rate limits. Steps 1, 3, and 4 are fast (< 30 s each). Full details in `README.md` and `docs/data_sources.md`.

---

## Files Produced This Session

| File | Description |
|---|---|
| `data/locations.csv` | 36 Douro vineyard sites with subregion, coordinates, elevation, and `weather_data_available` flag |
| `data/raw/weather/*.parquet` | 32 raw daily weather files (gitignored — re-run fetch to regenerate) |
| `data/interim/features_by_location_year.parquet` | 960 rows × 20 engineered features, pre-labelling (gitignored) |
| `data/processed/vinhaguard_dataset.parquet` | **Final ML dataset** — 960 rows × 21 columns including target |
| `data/processed/vinhaguard_dataset.csv` | CSV mirror of the above |
| `src/data/locations.py` | Pipeline step 1 — generates locations.csv |
| `src/data/fetch_weather.py` | Pipeline step 2 — fetches ERA5 weather via Open-Meteo |
| `src/data/build_features.py` | Pipeline step 3 — engineers 20 climate features |
| `src/data/make_dataset.py` | Pipeline step 4 — labels stress years, writes final dataset |
| `docs/data_dictionary.md` | Full 21-column reference with units, derivation, and labelling rule |
| `docs/data_sources.md` | API citations, licenses, and known limitations |
| `notebooks/01_data_exploration.ipynb` | Executed EDA notebook — distributions, heat trend, class balance, correlation heatmap |
| `README.md` | Updated with pipeline table, runtime note, and handoff section |

---

## Questions or Tweaks

Happy to adjust the label rule thresholds, re-fetch the missing 4 locations once the rate-limit window resets, or add new features if you need them — NDVI from Sentinel-2 is already on the roadmap. Just say the word.
