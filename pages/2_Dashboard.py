import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predict_risk_and_premium

st.set_page_config(page_title="Dashboard – VinhaGuard", page_icon="🍷", layout="wide")

BURGUNDY = "#6B1C2E"
GOLD = "#B8860B"
GREY = "#CCCCCC"

@st.cache_data
def load_history():
    parquet_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "douro_climate.parquet")
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    # Synthetic fallback — label clearly
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


st.title("Climate Risk Dashboard")
st.markdown("---")

selected_subregion = st.selectbox(
    "Select Subregion",
    ["Baixo Corgo", "Cima Corgo", "Douro Superior", "Pinhão", "Régua", "Vila Nova de Foz Côa"],
)

df = load_history()
if df["subregion"].eq(selected_subregion).sum() == 0:
    st.warning("No data for selected subregion.")
    st.stop()

sub_df = df[df["subregion"] == selected_subregion].copy()

TRIGGER_THRESHOLD = 14

# Chart 1 – Trigger History
st.subheader("Trigger History")
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
)
fig1.add_hline(
    y=TRIGGER_THRESHOLD,
    line_dash="dash",
    line_color=GOLD,
    annotation_text=f"Trigger threshold ({TRIGGER_THRESHOLD} days)",
    annotation_position="top left",
)
fig1.update_layout(legend_title_text="")
st.plotly_chart(fig1, use_container_width=True)

# Chart 2 – Feature Importance
st.subheader("Model Feature Importance")
result = predict_risk_and_premium(selected_subregion, 12, 40_000, "Heat")
fi = result["feature_importance"]
fi_df = pd.DataFrame({"Feature": list(fi.keys()), "Importance": list(fi.values())}).sort_values("Importance")

fig2 = px.bar(
    fi_df,
    x="Importance",
    y="Feature",
    orientation="h",
    color_discrete_sequence=[BURGUNDY],
    title="Feature Importance (Risk Model)",
    labels={"Importance": "Importance Score", "Feature": ""},
)
st.plotly_chart(fig2, use_container_width=True)

# Chart 3 – Basis Risk Panel
st.subheader("Basis Risk Analysis")
st.caption("For illustrative purposes. Actual loss data depends on farm-level records.")

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
        title=f"Trigger vs Estimated Loss — {selected_subregion}",
        labels={"Trigger Fired": "Trigger Fired (1=Yes)", "Estimated Loss": "Loss Occurred"},
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_explain:
    st.markdown("""
**O que é o risco de base?**

O risco de base ocorre quando o gatilho climático é ativado mas o agricultor não sofre perdas reais,
ou quando o agricultor sofre perdas mas o gatilho não é ativado.

VinhaGuard minimiza o risco de base calibrando os gatilhos com dados históricos de 30+ anos para
cada sub-região do Douro.

*Pontos vermelhos = anos em que o gatilho e as perdas coincidem (bom alinhamento).*
*Pontos dourados = anos com risco de base.*
""")

# Chart 4 – Premium Breakdown Donut
st.subheader("Premium Breakdown")

labels = ["Expected Payout", "Risk Loading", "Admin & Reinsurance"]
values = [60, 25, 15]
colors = [BURGUNDY, GOLD, GREY]

fig4 = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hole=0.5,
    marker_colors=colors,
)])
fig4.update_layout(title_text="Premium Composition (%)", showlegend=True)
st.plotly_chart(fig4, use_container_width=True)
st.caption("For illustrative purposes. Actual splits depend on model output and reinsurance terms.")
