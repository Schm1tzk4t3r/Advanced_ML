import streamlit as st

st.set_page_config(
    page_title="VinhaGuard AI",
    page_icon="🍷",
    layout="wide",
)

st.sidebar.image("https://via.placeholder.com/200x60/6B1C2E/FFFFFF?text=VinhaGuard+AI", use_container_width=True)
st.sidebar.markdown("*Transparent protection for Douro wine producers*")

st.title("VinhaGuard AI")
st.subheader("Parametric Climate Insurance for the Douro Valley")

st.markdown("""
---
**VinhaGuard** solves one of the most overlooked problems in Portuguese agriculture:
small wine producers in the Douro have no affordable, trustworthy way to insure
their harvest against extreme weather.

Our AI-powered platform provides **transparent, parametric insurance** — meaning
payouts are triggered automatically by objective climate data, with no adjusters,
no paperwork, and no disputes.

---
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Douro Subregions Covered", "6")
    st.caption("Baixo Corgo · Cima Corgo · Douro Superior · Pinhão · Régua · Vila Nova de Foz Côa")

with col2:
    st.metric("Avg. Payout Time", "< 72 hours")
    st.caption("Triggered automatically when climate thresholds are met")

with col3:
    st.metric("AI Risk Model", "LogReg + RF")
    st.caption("Trained on 30+ years of Douro climate data")

st.markdown("---")
st.info("Use the sidebar to navigate to **Risk Assessment**, **Dashboard**, **Pricing Explainer**, or the **Chatbot**.")
