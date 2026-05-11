import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predict_risk_and_premium

st.markdown("""
<style>
    .risk-high { color: #DC3545; font-weight: 700; }
    .risk-medium { color: #FFC107; font-weight: 700; }
    .risk-low { color: #28A745; font-weight: 700; }

    .result-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        padding: 25px;
        margin: 15px 0;
    }

    .premium-highlight {
        background: linear-gradient(135deg, #6B1C2E 0%, #8B2E3E 100%);
        color: white;
        padding: 30px;
        border-radius: 8px;
        text-align: center;
        margin: 20px 0;
    }

    .breakdown-table {
        background: #F8F9FA;
        border-radius: 8px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Climate Risk Assessment")
st.markdown("Evaluate your vineyard's climate risk and get a customized insurance quote.")
st.markdown("---")

SUBREGIONS = [
    "Baixo Corgo",
    "Cima Corgo",
    "Douro Superior",
    "Pinhão",
    "Régua",
    "Vila Nova de Foz Côa",
]

# Input form with better layout
with st.form("risk_form", border=True):
    st.subheader("📋 Your Vineyard")

    col1, col2 = st.columns(2)

    with col1:
        subregion = st.selectbox(
            "🗺️ Douro Sub-Region",
            SUBREGIONS,
            help="Select the closest sub-region to your vineyard"
        )
        area_ha = st.slider(
            "📏 Vineyard Area (hectares)",
            min_value=1, max_value=500, value=12,
            help="Total area of vineyard under insurance"
        )

    with col2:
        insured_value = st.number_input(
            "💰 Insured Crop Value (€)",
            min_value=1_000, max_value=5_000_000, value=40_000, step=5_000,
            help="Estimated value of this season's harvest"
        )
        risk_type = st.radio(
            "⛈️ Climate Risk Type",
            ["Heat", "Frost", "Both"],
            horizontal=True,
            help="Which climate hazards concern you most?"
        )

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        elevation = st.slider(
            "🏔️ Elevation (meters above sea level)",
            min_value=0, max_value=900, value=200,
            help="Higher elevation generally means cooler temps"
        )

    submitted = st.form_submit_button("📊 Calculate Risk & Quote", type="primary", use_container_width=True)

if submitted:
    if insured_value == 0 or area_ha == 0:
        st.error("❌ Insured value and area must be greater than zero.")
    else:
        with st.spinner("🔄 Running climate risk model..."):
            try:
                result = predict_risk_and_premium(subregion, area_ha, insured_value, risk_type, elevation)
            except Exception as e:
                st.error(f"⚠️ Model error: {e}")
                st.stop()

        st.markdown("---")
        st.subheader("📈 Your Risk Assessment")

        risk_prob = result["risk_prob"]
        premium_eur = result["premium_eur"]
        trigger = result["trigger_threshold"]
        basis_risk = result["basis_risk_pct"]

        # Risk gauge with color coding
        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)

            if risk_prob < 0.30:
                risk_class = "risk-low"
                risk_label = "✅ LOW RISK"
                risk_color = "#28A745"
            elif risk_prob < 0.60:
                risk_class = "risk-medium"
                risk_label = "⚠️ MEDIUM RISK"
                risk_color = "#FFC107"
            else:
                risk_class = "risk-high"
                risk_label = "🔴 HIGH RISK"
                risk_color = "#DC3545"

            st.markdown(f"<h3 style='margin-top: 0; color: {risk_color};'>{risk_prob:.0%}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 0.95rem; color: {risk_color}; font-weight: bold; margin: 5px 0;'>{risk_label}</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.85rem; color: #666; margin: 10px 0 0 0;'>Climate Stress Probability</p>", unsafe_allow_html=True)

            st.progress(risk_prob)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            st.markdown(f"**Trigger Condition:**")
            st.markdown(f"> {trigger}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Basis Risk", f"{basis_risk:.1f}%", help="Mismatch between trigger and actual loss")
            with col_b:
                st.metric("Premium %", f"{premium_eur / insured_value:.1%}", help="Annual premium as % of insured value")

            st.markdown("</div>", unsafe_allow_html=True)

        # Premium card
        st.markdown(f"""
        <div class='premium-highlight'>
            <h2 style='margin-top: 0;'>Annual Premium</h2>
            <h1 style='margin: 0; font-size: 3rem;'>€{premium_eur:,.0f}</h1>
            <p style='margin-bottom: 0; opacity: 0.9;'>{premium_eur / insured_value:.1%} of your insured value</p>
        </div>
        """, unsafe_allow_html=True)

        # Breakdown
        st.subheader("💳 Premium Breakdown")
        expected_payout = premium_eur * 0.60
        risk_loading = premium_eur * 0.25
        admin = premium_eur * 0.15

        breakdown_data = {
            "Component": ["Expected Payout", "Risk Loading", "Admin & Reinsurance", "TOTAL"],
            "Amount": [f"€{expected_payout:,.0f}", f"€{risk_loading:,.0f}", f"€{admin:,.0f}", f"€{premium_eur:,.0f}"],
            "Share": ["60%", "25%", "15%", "100%"],
        }

        st.dataframe(breakdown_data, use_container_width=True, hide_index=True)
        st.caption("💡 Expected Payout reflects the historical probability that the trigger fires and you receive a claim payout. Risk Loading covers model uncertainty and reinsurance. Admin covers platform operations.")

        st.info("ℹ️ This quote is illustrative and based on the climate risk model. Actual premiums may vary based on reinsurance costs and market conditions.", icon="ℹ️")
