import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predict_risk_and_premium

st.markdown("""
<style>
    .chart-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

BURGUNDY = "#6B1C2E"
GOLD = "#B8860B"
GREY = "#CCCCCC"

st.title("Climate Risk Dashboard")
st.markdown("Historical analysis and model explainability for your selected region.")
st.markdown("---")

# Region selector with better UX
col_select, col_info = st.columns([1, 3])
with col_select:
    selected_subregion = st.selectbox(
        "Select Sub-Region",
        ["Baixo Corgo", "Cima Corgo", "Douro Superior", "Pinhão", "Régua", "Vila Nova de Foz Côa"],
    )

@st.cache_data
def load_history():
    parquet_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "douro_climate.parquet")
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    import numpy as np
    rng = np.random.default_rng(42)
    years = list(range(1990, 2024))
    subregions = ["Baixo Corgo", "Cima Corgo", "Douro Superior", "Pinhão", "Régua", "Vila Nova de Foz Côa"]
    rows = []
    for sr in subregions:
        for yr in years:
            rows.append({
                "year": yr,
                "subregion": sr,
                "heat_days_38": int(rng.integers(0, 25)),
                "frost_days": int(rng.integers(0, 10)),
                "ndvi": round(float(rng.uniform(0.3, 0.8)), 3),
                "label": int(rng.integers(0, 2)),
            })
    return pd.DataFrame(rows)

df = load_history()
if df["subregion"].eq(selected_subregion).sum() == 0:
    st.warning("No data for selected subregion.")
    st.stop()

sub_df = df[df["subregion"] == selected_subregion].copy()
TRIGGER_THRESHOLD = 14

# Chart 1 – Trigger History
st.markdown("### 1️⃣ Historical Trigger Events")
st.markdown("Which years had heat stress above the trigger threshold?")

sub_df["triggered"] = sub_df["heat_days_38"] >= TRIGGER_THRESHOLD
sub_df["colour"] = sub_df["triggered"].map({True: "Triggered (payout)", False: "No trigger"})

fig1 = px.bar(
    sub_df,
    x="year",
    y="heat_days_38",
    color="colour",
    color_discrete_map={"Triggered (payout)": BURGUNDY, "No trigger": GREY},
    labels={"heat_days_38": "Heat Days ≥ 38°C", "year": "Year", "colour": ""},
    title=f"Annual Heat Days ≥ 38°C — {selected_subregion}",
    height=400,
)
fig1.add_hline(
    y=TRIGGER_THRESHOLD,
    line_dash="dash",
    line_color=GOLD,
    annotation_text=f"Trigger ({TRIGGER_THRESHOLD} days)",
    annotation_position="top left",
)
fig1.update_layout(legend_title_text="", hovermode="x unified", xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)
st.caption(f"💡 The trigger fired in **{sub_df['triggered'].sum()} of {len(sub_df)}** years ({sub_df['triggered'].mean():.0%} historical frequency).")

st.markdown("---")

# Chart 2 – Feature Importance
st.markdown("### 2️⃣ What Drives Risk?")
st.markdown("Which climate factors matter most in our AI model?")

result = predict_risk_and_premium(selected_subregion, 12, 40_000, "Heat")
fi = result["feature_importance"]
fi_df = pd.DataFrame({"Feature": list(fi.keys()), "Importance": list(fi.values())}).sort_values("Importance", ascending=True)

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
st.caption("🔍 Higher values = more impact on your risk score. Heat days dominate; elevation provides protection.")

st.markdown("---")

# Chart 3 – Basis Risk Panel
st.markdown("### 3️⃣ Basis Risk: The Reality Gap")
st.markdown("When does the trigger not match reality?")

col_scatter, col_explain = st.columns([2, 1])

with col_scatter:
    basis_df = sub_df[["year", "triggered", "label"]].copy()
    basis_df.columns = ["Year", "Trigger Fired", "Estimated Loss"]
    basis_df["Match"] = basis_df["Trigger Fired"] == basis_df["Estimated Loss"]
    basis_df["Status"] = basis_df["Match"].map({True: "Match", False: "Mismatch (basis risk)"})

    fig3 = px.scatter(
        basis_df,
        x="Year",
        y="Trigger Fired",
        color="Status",
        color_discrete_map={"Match": BURGUNDY, "Mismatch (basis risk)": GOLD},
        symbol="Estimated Loss",
        title="Trigger vs Estimated Loss Alignment",
        height=350,
    )
    fig3.update_layout(hovermode="x unified", xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

with col_explain:
    st.markdown("""
    **What is Basis Risk?**

    Basis risk = mismatch between:
    - When the **trigger fires** (objective climate data)
    - When you **actually suffer losses** (your farm reality)

    **Why it matters:**
    - ✅ Trigger fires, no loss → you keep the payout
    - ❌ No trigger, real loss → you're not covered
    - 🎯 Goal: minimize this gap through calibration

    VinhaGuard discloses basis risk explicitly — no false promises.
    """)

st.markdown("---")

# Chart 4 – Premium Breakdown Donut
st.markdown("### 4️⃣ Where Your Premium Goes")

labels = ["Expected Payout", "Risk Loading", "Admin & Reinsurance"]
values = [60, 25, 15]
colors = [BURGUNDY, GOLD, GREY]

fig4 = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hole=0.4,
    marker_colors=colors,
    textposition="auto",
    hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
)])
fig4.update_layout(title_text="Premium Composition (%)", height=400, showlegend=True)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
**Composition explained:**
- 💰 **Expected Payout** (60%) — Historical likelihood that trigger fires
- 🛡️ **Risk Loading** (25%) — Buffer for model uncertainty
- 🏢 **Admin** (15%) — Platform ops & reinsurance
""")

st.markdown("---")

# Section 5 – Model performance figures
st.markdown("### 5️⃣ AI Model Performance")
st.markdown("Evaluation metrics from training on 30+ years of Douro climate data:")

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")

fig_files = {
    "ROC Curve":              "ml_roc_curve.png",
    "Precision–Recall":       "ml_precision_recall_curve.png",
    "Feature Importance":     "ml_feature_importance.png",
    "Calibration Curve":      "ml_calibration_curve.png",
    "Confusion Matrix":       "ml_confusion_matrix.png",
}

available = {label: os.path.join(FIGURES_DIR, fname)
             for label, fname in fig_files.items()
             if os.path.exists(os.path.join(FIGURES_DIR, fname))}

if available:
    tab_labels = list(available.keys())
    tabs = st.tabs(tab_labels)
    for tab, (label, path) in zip(tabs, available.items()):
        with tab:
            st.image(path, use_container_width=True)
else:
    st.info("Model figure files not found in docs/figures/.")

st.markdown("---")
st.info("📌 All data on this dashboard is illustrative. Actual triggers and losses depend on real climate events and farm-specific conditions.", icon="ℹ️")
