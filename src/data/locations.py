"""
Vineyard location master list for VinhaGuard AI.

Subregion definitions follow the Instituto dos Vinhos do Douro e do Porto (IVDP)
classification of the Região Demarcada do Douro (RDD): Baixo Corgo, Cima Corgo,
and Douro Superior.

Coordinates were hand-curated to represent viticulturally meaningful sites within
each subregion — terraced schist slopes, south/southwest-facing exposures, and
elevations typical of the Douro's terroir — and do not correspond to specific named
quintas. All coordinates are decimal degrees, WGS84, 4 decimal places.

Run as a script to (re)generate data/locations.csv:
    python -m src.data.locations
"""

import pathlib

import pandas as pd

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT_PATH = _REPO_ROOT / "data" / "locations.csv"

# fmt: off
_LOCATIONS: list[dict] = [
    # ── Baixo Corgo (12 sites) ──────────────────────────────────────────────
    # Municipalities: Peso da Régua, Lamego, Mesão Frio, Resende, Tarouca
    # Western sub-region; cooler, more Atlantic influence; schist terraces along
    # the Douro and its tributaries (Corgo, Varosa).
    {"location_id": "BC01", "name": "Vale do Corgo Norte",     "subregion": "Baixo Corgo", "latitude": 41.1645, "longitude": -7.9120, "elevation_m": 145},
    {"location_id": "BC02", "name": "Encosta de Mesão Frio",   "subregion": "Baixo Corgo", "latitude": 41.1382, "longitude": -7.9015, "elevation_m": 285},
    {"location_id": "BC03", "name": "Terraço do Régua Norte",  "subregion": "Baixo Corgo", "latitude": 41.1748, "longitude": -7.7905, "elevation_m": 110},
    {"location_id": "BC04", "name": "Margem Sul do Régua",     "subregion": "Baixo Corgo", "latitude": 41.1510, "longitude": -7.7823, "elevation_m": 210},
    {"location_id": "BC05", "name": "Ribeira de Covelinhas",   "subregion": "Baixo Corgo", "latitude": 41.1830, "longitude": -7.7380, "elevation_m":  88},
    {"location_id": "BC06", "name": "Planalto de Godim",       "subregion": "Baixo Corgo", "latitude": 41.1672, "longitude": -7.7295, "elevation_m": 420},
    {"location_id": "BC07", "name": "Serra da Lamego",         "subregion": "Baixo Corgo", "latitude": 41.1125, "longitude": -7.8235, "elevation_m": 530},
    {"location_id": "BC08", "name": "Vale Meão de Lamego",     "subregion": "Baixo Corgo", "latitude": 41.1290, "longitude": -7.8080, "elevation_m": 380},
    {"location_id": "BC09", "name": "Encosta de Resende",      "subregion": "Baixo Corgo", "latitude": 41.0925, "longitude": -7.9350, "elevation_m": 340},
    {"location_id": "BC10", "name": "Alto de Resende",         "subregion": "Baixo Corgo", "latitude": 41.0740, "longitude": -7.9185, "elevation_m": 695},
    {"location_id": "BC11", "name": "Ribeira da Teja",         "subregion": "Baixo Corgo", "latitude": 41.1795, "longitude": -7.7125, "elevation_m":  92},
    {"location_id": "BC12", "name": "Planalto de Tarouca",     "subregion": "Baixo Corgo", "latitude": 41.0605, "longitude": -7.7825, "elevation_m": 610},

    # ── Cima Corgo (14 sites) ───────────────────────────────────────────────
    # Municipalities: Pinhão, Sabrosa, Alijó, São João da Pesqueira,
    #                 Tabuaço, Carrazeda de Ansiães
    # Central sub-region; classic Port heartland; higher diurnal temperature
    # range; terraces on both banks of the Douro and Pinhão river.
    {"location_id": "CC01", "name": "Terraço do Pinhão Norte",    "subregion": "Cima Corgo", "latitude": 41.1920, "longitude": -7.5420, "elevation_m": 105},
    {"location_id": "CC02", "name": "Encosta de Sabrosa",         "subregion": "Cima Corgo", "latitude": 41.2185, "longitude": -7.5035, "elevation_m": 350},
    {"location_id": "CC03", "name": "Alto de Alijó",              "subregion": "Cima Corgo", "latitude": 41.2680, "longitude": -7.4720, "elevation_m": 580},
    {"location_id": "CC04", "name": "Margem Sul do Pinhão",       "subregion": "Cima Corgo", "latitude": 41.1735, "longitude": -7.5380, "elevation_m": 175},
    {"location_id": "CC05", "name": "Terraço de São João",        "subregion": "Cima Corgo", "latitude": 41.1420, "longitude": -7.4025, "elevation_m": 240},
    {"location_id": "CC06", "name": "Planalto de Pesqueira",      "subregion": "Cima Corgo", "latitude": 41.1260, "longitude": -7.3840, "elevation_m": 520},
    {"location_id": "CC07", "name": "Vale de Tabuaço",            "subregion": "Cima Corgo", "latitude": 41.1165, "longitude": -7.5660, "elevation_m": 310},
    {"location_id": "CC08", "name": "Alto de Tabuaço",            "subregion": "Cima Corgo", "latitude": 41.1042, "longitude": -7.5495, "elevation_m": 625},
    {"location_id": "CC09", "name": "Terraço de Carrazeda",       "subregion": "Cima Corgo", "latitude": 41.2350, "longitude": -7.2955, "elevation_m": 195},
    {"location_id": "CC10", "name": "Planalto de Ansiães",        "subregion": "Cima Corgo", "latitude": 41.2520, "longitude": -7.2620, "elevation_m": 450},
    {"location_id": "CC11", "name": "Encosta Sul de Alijó",       "subregion": "Cima Corgo", "latitude": 41.2420, "longitude": -7.4385, "elevation_m": 480},
    {"location_id": "CC12", "name": "Terraço Baixo de Sabrosa",   "subregion": "Cima Corgo", "latitude": 41.1985, "longitude": -7.4950, "elevation_m": 155},
    {"location_id": "CC13", "name": "Vale de Figueira",           "subregion": "Cima Corgo", "latitude": 41.2095, "longitude": -7.4680, "elevation_m": 280},
    {"location_id": "CC14", "name": "Ervedosa do Douro",          "subregion": "Cima Corgo", "latitude": 41.1580, "longitude": -7.3630, "elevation_m": 135},

    # ── Douro Superior (10 sites) ───────────────────────────────────────────
    # Municipalities: Vila Nova de Foz Côa, Torre de Moncorvo,
    #                 Freixo de Espada à Cinta, Mêda, Vila Flor
    # Eastern sub-region; most continental climate; highest heat accumulation;
    # extends to the Spanish border at Barca d'Alva.
    {"location_id": "DS01", "name": "Terraço de Foz Côa",      "subregion": "Douro Superior", "latitude": 41.0845, "longitude": -7.1510, "elevation_m": 165},
    {"location_id": "DS02", "name": "Alto de Foz Côa",         "subregion": "Douro Superior", "latitude": 41.0650, "longitude": -7.1285, "elevation_m": 450},
    {"location_id": "DS03", "name": "Vale do Moncorvo",        "subregion": "Douro Superior", "latitude": 41.1905, "longitude": -7.0785, "elevation_m": 215},
    {"location_id": "DS04", "name": "Encosta de Moncorvo",     "subregion": "Douro Superior", "latitude": 41.2120, "longitude": -7.0625, "elevation_m": 490},
    {"location_id": "DS05", "name": "Terraço de Freixo",       "subregion": "Douro Superior", "latitude": 41.0605, "longitude": -6.8215, "elevation_m": 125},
    {"location_id": "DS06", "name": "Encosta de Freixo",       "subregion": "Douro Superior", "latitude": 41.0785, "longitude": -6.8420, "elevation_m": 380},
    {"location_id": "DS07", "name": "Planalto de Mêda",        "subregion": "Douro Superior", "latitude": 40.9875, "longitude": -7.2545, "elevation_m": 640},
    {"location_id": "DS08", "name": "Terraço de Vila Flor",    "subregion": "Douro Superior", "latitude": 41.2985, "longitude": -7.1525, "elevation_m": 280},
    {"location_id": "DS09", "name": "Pocinho Ribeira",         "subregion": "Douro Superior", "latitude": 41.0990, "longitude": -7.1055, "elevation_m":  90},
    {"location_id": "DS10", "name": "Barca d'Alva Terraço",   "subregion": "Douro Superior", "latitude": 41.0382, "longitude": -7.0085, "elevation_m": 135},
]
# fmt: on

_COLUMNS = ["location_id", "name", "subregion", "latitude", "longitude", "elevation_m"]


def build_dataframe() -> pd.DataFrame:
    return pd.DataFrame(_LOCATIONS)[_COLUMNS]


def main() -> None:
    df = build_dataframe()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    elev = df["elevation_m"]
    counts = df.groupby("subregion", sort=False).size()

    print(f"Wrote {len(df)} rows → {OUTPUT_PATH}")
    print()
    print("Rows per subregion:")
    for subregion, n in counts.items():
        print(f"  {subregion}: {n}")
    print()
    print(
        f"Elevation (m):  "
        f"min={elev.min()}  "
        f"median={elev.median():.0f}  "
        f"max={elev.max()}"
    )


if __name__ == "__main__":
    main()
