import streamlit as st
import plotly.graph_objects as go

BURGUNDY = "#6B1C2E"
GOLD = "#B8860B"

st.title("How It's Priced")
st.markdown("Understand exactly how your insurance premium is calculated.")
st.markdown("---")

# Formula section with better styling
st.markdown("""
### The VinhaGuard Pricing Formula

Our actuarial model is transparent and rule-based:
""")

st.markdown("""
<div style="background: linear-gradient(135deg, #F5F5F5 0%, #FAFAFA 100%); padding: 25px; border-radius: 8px; border-left: 4px solid #6B1C2E;">

**Premium = Expected Loss × (1 + Risk Loading) × (1 + Admin Margin)**

Where:
- **Expected Loss** = Insured Value × Risk Probability × Historical Loss Rate
- **Risk Probability** = AI model output (70% historical + 30% model blend)
- **Historical Loss Rate** = % of crop lost when trigger fires (varies by risk type)
- **Risk Loading** ≈ 25% (uncertainty buffer + reinsurance)
- **Admin Margin** ≈ 15% (platform operations)

</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Interactive calculator
st.markdown("### Interactive Premium Calculator")
st.markdown("Adjust the sliders below to see how each component affects price:")

col1, col2, col3 = st.columns(3)

with col1:
    insured_value = st.number_input("💰 Insured Value (€)", min_value=1_000, max_value=5_000_000, value=40_000, step=5_000)
    risk_prob = st.slider("📊 Risk Probability (%)", min_value=0, max_value=100, value=62) / 100
    loss_given_trigger = st.slider("📉 Loss if Trigger Fires (%)", min_value=10, max_value=100, value=55) / 100

with col2:
    risk_loading = st.slider("🛡️ Risk Loading (%)", min_value=0, max_value=50, value=25) / 100
    admin_margin = st.slider("🏢 Admin Margin (%)", min_value=0, max_value=30, value=15) / 100

with col3:
    # Calculations
    expected_loss = insured_value * risk_prob * loss_given_trigger
    risk_load_amount = expected_loss * risk_loading
    admin_amount = expected_loss * (1 + risk_loading) * admin_margin
    premium = expected_loss * (1 + risk_loading) * (1 + admin_margin)

    st.metric("Expected Loss", f"€{expected_loss:,.0f}", f"({risk_prob:.0%} × {loss_given_trigger:.0%} of value)")
    st.metric("+ Risk Loading", f"€{risk_load_amount:,.0f}")
    st.metric("Final Premium", f"€{premium:,.0f}", f"{premium / insured_value:.1%} of value")

st.markdown("---")

# Waterfall chart
st.markdown("### Premium Build-up Waterfall")
st.markdown("Follow the money from risk to your final premium:")

fig = go.Figure(go.Waterfall(
    name="Premium Build-up",
    orientation="v",
    measure=["relative", "relative", "relative", "total"],
    x=["Expected Loss", "Risk Loading", "Admin Margin", "Your Annual Premium"],
    y=[expected_loss, risk_load_amount, admin_amount, 0],
    connector={"line": {"color": BURGUNDY}},
    increasing={"marker": {"color": BURGUNDY}},
    totals={"marker": {"color": GOLD}},
    text=[f"€{expected_loss:,.0f}", f"€{risk_load_amount:,.0f}", f"€{admin_amount:,.0f}", f"€{premium:,.0f}"],
    textposition="outside",
))
fig.update_layout(title="Premium Build-up Waterfall", yaxis_title="€", height=450, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Comparison table
st.markdown("### Parametric vs Traditional Insurance")

comparison_data = {
    "Aspect": [
        "Trigger",
        "Payout Time",
        "Transparency",
        "Basis Risk",
        "Premium",
        "Paperwork",
    ],
    "Traditional Insurance": [
        "Farm inspector asses loss",
        "Weeks–months",
        "Hidden pricing",
        "Very low",
        "High (overhead)",
        "Extensive claims forms",
    ],
    "VinhaGuard (Parametric)": [
        "Objective climate data",
        "< 72 hours",
        "Formula-based, transparent",
        "Present (disclosed)",
        "Actuarially fair",
        "Minimal — automatic",
    ],
}

st.dataframe(comparison_data, use_container_width=True, hide_index=True)

st.markdown("""
---

### Why Parametric?

**The old model is broken:**
- Adjuster fees = high premiums
- Weeks of investigation = delayed payouts
- Disputes over whether loss occurred = litigation
- Small producers priced out entirely

**Parametric flips the script:**
- Objective trigger (weather data) = no disputes
- Automatic payout = fast cash
- Transparent formula = trust
- AI + data = accurate pricing for all farm sizes
""")

st.info("""
⚠️ **Trade-off:** Basis risk is inherent in parametric insurance. We can't eliminate it,
but we disclose it and calibrate triggers to minimize it. This is the price of speed and transparency.
""", icon="ℹ️")

st.markdown("---")
st.caption("💡 All figures above are illustrative for educational purposes.")
