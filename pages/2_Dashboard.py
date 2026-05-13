import os
import sys
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predict_risk_and_premium

LOCATIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "locations.csv")

st.markdown(
    """
<style>
    .chart-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    div[data-baseweb="select"] input {
        pointer-events: none;
        caret-color: transparent;
    }
    .wx-card {
        border: 2px solid;
        border-radius: 10px;
        padding: 14px 10px;
        text-align: center;
        margin-bottom: 8px;
        min-height: 200px;
    }
    .wx-label { font-size: 0.75em; color: #666; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .wx-date  { font-size: 0.70em; color: #999; margin-bottom: 4px; }
    .wx-icon  { font-size: 2.2em; line-height: 1.2; }
    .wx-desc  { font-size: 0.80em; color: #444; margin-bottom: 6px; }
    .wx-temp-max { font-size: 1.1em; font-weight: bold; color: #C62828; }
    .wx-temp-min { font-size: 1.0em; color: #1565C0; }
    .wx-precip   { font-size: 0.82em; color: #555; margin-top: 3px; }
    .wx-badge    { font-size: 0.78em; font-weight: bold; margin-top: 6px; }
    .trigger-card {
        border: 2px solid;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        background: white;
        margin-bottom: 8px;
        min-height: 140px;
    }
    .trigger-icon   { font-size: 1.8em; }
    .trigger-title  { font-size: 0.95em; font-weight: bold; margin: 4px 0; color: #222; }
    .trigger-desc   { font-size: 0.78em; color: #666; line-height: 1.5; margin: 4px 0; }
    .trigger-status { font-size: 0.85em; font-weight: bold; margin-top: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

BURGUNDY = "#6B1C2E"
GOLD = "#B8860B"
GREY = "#CCCCCC"

DISPLAY_SUBREGIONS = [
    "Baixo Corgo",
    "Cima Corgo",
    "Douro Superior",
    "Pinhao",
    "Regua",
    "Vila Nova de Foz Coa",
]

# Centroid coordinates per sub-region (derived from locations.csv means)
SUBREGION_COORDS = {
    "Baixo Corgo":          {"lat": 41.136, "lon": -7.819},
    "Cima Corgo":           {"lat": 41.188, "lon": -7.449},
    "Douro Superior":       {"lat": 41.111, "lon": -7.060},
    "Pinhao":               {"lat": 41.188, "lon": -7.449},
    "Regua":                {"lat": 41.136, "lon": -7.819},
    "Vila Nova de Foz Coa": {"lat": 41.111, "lon": -7.060},
}

# WMO Weather Interpretation Codes → (description, emoji)
WMO_META: dict[int, tuple[str, str]] = {
    0:  ("Clear sky",           "☀️"),
    1:  ("Mainly clear",        "🌤️"),
    2:  ("Partly cloudy",       "⛅"),
    3:  ("Overcast",            "☁️"),
    45: ("Fog",                 "🌫️"),
    48: ("Icy fog",             "🌫️"),
    51: ("Light drizzle",       "🌦️"),
    53: ("Drizzle",             "🌦️"),
    55: ("Heavy drizzle",       "🌧️"),
    61: ("Light rain",          "🌧️"),
    63: ("Rain",                "🌧️"),
    65: ("Heavy rain",          "🌧️"),
    71: ("Light snow",          "❄️"),
    73: ("Snow",                "❄️"),
    75: ("Heavy snow",          "❄️"),
    77: ("Snow grains",         "❄️"),
    80: ("Light showers",       "🌦️"),
    81: ("Showers",             "🌧️"),
    82: ("Heavy showers",       "⛈️"),
    85: ("Snow showers",        "🌨️"),
    86: ("Heavy snow showers",  "🌨️"),
    95: ("Thunderstorm",        "⛈️"),
    96: ("Thunderstorm + hail", "⛈️"),
    99: ("Thunderstorm + hail", "⛈️"),
}

# Trigger thresholds (must match model/predict.py PRICING_CONFIG definitions)
HEAT_TEMP_THRESH   = 38.0   # °C — a day counts as a heat day if max temp ≥ this
FROST_TEMP_THRESH  = -2.0   # °C — a day counts as a frost day if min temp ≤ this
DRY_MM_THRESH      =  1.0   # mm — below this = dry day
HEAT_DAYS_TRIGGER  =  5     # seasonal threshold: ≥5 heat days → payout
FROST_DAYS_TRIGGER =  3     # seasonal threshold: ≥3 frost days → payout


@st.cache_data(ttl=1800)
def _fetch_weather(lat: float, lon: float) -> dict | None:
    """Fetch today + last 3 days of daily weather from Open-Meteo (no API key needed)."""
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":  lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                "past_days":     3,
                "forecast_days": 1,
                "timezone": "Europe/Lisbon",
            },
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _parse_weather_days(data: dict) -> list[dict]:
    d = data["daily"]
    rows = []
    for i, date in enumerate(d["time"]):
        max_t  = d["temperature_2m_max"][i]
        min_t  = d["temperature_2m_min"][i]
        precip = d["precipitation_sum"][i] or 0.0
        rows.append({
            "date":      date,
            "max_temp":  max_t,
            "min_temp":  min_t,
            "precip":    precip,
            "code":      d["weathercode"][i],
            "heat_day":  max_t is not None and max_t >= HEAT_TEMP_THRESH,
            "frost_day": min_t is not None and min_t <= FROST_TEMP_THRESH,
            "dry_day":   precip < DRY_MM_THRESH,
        })
    return rows


def _weather_trigger_summary(days: list[dict]) -> dict:
    heat_n  = sum(1 for d in days if d["heat_day"])
    frost_n = sum(1 for d in days if d["frost_day"])
    consec_dry = 0
    for d in reversed(days):
        if d["dry_day"]:
            consec_dry += 1
        else:
            break
    return {
        "heat_count":      heat_n,
        "frost_count":     frost_n,
        "consecutive_dry": consec_dry,
        "heat_triggered":  heat_n  >= HEAT_DAYS_TRIGGER,
        "frost_triggered": frost_n >= FROST_DAYS_TRIGGER,
    }


@st.cache_data
def load_history():
    scored_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "model",
        "artifacts",
        "scored_history.csv",
    )
    if not os.path.exists(scored_path):
        st.error("Missing model/artifacts/scored_history.csv. Run `python -m model.train` first.")
        st.stop()

    df = pd.read_csv(scored_path)
    required = {
        "year",
        "subregion",
        "location_id",
        "heat_days_38",
        "heat_trigger",
        "climate_stress_year",
        "model_stress_probability",
    }
    missing = required.difference(df.columns)
    if missing:
        st.error(f"scored_history.csv is missing required columns: {', '.join(sorted(missing))}")
        st.stop()
    return df


st.title("Climate Risk Dashboard")
st.markdown("Historical analysis and model explainability for your selected region.")
st.markdown("---")

# ── Section: Live Weather Monitor ─────────────────────────────────────────────
_wx_display = st.session_state.get("wx_location", list(SUBREGION_COORDS.keys())[1])
st.markdown(f"### Live Weather Monitor — {_wx_display}")

wx_col_loc, wx_col_info = st.columns([1, 3])
with wx_col_loc:
    wx_location = st.selectbox(
        "Monitor location",
        list(SUBREGION_COORDS.keys()),
        index=1,
        key="wx_location",
    )

coords   = SUBREGION_COORDS[wx_location]
wx_data  = _fetch_weather(coords["lat"], coords["lon"])

if wx_data is None:
    st.warning("Unable to fetch live weather data from Open-Meteo. Check your internet connection and try again.")
else:
    wx_days = _parse_weather_days(wx_data)
    trig    = _weather_trigger_summary(wx_days)

    with wx_col_info:
        st.caption(
            f"Data: [Open-Meteo](https://open-meteo.com) · "
            f"Coordinates: {coords['lat']:.3f}°N, {abs(coords['lon']):.3f}°W · "
            f"Retrieved: {datetime.now().strftime('%d %b %Y, %H:%M')} · Cached 30 min"
        )

    # ── Day cards (today + last 3 days) ───────────────────────────────────────
    day_labels = ["3 Days Ago", "2 Days Ago", "Yesterday", "Today"]
    day_cols   = st.columns(4)

    for col, day, label in zip(day_cols, wx_days, day_labels):
        with col:
            desc, icon = WMO_META.get(day["code"], ("Unknown", "🌡️"))
            date_str   = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%b %d")
            max_t = f"{day['max_temp']:.1f}°C" if day["max_temp"] is not None else "N/A"
            min_t = f"{day['min_temp']:.1f}°C" if day["min_temp"] is not None else "N/A"

            if day["heat_day"]:
                card_color, bg = "#C62828", "#FFF5F5"
                badge          = "Heat Day"
            elif day["frost_day"]:
                card_color, bg = "#1565C0", "#F0F4FF"
                badge          = "Frost Day"
            else:
                card_color, bg = "#2E7D32", "#F5FFF5"
                badge          = "Normal"

            st.markdown(
                f"""
                <div class="wx-card" style="border-color:{card_color};background:{bg};">
                    <div class="wx-label">{label}</div>
                    <div class="wx-date">{date_str}</div>
                    <div class="wx-icon">{icon}</div>
                    <div class="wx-desc">{desc}</div>
                    <div class="wx-temp-max">&#8593; {max_t}</div>
                    <div class="wx-temp-min">&#8595; {min_t}</div>
                    <div class="wx-precip">&#128167; {day['precip']:.1f} mm</div>
                    <div class="wx-badge" style="color:{card_color};">{badge}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)

    # ── Trigger status cards ───────────────────────────────────────────────────
    st.markdown("#### Insurance Trigger Status")

    tc1, tc2, tc3 = st.columns(3)

    with tc1:
        heat_frac = trig["heat_count"] / HEAT_DAYS_TRIGGER
        if trig["heat_triggered"]:
            t_color, t_status = "#C62828", "PAYOUT TRIGGERED"
        elif trig["heat_count"] > 0:
            t_color  = "#F57C00"
            t_status = f"Accumulating ({trig['heat_count']}/{HEAT_DAYS_TRIGGER} days)"
        else:
            t_color, t_status = "#2E7D32", "No trigger"
        st.markdown(
            f"""
            <div class="trigger-card" style="border-color:{t_color};">
                <div class="trigger-icon"></div>
                <div class="trigger-title">Heat Trigger</div>
                <div class="trigger-desc">Days &ge;38 &deg;C in window<br>
                    {trig['heat_count']} of {HEAT_DAYS_TRIGGER} needed (seasonal)</div>
                <div class="trigger-status" style="color:{t_color};">{t_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tc2:
        if trig["frost_triggered"]:
            t_color, t_status = "#C62828", "PAYOUT TRIGGERED"
        elif trig["frost_count"] > 0:
            t_color  = "#1565C0"
            t_status = f"Accumulating ({trig['frost_count']}/{FROST_DAYS_TRIGGER} days)"
        else:
            t_color, t_status = "#2E7D32", "No trigger"
        st.markdown(
            f"""
            <div class="trigger-card" style="border-color:{t_color};">
                <div class="trigger-icon"></div>
                <div class="trigger-title">Frost Trigger</div>
                <div class="trigger-desc">Days &le;-2 &deg;C in window<br>
                    {trig['frost_count']} of {FROST_DAYS_TRIGGER} needed (seasonal)</div>
                <div class="trigger-status" style="color:{t_color};">{t_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tc3:
        dry = trig["consecutive_dry"]
        if dry >= 20:
            d_color, d_status = "#C62828", "Drought Risk"
        elif dry >= 7:
            d_color, d_status = "#F57C00", "Dry Spell"
        else:
            d_color, d_status = "#2E7D32", "Normal"
        st.markdown(
            f"""
            <div class="trigger-card" style="border-color:{d_color};">
                <div class="trigger-icon"></div>
                <div class="trigger-title">Drought Monitor</div>
                <div class="trigger-desc">Consecutive dry days (&lt;1 mm/day)<br>
                    {dry} day{"s" if dry != 1 else ""} (trigger: above 80th&nbsp;pct)</div>
                <div class="trigger-status" style="color:{d_color};">{d_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Overall payout banner ──────────────────────────────────────────────────
    any_triggered = trig["heat_triggered"] or trig["frost_triggered"]
    any_warning   = trig["consecutive_dry"] >= 7 or trig["heat_count"] > 0 or trig["frost_count"] > 0

    if any_triggered:
        b_color, b_bg = "#C62828", "#FFF0F0"
        b_text = (
            "PAYOUT CONDITION MET — A trigger threshold has been reached "
            "in the observed weather window. Policy review is recommended."
        )
    elif any_warning:
        b_color, b_bg = "#F57C00", "#FFF8E1"
        b_text = (
            "ELEVATED RISK — Some trigger-relevant weather conditions observed. "
            "Continue monitoring the forecast."
        )
    else:
        b_color, b_bg = "#2E7D32", "#F1F8E9"
        b_text = (
            "CONDITIONS NORMAL — No trigger events detected in the recent "
            "3-day weather window. All indicators within safe range."
        )

    st.markdown(
        f"""
        <div style="border-left:4px solid {b_color};background:{b_bg};
                    padding:12px 16px;border-radius:4px;margin-top:12px;">
            {b_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("---")

col_select, col_risk, col_info = st.columns([1, 1, 2])
with col_select:
    selected_subregion = st.selectbox("Select Demo Location / Risk Region", DISPLAY_SUBREGIONS)
with col_risk:
    selected_risk_type = st.selectbox("Risk Type", ["Heat", "Frost", "Drought", "All"])

df = load_history()
result = predict_risk_and_premium(selected_subregion, 12, 40_000, selected_risk_type)
canonical_subregion = result["subregion_used"]
sub_df = df[df["subregion"] == canonical_subregion].copy()


if sub_df.empty:
    st.warning("No model history is available for this risk profile.")
    st.stop()

# For combined cover, compute a combined trigger (any hazard fires) before aggregation.
sub_df = sub_df.copy()
sub_df["any_trigger"] = (
    (sub_df["heat_trigger"] == 1)
    | (sub_df["frost_trigger"] == 1)
    | (sub_df["drought_trigger"] == 1)
).astype(int)

# Map risk type to the correct column and chart config
RISK_CHART_CONFIG = {
    "Heat":    {"col": "heat_days_38",            "trigger_col": "heat_trigger",    "threshold": 5,    "y_label": "Average heat days >= 38 C",             "title": "Annual Heat Days >= 38 C"},
    "Frost":   {"col": "spring_severe_frost_days", "trigger_col": "frost_trigger",   "threshold": 3,    "y_label": "Average severe frost days (spring)",    "title": "Annual Severe Frost Days (Spring)"},
    "Drought": {"col": "max_consecutive_dry_days", "trigger_col": "drought_trigger", "threshold": None, "y_label": "Average max consecutive dry days",      "title": "Annual Max Consecutive Dry Days"},
    "All":    {"col": "climate_stress_year",      "trigger_col": "any_trigger",     "threshold": None, "y_label": "Share of sites with any climate stress", "title": "Annual Combined Climate Stress (Heat / Frost / Drought)"},
}
chart_cfg = RISK_CHART_CONFIG[selected_risk_type]

agg_cols = {
    chart_cfg["col"]: (chart_cfg["col"], "mean"),
    chart_cfg["trigger_col"]: (chart_cfg["trigger_col"], "max"),
    "climate_stress_year": ("climate_stress_year", "max"),
    "model_stress_probability": ("model_stress_probability", "mean"),
}
year_df = sub_df.groupby("year", as_index=False).agg(**agg_cols)
year_df["triggered"] = year_df[chart_cfg["trigger_col"]].astype(bool)
year_df["colour"] = year_df["triggered"].map({True: "Triggered (payout)", False: "No trigger"})

# Chart 1 - Trigger History
st.markdown("### 1. Historical Trigger Events")
st.markdown(f"Which years crossed the **{selected_risk_type}** trigger threshold?")

fig1 = px.bar(
    year_df,
    x="year",
    y=chart_cfg["col"],
    color="colour",
    color_discrete_map={"Triggered (payout)": BURGUNDY, "No trigger": GREY},
    labels={chart_cfg["col"]: chart_cfg["y_label"], "year": "Year", "colour": ""},
    title=f"{chart_cfg['title']} — {canonical_subregion}",
    height=400,
)
if chart_cfg["threshold"] is not None:
    fig1.add_hline(
        y=chart_cfg["threshold"],
        line_dash="dash",
        line_color=GOLD,
        annotation_text=f"Trigger ({chart_cfg['threshold']} days)",
        annotation_position="top left",
    )
fig1.update_layout(legend_title_text="", hovermode="x unified", xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)
st.caption(
    f"The trigger fired in {int(year_df['triggered'].sum())} of {len(year_df)} years "
    f"({year_df['triggered'].mean():.0%} historical frequency)."
)

st.markdown("---")

# Chart 2 - Feature Importance
st.markdown("### 2. What Drives Risk?")
st.markdown("Which climate factors matter most in our AI model?")

fi = result["feature_importance"]
fi_df = pd.DataFrame({"Feature": list(fi.keys()), "Importance": list(fi.values())}).sort_values(
    "Importance", ascending=True
)

fig2 = px.bar(
    fi_df,
    y="Feature",
    x="Importance",
    orientation="h",
    color_discrete_sequence=[BURGUNDY],
    title="Feature Importance in Risk Model",
    height=300,
)
fig2.update_layout(xaxis_title="Importance Score", yaxis_title="", hovermode="y unified")
st.plotly_chart(fig2, use_container_width=True)
st.caption("Higher values indicate stronger influence on the model's risk ranking.")

st.markdown("---")

# # Chart 3 - Trigger Alignment Diagnostic
# st.markdown("### 3. Trigger Alignment Diagnostic")
# st.markdown("How well does the selected trigger align with the broader climate-stress proxy?")

# col_scatter, col_explain = st.columns([2, 1])

# with col_scatter:
#     basis_df = year_df[["year", "triggered", "climate_stress_year", "model_stress_probability"]].copy()
#     basis_df.columns = ["Year", "Trigger Fired", "Climate Stress Year", "Model Stress Probability"]
#     basis_df["Match"] = basis_df["Trigger Fired"] == basis_df["Climate Stress Year"].astype(bool)
#     basis_df["Status"] = basis_df["Match"].map({True: "Match", False: "Mismatch (trigger ≠ stress proxy)"})

#     fig3 = px.scatter(
#         basis_df,
#         x="Year",
#         y="Trigger Fired",
#         color="Status",
#         color_discrete_map={"Match": BURGUNDY, "Mismatch (trigger ≠ stress proxy)": GOLD},
#         symbol="Climate Stress Year",
#         size="Model Stress Probability",
#         title=f"{selected_risk_type} Trigger vs Climate Stress Proxy",
#         height=350,
#     )
#     fig3.update_layout(hovermode="x unified", xaxis_tickangle=-45)
#     st.plotly_chart(fig3, use_container_width=True)

# with col_explain:
#     st.markdown(
#         """
# **What does this chart show?**

# This diagnostic compares when the objective climate trigger fires
# against when the broader climate-stress proxy is active.

# Mismatches (gold dots) indicate years where the two signals diverge.
# This is a **model-level diagnostic**, not a direct measure of basis risk:
# true basis risk measures the gap between the trigger and **actual farm losses**,
# which requires yield or claims data not yet available in this prototype.
# """
#     )

# st.markdown("---")

# Chart 4 - Premium Breakdown Donut
st.markdown("### 3. Where Your Premium Goes")

pricing = result["pricing_breakdown"]
labels = ["Expected Payout", "Risk Loading", "Admin Cost", "Margin"]
values = [
    pricing["expected_payout_eur"],
    pricing["risk_loading_eur"],
    pricing["admin_eur"],
    pricing["margin_eur"],
]
colors = [BURGUNDY, GOLD, GREY, "#8F8F8F"]

fig4 = go.Figure(
    data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textposition="auto",
            hovertemplate="<b>%{label}</b><br>EUR %{value:,.0f}<extra></extra>",
        )
    ]
)
fig4.update_layout(title_text="Premium Composition (EUR)", height=400, showlegend=True)
st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    f"""
**Composition explained:**
- **Expected payout:** EUR {pricing['expected_payout_eur']:,.0f}
- **Risk loading:** EUR {pricing['risk_loading_eur']:,.0f}
- **Admin cost:** EUR {pricing['admin_eur']:,.0f}
- **Margin:** EUR {pricing['margin_eur']:,.0f}
"""
)

st.markdown("---")

st.info(
    "This dashboard uses historical climate-stress proxies, not farm-level claims. "
    "Actual triggers and losses depend on real climate events and farm-specific conditions."
)
