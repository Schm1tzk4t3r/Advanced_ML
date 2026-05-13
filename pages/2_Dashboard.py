import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predict_risk_and_premium

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

col_select, col_risk, col_info = st.columns([1, 1, 2])
with col_select:
    selected_subregion = st.selectbox("Select Demo Location / Risk Region", DISPLAY_SUBREGIONS)
with col_risk:
    selected_risk_type = st.selectbox("Risk Type", ["Heat", "Frost", "Drought", "Both"])

df = load_history()
result = predict_risk_and_premium(selected_subregion, 12, 40_000, selected_risk_type)
canonical_subregion = result["subregion_used"]
sub_df = df[df["subregion"] == canonical_subregion].copy()

with col_info:
    st.info(result["risk_profile_note"])
    st.caption(
        f"Dashboard uses the richer model artifact: {len(sub_df):,} location-year rows "
        f"across {result['n_locations']} historical vineyard sites for this profile."
    )

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
    "Both":    {"col": "climate_stress_year",      "trigger_col": "any_trigger",     "threshold": None, "y_label": "Share of sites with any climate stress", "title": "Annual Combined Climate Stress (Heat / Frost / Drought)"},
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

# Chart 3 - Trigger Alignment Diagnostic
st.markdown("### 3. Trigger Alignment Diagnostic")
st.markdown("How well does the selected trigger align with the broader climate-stress proxy?")

col_scatter, col_explain = st.columns([2, 1])

with col_scatter:
    basis_df = year_df[["year", "triggered", "climate_stress_year", "model_stress_probability"]].copy()
    basis_df.columns = ["Year", "Trigger Fired", "Climate Stress Year", "Model Stress Probability"]
    basis_df["Match"] = basis_df["Trigger Fired"] == basis_df["Climate Stress Year"].astype(bool)
    basis_df["Status"] = basis_df["Match"].map({True: "Match", False: "Mismatch (trigger ≠ stress proxy)"})

    fig3 = px.scatter(
        basis_df,
        x="Year",
        y="Trigger Fired",
        color="Status",
        color_discrete_map={"Match": BURGUNDY, "Mismatch (trigger ≠ stress proxy)": GOLD},
        symbol="Climate Stress Year",
        size="Model Stress Probability",
        title=f"{selected_risk_type} Trigger vs Climate Stress Proxy",
        height=350,
    )
    fig3.update_layout(hovermode="x unified", xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

with col_explain:
    st.markdown(
        """
**What does this chart show?**

This diagnostic compares when the objective climate trigger fires
against when the broader climate-stress proxy is active.

Mismatches (gold dots) indicate years where the two signals diverge.
This is a **model-level diagnostic**, not a direct measure of basis risk:
true basis risk measures the gap between the trigger and **actual farm losses**,
which requires yield or claims data not yet available in this prototype.
"""
    )

st.markdown("---")

# Chart 4 - Premium Breakdown Donut
st.markdown("### 4. Where Your Premium Goes")

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

# Section 5 - Model performance figures
st.markdown("### 5. AI Model Performance")
st.markdown(
    "Evaluation metrics from training on 30+ years of Douro climate data. "
    "Random Forest was selected for its higher ROC-AUC (0.970 vs 0.949). "
    "Note: Logistic Regression has a better Brier score (0.071 vs 0.115), "
    "meaning it is better probability-calibrated — relevant context when interpreting premium outputs."
)

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")

fig_files = {
    "ROC Curve": "ml_roc_curve.png",
    "Precision-Recall": "ml_precision_recall_curve.png",
    "Feature Importance": "ml_feature_importance.png",
    "Calibration Curve": "ml_calibration_curve.png",
    "Confusion Matrix": "ml_confusion_matrix.png",
}

available = {
    label: os.path.join(FIGURES_DIR, fname)
    for label, fname in fig_files.items()
    if os.path.exists(os.path.join(FIGURES_DIR, fname))
}

if available:
    tabs = st.tabs(list(available.keys()))
    for tab, (label, path) in zip(tabs, available.items()):
        with tab:
            st.image(path, use_container_width=True)
else:
    st.info("Model figure files not found in docs/figures/.")

st.markdown("---")
st.info(
    "This dashboard uses historical climate-stress proxies, not farm-level claims. "
    "Actual triggers and losses depend on real climate events and farm-specific conditions."
)
