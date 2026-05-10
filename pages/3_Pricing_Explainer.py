import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Pricing Explainer - VinhaGuard", page_icon="🍷", layout="wide")

BURGUNDY = "#6B1C2E"
GOLD = "#B8860B"

st.title("Pricing Explainer")
st.markdown("How we calculate your premium")
st.markdown("---")

st.markdown("""
### The VinhaGuard Pricing Formula

The annual premium is computed as:

> **Premium = Insured Value x Risk Probability x Loss Given Trigger x (1 + Risk Loading) x (1 + Admin Margin)**

Where:
- **Risk Probability** — output of the AI model for your subregion and risk type
- **Loss Given Trigger** — historical average crop loss (%) when the trigger fires
- **Risk Loading** — buffer for model uncertainty and reinsurance cost (~25%)
- **Admin Margin** — platform and operational costs (~15%)
""")

st.markdown("---")
st.subheader("Interactive Premium Calculator")

col1, col2 = st.columns(2)
with col1:
    insured_value = st.number_input("Insured Value (€)", min_value=1_000, max_value=5_000_000, value=40_000, step=1_000)
    risk_prob = st.slider("Risk Probability (%)", min_value=0, max_value=100, value=62) / 100
    loss_given_trigger = st.slider("Loss Given Trigger (%)", min_value=10, max_value=100, value=55) / 100

with col2:
    risk_loading = st.slider("Risk Loading (%)", min_value=0, max_value=50, value=25) / 100
    admin_margin = st.slider("Admin Margin (%)", min_value=0, max_value=30, value=15) / 100

expected_loss = insured_value * risk_prob * loss_given_trigger
premium = expected_loss * (1 + risk_loading) * (1 + admin_margin)

st.metric("Calculated Annual Premium", f"€{premium:,.0f}", f"{premium / insured_value:.2%} of insured value")

# Waterfall chart showing premium build-up
fig = go.Figure(go.Waterfall(
    name="Premium Build-up",
    orientation="v",
    measure=["relative", "relative", "relative", "total"],
    x=["Expected Loss", "Risk Loading", "Admin Margin", "Total Premium"],
    y=[expected_loss, expected_loss * risk_loading, expected_loss * (1 + risk_loading) * admin_margin, 0],
    connector={"line": {"color": BURGUNDY}},
    increasing={"marker": {"color": BURGUNDY}},
    totals={"marker": {"color": GOLD}},
))
fig.update_layout(title="Premium Build-up Waterfall", yaxis_title="€")
st.plotly_chart(fig, use_container_width=True)
st.caption("For illustrative purposes. Actual values depend on model output.")

st.markdown("---")
st.markdown("""
### Why Parametric?

Traditional indemnity insurance requires an adjuster to visit your farm and assess losses —
a process that can take weeks or months. VinhaGuard pays automatically when objective
climate data crosses a pre-agreed threshold, with **no adjuster, no paperwork, no disputes**.

| | Traditional Insurance | VinhaGuard (Parametric) |
|---|---|---|
| Trigger | Assessed farm loss | Objective climate data |
| Payout time | Weeks-months | < 72 hours |
| Transparency | Limited | Full (AI + data) |
| Basis risk | Low | Present — disclosed |
| Premium | High (overhead) | Actuarially priced |
""")
