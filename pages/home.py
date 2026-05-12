import streamlit as st

st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #0e0307 0%, #2a0910 25%, #6B1C2E 60%, #7a3018 80%, #a06010 100%);
    border-radius: 16px;
    padding: 72px 56px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 2.5rem;
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        -55deg, transparent, transparent 14px,
        rgba(255,255,255,0.012) 14px, rgba(255,255,255,0.012) 28px
    );
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(184,134,11,0.25);
    border: 1px solid rgba(184,134,11,0.6);
    color: #f0d878;
    padding: 5px 18px;
    border-radius: 20px;
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    font-family: Georgia, serif;
    font-size: 3.2rem;
    font-weight: 700;
    margin: 0 0 16px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.4);
    line-height: 1.15;
}
.hero p {
    color: rgba(255,255,255,0.82);
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.75;
}
.stat-card {
    background: white;
    border: 1px solid #f0e0e3;
    border-radius: 12px;
    padding: 28px 18px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(107,28,46,0.07);
    height: 100%;
}
.stat-card .num {
    font-family: Georgia, serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #6B1C2E;
    line-height: 1;
}
.stat-card .lbl {
    color: #444;
    font-size: 0.88rem;
    font-weight: 600;
    margin-top: 6px;
}
.stat-card .cap {
    color: #999;
    font-size: 0.75rem;
    margin-top: 6px;
    line-height: 1.4;
}
.feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 6px;
}
.feature-item {
    background: #fafafa;
    border: 1px solid #ede8e9;
    border-left: 3px solid #6B1C2E;
    border-radius: 8px;
    padding: 16px 18px;
}
.feature-item strong {
    display: block;
    font-size: 0.9rem;
    color: #1F1F1F;
    margin-bottom: 4px;
}
.feature-item span {
    font-size: 0.8rem;
    color: #666;
    line-height: 1.5;
}
.region-card {
    background: linear-gradient(160deg, #1a0510, #2f1020);
    border-radius: 12px;
    padding: 28px 24px;
    color: white;
}
.region-card .title {
    font-family: Georgia, serif;
    font-size: 1rem;
    color: #ddb8c0;
    margin-bottom: 16px;
    letter-spacing: 0.5px;
}
.region-pill {
    background: rgba(107,28,46,0.45);
    border: 1px solid rgba(107,28,46,0.7);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 0.83rem;
    color: #e8d0d4;
    margin-bottom: 8px;
}
.step-box {
    background: white;
    border: 1px solid #f0e0e3;
    border-radius: 10px;
    padding: 24px 16px;
    text-align: center;
    box-shadow: 0 1px 6px rgba(107,28,46,0.06);
    height: 100%;
}
.step-num {
    font-family: Georgia, serif;
    font-size: 0.68rem;
    color: #B8860B;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.step-icon { font-size: 1.8rem; margin-bottom: 10px; }
.step-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; color: #1F1F1F; }
.step-desc { font-size: 0.79rem; color: #666; line-height: 1.55; }

.section-heading {
    font-family: Georgia, serif;
    font-size: 1.5rem;
    color: #1F1F1F;
    margin-bottom: 4px;
    margin-top: 0;
}
.section-sub {
    color: #777;
    font-size: 0.88rem;
    margin-bottom: 1.4rem;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">Douro Valley · Portugal</div>
    <h1>VinhaGuard AI</h1>
    <p>
        Parametric climate insurance built for Douro wine producers.
        Objective triggers, automatic payouts, and transparent pricing —
        with no adjusters, no paperwork, and no disputes.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Key stats ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
stats = [
    ("3 + 3",  "Risk Profiles + Demo Places", "Three IVDP profiles plus familiar locations"),
    ("< 72h",  "Payout Speed",          "Triggered by climate data"),
    ("30 +",   "Years of Data",         "Historical Douro climate records"),
    ("AI",     "Risk Modelling",        "Logistic Regression + Random Forest"),
]
for col, (num, lbl, cap) in zip([c1, c2, c3, c4], stats):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="num">{num}</div>
            <div class="lbl">{lbl}</div>
            <div class="cap">{cap}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Why VinhaGuard ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<p class="section-heading">Why VinhaGuard?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Small Douro producers have no affordable, trustworthy way to insure harvests against extreme weather. We change that.</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-item">
            <strong>Objective Triggers</strong>
            <span>Climate thresholds replace inspector visits. No disputes, no subjectivity.</span>
        </div>
        <div class="feature-item">
            <strong>Automatic Payouts</strong>
            <span>Payment begins within 72 hours of trigger confirmation. No claims forms.</span>
        </div>
        <div class="feature-item">
            <strong>Transparent Pricing</strong>
            <span>Formula-based premiums derived from 30 years of regional climate records.</span>
        </div>
        <div class="feature-item">
            <strong>Full Disclosure</strong>
            <span>Basis risk explained upfront. No hidden terms, no fine print.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="region-card">
        <div class="title">Risk profiles and demo locations</div>
        <div class="region-pill">Baixo Corgo — Maritime influence</div>
        <div class="region-pill">Cima Corgo — Historically challenging</div>
        <div class="region-pill">Douro Superior — Hottest and driest</div>
        <div class="region-pill">Pinhão — Premium wine country</div>
        <div class="region-pill">Régua — River valley terraces</div>
        <div class="region-pill">Vila Nova de Foz Côa — Eastern frontier</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown('<p class="section-heading">How It Works</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Four steps from vineyard data to automatic payout.</p>', unsafe_allow_html=True)

steps = [
    ("01", "Enter Details",      "Sub-region, vineyard area, crop value, and your preferred risk coverage type."),
    ("02", "Get a Quote",         "AI risk model analyzes 30+ years of Douro climate data and returns a tailored premium."),
    ("03", "Activate Coverage",   "Select your trigger threshold and confirm your annual premium to start coverage."),
    ("04", "Automatic Payout",    "Trigger fires — payment within 72 hours. No claims. No friction. No delays."),
]
cols = st.columns(4)
for col, (num, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
        <div class="step-box">
            <div class="step-num">Step {num}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#bbb;font-size:0.75rem;">VinhaGuard AI — Academic prototype · Nova SBE Advanced Machine Learning · Not a licensed insurance product</p>', unsafe_allow_html=True)
