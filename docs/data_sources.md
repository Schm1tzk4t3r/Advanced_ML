# Data Sources — VinhaGuard AI

This document describes every external data source used in the VinhaGuard AI
data pipeline, with citations, license terms, and known limitations.

---

## 1. Open-Meteo Historical Weather API

**Role in pipeline:** Primary weather data provider. Called by `src/data/fetch_weather.py`.

| Field | Value |
|---|---|
| Endpoint | `https://archive-api.open-meteo.com/v1/archive` |
| Documentation | https://open-meteo.com/en/docs/historical-weather-api |
| Variables fetched | `temperature_2m_max`, `temperature_2m_min`, `temperature_2m_mean`, `precipitation_sum` |
| Temporal resolution | Daily |
| Period | 1995-01-01 – 2024-12-31 |
| Spatial resolution | ~9 km (native ERA5 grid, 0.1° re-gridded product) |
| Timezone | `Europe/Lisbon` |
| License | Free for non-commercial use; attribution required. |
| Terms of service | https://open-meteo.com/en/terms |

**Citation:**

> Zippenfenig, P. (2023). *Open-Meteo.com Weather API* [Software]. Zenodo.
> https://doi.org/10.5281/zenodo.7970649

**Usage notes:** The free tier is rate-limited (burst limit approximately 3–4 requests per minute per IP). No API key is required for non-commercial use. For higher request rates, a commercial subscription is available at https://open-meteo.com/en/pricing.

---

## 2. ERA5 Reanalysis (ECMWF)

**Role in pipeline:** Underlying atmospheric reanalysis dataset that Open-Meteo distributes. Not accessed directly — accessed via Open-Meteo.

ERA5 is the fifth generation ECMWF global atmospheric reanalysis, covering 1940 to present at hourly resolution on a ~31 km native grid, regridded to 0.25° (~25 km) for distribution. Open-Meteo further interpolates to a 0.1° (~9 km) grid for its API output.

| Field | Value |
|---|---|
| Provider | European Centre for Medium-Range Weather Forecasts (ECMWF) |
| Dataset page | https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5 |
| Copernicus CDS | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels |
| Native resolution | ~31 km (TL639 spectral grid); regridded to 0.25° |
| Temporal coverage | 1940 – present (hourly) |
| License | Copernicus License Agreement — free for any purpose including commercial, attribution required. |

**Citation:**

> Hersbach, H., Bell, B., Berrisford, P., et al. (2020). The ERA5 global reanalysis.
> *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049.
> https://doi.org/10.1002/qj.3803

---

## 3. TerraClimate

**Role in pipeline:** Water-balance enrichment. Called by `src/data/fetch_terraclimate.py`.

TerraClimate provides monthly global climate and climatic water-balance data at
approximately 1/24 degree spatial resolution. VinhaGuard uses it to add
physiologically meaningful drought indicators that are not captured by simple
daily rainfall counts alone.

| Field | Value |
|---|---|
| Provider | Climatology Lab / University of California Merced |
| Dataset page | https://www.climatologylab.org/terraclimate.html |
| Variable guide | https://www.climatologylab.org/terraclimate-variables.html |
| THREDDS/OPeNDAP archive | http://thredds.northwestknowledge.net:8080/thredds/catalog/TERRACLIMATE_ALL/data/catalog.html |
| Variables used | `vpd`, `def`, `soil`, `ppt` |
| Temporal resolution | Monthly |
| Period used | 1995-01 – 2024-12 |
| Spatial resolution | ~4 km |

**Citation:**

> Abatzoglou, J. T., Dobrowski, S. Z., Parks, S. A., & Hegewisch, K. C. (2018).
> TerraClimate, a high-resolution global dataset of monthly climate and climatic
> water balance from 1958-2015. *Scientific Data*, 5, 170191.
> https://doi.org/10.1038/sdata.2017.191

**Usage notes:** The script does not download global files. It reads the nearest
TerraClimate grid cell for each project vineyard location through OPeNDAP,
caches each variable-year extraction under `data/raw/terraclimate/`, then writes
annual ML-ready features to `data/processed/terraclimate_features.parquet`.

---

## 4. IVDP — Instituto dos Vinhos do Douro e do Porto

**Role in pipeline:** Authority for sub-region definitions used in `data/locations.csv` and throughout the dataset.

