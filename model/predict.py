"""
Mock backend for VinhaGuard.
Replace this module with Person 3's real model once delivered.
The function signature and return dict keys must stay identical.
"""

import random


def predict_risk_and_premium(
    subregion: str,
    area_ha: float,
    insured_value: float,
    risk_type: str,
    elevation: float | None = None,
) -> dict:
    """
    Returns a risk and premium estimate for a given vineyard.

    Parameters
    ----------
    subregion     : one of the six Douro sub-regions
    area_ha       : vineyard area in hectares
    insured_value : insured crop value in euros
    risk_type     : "Heat", "Frost", or "Both"
    elevation     : vineyard elevation in metres (optional)

    Returns
    -------
    dict with keys:
        risk_prob          float  [0, 1]
        premium_eur        float  euros
        trigger_threshold  str    human-readable trigger description
        basis_risk_pct     float  percentage
        feature_importance dict   {feature_name: importance_score}
    """
    # ------------------------------------------------------------------
    # MOCK — replace with real model inference once Person 3 delivers
    # ------------------------------------------------------------------
    _risk_by_subregion = {
        "Baixo Corgo": 0.45,
        "Cima Corgo": 0.55,
        "Douro Superior": 0.72,
        "Pinhão": 0.67,
        "Régua": 0.58,
        "Vila Nova de Foz Côa": 0.63,
    }

    base_risk = _risk_by_subregion.get(subregion, 0.60)

    if elevation is not None:
        base_risk -= (elevation / 900) * 0.10

    if risk_type == "Frost":
        base_risk *= 0.70
    elif risk_type == "Both":
        base_risk = min(base_risk * 1.10, 0.95)

    base_risk = round(max(0.05, min(0.95, base_risk)), 3)

    loss_given_trigger = 0.55
    risk_loading = 0.25
    admin_margin = 0.15
    premium_eur = round(
        insured_value * base_risk * loss_given_trigger * (1 + risk_loading) * (1 + admin_margin),
        0,
    )

    if risk_type == "Frost":
        trigger = "3 dias consecutivos abaixo de -2°C durante a floração (abril–maio)"
    elif risk_type == "Both":
        trigger = "14 dias > 38°C durante a véraison OU 3 dias < -2°C durante a floração"
    else:
        trigger = "14 dias consecutivos acima de 38°C durante a véraison (julho–agosto)"

    return {
        "risk_prob": base_risk,
        "premium_eur": premium_eur,
        "trigger_threshold": trigger,
        "basis_risk_pct": 12.5,
        "feature_importance": {
            "heat_days_38": 0.41,
            "max_temp": 0.28,
            "ndvi": 0.19,
            "elevation": 0.12,
        },
    }
