import streamlit as st

st.set_page_config(
    page_title="VinhaGuard AI",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #120408 0%, #1f0810 50%, #2a0d18 100%);
    border-right: 1px solid #4a1020;
}
[data-testid="stSidebarNav"] a {
    color: #ddb8c0 !important;
    border-radius: 6px;
    transition: background 0.2s;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(107,28,46,0.4) !important;
}
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: rgba(107,28,46,0.6) !important;
}
[data-testid="stSidebarNav"] span {
    color: #ddb8c0 !important;
}

h1, h2, h3 {
    font-family: Georgia, 'Times New Roman', serif;
}

[data-testid="metric-container"] {
    background: white;
    border: 1px solid #f0e0e3;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 1px 6px rgba(107,28,46,0.07);
}
[data-testid="metric-container"] label {
    color: #6B1C2E !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="text-align:center; padding: 24px 12px 16px;">
    <div style="font-size: 2.2rem; margin-bottom: 6px;">🍷</div>
    <div style="color: #e8c4cc; font-size: 1rem; font-weight: 700; letter-spacing: 3px;
                font-family: Georgia, serif; text-transform: uppercase;">VinhaGuard</div>
    <div style="color: #7a4a54; font-size: 0.68rem; letter-spacing: 2px; margin-top: 3px;
                text-transform: uppercase;">Climate Insurance · Douro</div>
</div>
<hr style="border: none; border-top: 1px solid #4a1020; margin: 0 12px 8px;">
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/home.py",                title="Overview",           icon="🏠", default=True),
    st.Page("pages/1_Risk_Assessment.py",   title="Risk Assessment",    icon="🎯"),
    st.Page("pages/2_Dashboard.py",         title="Climate Dashboard",  icon="📊"),
    st.Page("pages/3_Pricing_Explainer.py", title="How It's Priced",    icon="💰"),
    st.Page("pages/4_Chatbot.py",           title="AI Assistant",       icon="💬"),
])
pg.run()