The Instituto dos Vinhos do Douro e do Porto (IVDP) is the regulatory body that governs the Douro Demarcated Region (Região Demarcada do Douro, RDD) and Port wine. VinhaGuard uses the IVDP's three-zone sub-region classification — Baixo Corgo, Cima Corgo, and Douro Superior — as the primary geographic grouping variable.

| Field | Value |
|---|---|
| Organisation | Instituto dos Vinhos do Douro e do Porto (IVDP) |
| Homepage | https://www.ivdp.pt/en |
| Region characteristics | https://www.ivdp.pt/en/page/caracteristicas-da-regiao/169 |
| Sub-region definitions | Baixo Corgo (west, most Atlantic), Cima Corgo (centre, Port heartland), Douro Superior (east, most continental) |

The 36 vineyard site coordinates in `data/locations.csv` were hand-curated to represent viticulturally meaningful locations within each IVDP sub-region. They do not correspond to any specific named quinta or commercial property.

---

## 5. IPMA — Instituto Português do Mar e da Atmosfera

**Role in pipeline:** Portuguese national meteorological authority. Used as an independent reference for data validation and for contextualising known extreme years (2003, 2005, 2017, 2022).

IPMA maintains long historical climate series for Portugal, including official station records stretching back to the 19th century. Their published climate normals and extreme event analyses were used to cross-check whether the VinhaGuard labelling rule correctly identifies documented stress years in the Douro region.

| Field | Value |
|---|---|
| Organisation | Instituto Português do Mar e da Atmosfera |
| Homepage | https://www.ipma.pt/en |
| Climate normals and long series | https://www.ipma.pt/en/clima/normais.clima/ |
| Extreme events archive | https://www.ipma.pt/en/oclima/extremos.clima/ |

---

## Limitations

### 1. Missing locations (rate-limited fetch)

Weather data was successfully retrieved for **32 of 36** planned vineyard
locations. Four locations — **CC03**, **CC12**, **DS05**, **DS10** — could not
be fetched within the project timeline due to Open-Meteo free-tier rate limits.
Sub-region coverage remains balanced:

| Sub-region | Planned | Retrieved | Missing |
|---|---|---|---|
| Baixo Corgo | 12 | 10 | — |
| Cima Corgo | 14 | 12 | CC03, CC12 |
| Douro Superior | 10 | 8 | DS05, DS10 |

The fetch script (`src/data/fetch_weather.py`) is resumable: re-running it will
skip the 32 already-downloaded files and retry only the 4 missing locations.

### 2. ERA5 grid resolution and basis risk

ERA5 data is distributed at approximately 9 km spatial resolution by
Open-Meteo. Any two vineyard sites that fall within the same ERA5 grid cell
will receive **identical raw weather values** regardless of their true
micro-climatic differences (aspect, slope, local wind exposure). For the Douro,
where vineyard micro-climates vary sharply over short distances, this is a
known caveat. It means the dataset captures **sub-regional climate signal** but
not within-cell vineyard heterogeneity. This constitutes a source of
**basis risk** for the parametric insurance product: trigger conditions may be
met or missed at the data-grid level while actual farm-level conditions differ.

### 3. TerraClimate grid resolution

TerraClimate adds useful drought physiology signals, but it is still gridded
data, not direct vineyard observations. Soil moisture and water deficit are
estimated at grid-cell scale and do not capture plot-level terrace structure,
irrigation, vine age, rootstock, canopy management, or local soil depth.

### 4. NDVI / Sentinel-2 intentionally scoped out

Normalised Difference Vegetation Index (NDVI) derived from Sentinel-2
multispectral imagery was identified as a valuable additional feature for
capturing actual vegetation stress independent of meteorological proxies. It
was intentionally excluded from the MVP due to time constraints. NDVI
integration (via the Copernicus Data Space Ecosystem or Google Earth Engine)
is on the project roadmap.

### 5. Legacy synthetic archive in data/processed/

`data/processed/douro_climate.parquet` is **not** part of the production
pipeline. It is an earlier synthetic dataset (6 sub-regions × 34 years,
generated by `src/data/generate_synthetic.py`) that remains in the repository
only as a reproducibility archive from an earlier prototype. The current
Streamlit dashboard, ML training script, and pricing backend use the processed
VinhaGuard dataset and model artifacts instead.

**Do not use `douro_climate.parquet` for model training, evaluation, or final
presentation claims.**
