import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predict_risk_and_premium

st.set_page_config(page_title="Risk Assessment – VinhaGuard", page_icon="🍷", layout="wide")

st.title("Climate Risk Assessment")
st.markdown("---")

SUBREGIONS = [
    "Baixo Corgo",
    "Cima Corgo",
    "Douro Superior",
    "Pinhão",
    "Régua",
    "Vila Nova de Foz Côa",
]

with st.form("risk_form"):
    st.subheader("Vineyard Parameters")

    col1, col2 = st.columns(2)
    with col1:
        subregion = st.selectbox("Subregion", SUBREGIONS)
        area_ha = st.slider("Vineyard Area (ha)", min_value=1, max_value=500, value=12)
        risk_type = st.radio("Risk Type", ["Heat", "Frost", "Both"], horizontal=True)

    with col2:
        insured_value = st.number_input("Insured Value (€)", min_value=1_000, max_value=5_000_000, value=40_000, step=1_000)
        with st.expander("Optional (advanced)"):
            elevation = st.slider("Elevation (m)", min_value=0, max_value=900, value=200)

    submitted = st.form_submit_button("Assess Risk", type="primary")

if submitted:
    if insured_value == 0 or area_ha == 0:
        st.error("Insured value and area must be greater than zero.")
    else:
        with st.spinner("Running climate risk model..."):
            try:
                result = predict_risk_and_premium(subregion, area_ha, insured_value, risk_type, elevation)
            except Exception as e:
                st.error(f"Model error: {e}")
                st.stop()

        st.markdown("---")
        st.subheader("Risk Assessment Results")

        risk_prob = result["risk_prob"]
        premium_eur = result["premium_eur"]
        trigger = result["trigger_threshold"]
        basis_risk = result["basis_risk_pct"]

        col_gauge, col_premium = st.columns(2)

        with col_gauge:
            if risk_prob < 0.30:
                colour = "normal"
                label = "Low Risk"
            elif risk_prob < 0.60:
                colour = "off"
                label = "Medium Risk"
            else:
                colour = "inverse"
                label = "High Risk"

            st.metric("Climate Stress Probability", f"{risk_prob:.0%}", label_visibility="visible")
            st.progress(risk_prob)
            st.caption(label)

            if risk_prob >= 0.60:
                st.warning(f"**Trigger condition:** {trigger}")
            elif risk_prob >= 0.30:
                st.info(f"**Trigger condition:** {trigger}")
            else:
                st.success(f"**Trigger condition:** {trigger}")

        with col_premium:
            st.metric("Annual Premium", f"€{premium_eur:,.0f}")
            st.caption(f"{premium_eur / insured_value:.1%} of insured value")
            st.metric("Basis Risk", f"{basis_risk:.1f}%")
            st.caption("Gap between trigger and actual farm loss")

        st.markdown("#### Premium Breakdown")
        expected_payout = premium_eur * 0.60
        risk_loading = premium_eur * 0.25
        admin = premium_eur * 0.15
        st.dataframe(
            {
                "Component": ["Expected Payout", "Risk Loading", "Admin & Reinsurance"],
                "Amount (€)": [f"{expected_payout:,.0f}", f"{risk_loading:,.0f}", f"{admin:,.0f}"],
                "Share": ["60%", "25%", "15%"],
            },
            use_container_width=True,
            hide_index=True,
        )
        st.caption("For illustrative purposes. Actual values depend on model output.")
