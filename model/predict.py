"""Production inference and pricing backend for VinhaGuard AI.

The Streamlit app imports ``predict_risk_and_premium`` from this module. The
function keeps the original public signature, but the implementation now uses
the trained model artifact and historical trigger data produced by
``python -m model.train``.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
import unicodedata

import joblib
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = REPO_ROOT / "model" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "risk_model.joblib"
SCORED_HISTORY_PATH = ARTIFACT_DIR / "scored_history.csv"
FEATURE_IMPORTANCE_PATH = ARTIFACT_DIR / "feature_importance.csv"

VALID_SUBREGIONS = ["Baixo Corgo", "Cima Corgo", "Douro Superior"]
SUBREGION_ALIASES = {
    "baixo corgo": "Baixo Corgo",
    "cima corgo": "Cima Corgo",
    "douro superior": "Douro Superior",
    "pinhao": "Cima Corgo",
    "regua": "Baixo Corgo",
    "vila nova de foz coa": "Douro Superior",
}


@dataclass(frozen=True)
class PricingConfig:
    loss_given_trigger: float
    base_risk_loading: float
    admin_margin: float
    platform_fee_eur: float
    per_hectare_admin_eur: float
    trigger_threshold: str


PRICING_CONFIG: dict[str, PricingConfig] = {
    "Heat": PricingConfig(
        loss_given_trigger=0.50,
        base_risk_loading=0.25,
        admin_margin=0.15,
        platform_fee_eur=50.0,
        per_hectare_admin_eur=2.0,
        trigger_threshold="14 days above 38 C during veraison (July-August)",
    ),
    "Frost": PricingConfig(
        loss_given_trigger=0.40,
        base_risk_loading=0.25,
        admin_margin=0.15,
        platform_fee_eur=50.0,
        per_hectare_admin_eur=2.0,
        trigger_threshold="3 spring days below -2 C during budbreak/flowering",
    ),
    "Drought": PricingConfig(
        loss_given_trigger=0.45,
        base_risk_loading=0.25,
        admin_margin=0.15,
        platform_fee_eur=50.0,
        per_hectare_admin_eur=2.0,
        trigger_threshold="Dry-spell length above the vineyard's historical 80th percentile",
    ),
    "Both": PricingConfig(
        loss_given_trigger=0.55,
        base_risk_loading=0.30,
        admin_margin=0.15,
        platform_fee_eur=50.0,
        per_hectare_admin_eur=2.0,
        trigger_threshold="Heat, frost, or drought stress trigger",
    ),
}


def _repair_text(value: str) -> str:
    """Recover common UTF-8 text that was accidentally read as Latin-1."""
    text = value
    for _ in range(2):
        try:
            repaired = text.encode("latin1").decode("utf-8")
        except UnicodeError:
            break
        if repaired == text:
            break
        text = repaired
    return text


def _ascii_key(value: str) -> str:
    repaired = _repair_text(value).strip().lower()
    normalized = unicodedata.normalize("NFKD", repaired)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_text = ascii_text.replace("?", "")
    return " ".join(ascii_text.split())


def _normalise_subregion(subregion: str) -> str:
    key = _ascii_key(str(subregion))
    if key in SUBREGION_ALIASES:
        return SUBREGION_ALIASES[key]
    if key.startswith("pinh"):
        return "Cima Corgo"
    if key.startswith("reg") or key.startswith("rgua"):
        return "Baixo Corgo"
    if "foz" in key and ("coa" in key or key.endswith("foz ca") or key.endswith("foz co")):
        return "Douro Superior"
    raise ValueError(
        f"Unknown subregion '{subregion}'. Expected one of: {', '.join(VALID_SUBREGIONS)}."
    )


def _normalise_risk_type(risk_type: str) -> str:
    cleaned = str(risk_type).strip().title()
    if cleaned == "Heat + Frost":
        cleaned = "Both"
    if cleaned not in PRICING_CONFIG:
        raise ValueError(f"Unknown risk_type '{risk_type}'. Expected Heat, Frost, Drought, or Both.")
    return cleaned


@lru_cache(maxsize=1)
def _load_artifacts() -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    missing = [p for p in [MODEL_PATH, SCORED_HISTORY_PATH, FEATURE_IMPORTANCE_PATH] if not p.exists()]
    if missing:
        missing_text = ", ".join(str(p.relative_to(REPO_ROOT)) for p in missing)
        raise FileNotFoundError(
            f"Missing ML artifact(s): {missing_text}. Run 'python -m model.train' from the repo root."
        )

    artifact = joblib.load(MODEL_PATH)
    history = pd.read_csv(SCORED_HISTORY_PATH)
    importance = pd.read_csv(FEATURE_IMPORTANCE_PATH)
    return artifact, history, importance


def _weighted_average(values: pd.Series, weights: np.ndarray) -> float:
    total = float(weights.sum())
    if total <= 0:
        return float(values.mean())
    return float(np.average(values.to_numpy(dtype=float), weights=weights))


def _history_weights(history: pd.DataFrame, elevation: float | None) -> np.ndarray:
    weights = np.ones(len(history), dtype=float)
    if elevation is None:
        return weights

    # A Gaussian kernel gives strongest weight to sites near the user's
    # elevation, while keeping enough rows to avoid overfitting one vineyard.
    sigma_m = 175.0
    distance = history["elevation_m"].to_numpy(dtype=float) - float(elevation)
    weights = np.exp(-0.5 * (distance / sigma_m) ** 2)
    return np.clip(weights, 0.05, 1.0)


def _basis_risk_pct(history: pd.DataFrame, elevation: float | None) -> float:
    base = 10.0
    location_count = int(history["location_id"].nunique())
    if location_count < 10:
        base += 2.5

    if elevation is not None:
        median_elev = float(history["elevation_m"].median())
        base += min(abs(float(elevation) - median_elev) / 100.0, 5.0)

    # ERA5/Open-Meteo grid data does not capture plot-level slope/aspect and
    # vineyard microclimate, so a non-zero basis-risk warning is always kept.
    return round(float(np.clip(base, 8.0, 22.0)), 1)


def _risk_components(history: pd.DataFrame, weights: np.ndarray, risk_type: str) -> dict[str, float]:
    stress_model = _weighted_average(history["model_stress_probability"], weights)
    stress_history = _weighted_average(history["climate_stress_year"], weights)
    heat_history = _weighted_average(history["heat_trigger"], weights)
    frost_history = _weighted_average(history["frost_trigger"], weights)
    drought_history = _weighted_average(history["drought_trigger"], weights)

    if risk_type == "Heat":
        historical = heat_history
        model_component = stress_model
    elif risk_type == "Frost":
        historical = frost_history
        model_component = min(stress_model, max(frost_history * 1.25, 0.02))
    elif risk_type == "Drought":
        historical = drought_history
        model_component = stress_model
    else:
        historical = stress_history
        model_component = stress_model

    blended = 0.70 * historical + 0.30 * model_component
    return {
        "risk_prob": round(float(np.clip(blended, 0.01, 0.95)), 4),
        "historical_trigger_rate": round(float(historical), 4),
        "model_stress_probability": round(float(model_component), 4),
        "heat_trigger_rate": round(float(heat_history), 4),
        "frost_trigger_rate": round(float(frost_history), 4),
        "drought_trigger_rate": round(float(drought_history), 4),
        "combined_stress_rate": round(float(stress_history), 4),
    }


def _premium_breakdown(
    risk_prob: float,
    insured_value: float,
    area_ha: float,
    basis_risk_pct: float,
    config: PricingConfig,
) -> dict[str, float]:
    expected_payout = float(insured_value) * risk_prob * config.loss_given_trigger
    uncertainty_loading = config.base_risk_loading + max(basis_risk_pct - 10.0, 0.0) / 100.0
    risk_loading_eur = expected_payout * uncertainty_loading
    admin_eur = config.platform_fee_eur + config.per_hectare_admin_eur * float(area_ha)
    subtotal = expected_payout + risk_loading_eur + admin_eur
    margin_eur = subtotal * config.admin_margin
    premium = subtotal + margin_eur

    return {
        "expected_payout_eur": round(expected_payout, 2),
        "risk_loading_eur": round(risk_loading_eur, 2),
        "admin_eur": round(admin_eur, 2),
        "margin_eur": round(margin_eur, 2),
        "premium_eur": round(premium, 0),
        "premium_rate": round(premium / float(insured_value), 4),
        "loss_given_trigger": config.loss_given_trigger,
        "risk_loading_pct": round(uncertainty_loading, 4),
        "admin_margin_pct": config.admin_margin,
    }


def _top_feature_importance(importance: pd.DataFrame, top_n: int = 6) -> dict[str, float]:
    score_col = "permutation_importance_mean"
    if score_col not in importance.columns:
        score_col = "gini_importance"

    top = importance.sort_values(score_col, ascending=False).head(top_n)
    total = float(top[score_col].sum())
    if total <= 0:
        return {row["feature"]: 0.0 for _, row in top.iterrows()}
    return {row["feature"]: round(float(row[score_col] / total), 3) for _, row in top.iterrows()}


def predict_risk_and_premium(
    subregion: str,
    area_ha: float,
    insured_value: float,
    risk_type: str,
    elevation: float | None = None,
) -> dict:
    """Return a climate-risk and premium estimate for one vineyard quote.

    The public function signature is intentionally stable for the Streamlit app.
    Internally, the quote is priced from:
    - historical trigger behavior for the selected Douro subregion;
    - optional elevation-weighted similarity to historical vineyard sites;
    - the trained Random Forest model's stress probability on comparable history.

    This keeps the product honest: at quote time, the user has not observed the
    coming season's weather yet, so the backend estimates trigger probability
    from historical climatology instead of fabricating future weather features.
    """
    if area_ha <= 0:
        raise ValueError("area_ha must be greater than zero.")
    if insured_value <= 0:
        raise ValueError("insured_value must be greater than zero.")

    canonical_subregion = _normalise_subregion(subregion)
    canonical_risk = _normalise_risk_type(risk_type)
    config = PRICING_CONFIG[canonical_risk]

    _, history, importance = _load_artifacts()
    sub_history = history[history["subregion"] == canonical_subregion].copy()
    if sub_history.empty:
        raise ValueError(f"No historical data available for subregion '{canonical_subregion}'.")

    weights = _history_weights(sub_history, elevation)
    basis_risk = _basis_risk_pct(sub_history, elevation)
    risk = _risk_components(sub_history, weights, canonical_risk)
    pricing = _premium_breakdown(
        risk_prob=risk["risk_prob"],
        insured_value=float(insured_value),
        area_ha=float(area_ha),
        basis_risk_pct=basis_risk,
        config=config,
    )

    return {
        "risk_prob": risk["risk_prob"],
        "premium_eur": pricing["premium_eur"],
        "trigger_threshold": config.trigger_threshold,
        "basis_risk_pct": basis_risk,
        "feature_importance": _top_feature_importance(importance),
        "pricing_breakdown": pricing,
        "historical_trigger_rate": risk["historical_trigger_rate"],
        "model_stress_probability": risk["model_stress_probability"],
        "hazard_rates": {
            "heat": risk["heat_trigger_rate"],
            "frost": risk["frost_trigger_rate"],
            "drought": risk["drought_trigger_rate"],
            "combined": risk["combined_stress_rate"],
        },
        "subregion_used": canonical_subregion,
        "risk_type_used": canonical_risk,
        "n_historical_rows": int(len(sub_history)),
        "n_locations": int(sub_history["location_id"].nunique()),
    }
