import streamlit as st

DISCLAIMER = (
    "⚠️ This chatbot provides general information only. "
    "Consult a licensed insurance advisor for binding advice."
)

FAQ: dict[str, str] = {
    "what is parametric insurance": (
        "Parametric insurance pays **automatically** when an objective climate indicator "
        "— such as days above 38°C or frost events — crosses a **pre-agreed threshold**. "
        "No adjuster visits. No paperwork. Just climate data triggers payment.\n\n"
        "**Key difference:** Traditional insurance asks 'Did you lose money?' Parametric asks "
        "'Did climate conditions hit the trigger?' Much simpler."
    ),
    "when do i receive payment": (
        "Payment timing:\n"
        "1. **Trigger fires** — climate data confirms threshold met\n"
        "2. **72 hours** — payment processing begins\n"
        "3. **Week 1** — funds deposited to your account\n\n"
        "No waiting for inspectors, no claim forms, no negotiation. Automatic."
    ),
    "what is basis risk": (
        "Basis risk = the gap between when the **trigger fires** and when you **actually suffer losses**.\n\n"
        "**Two scenarios:**\n"
        "- ✅ Trigger fires → no loss → you keep payout (good for you)\n"
        "- ❌ Real loss → trigger doesn't fire → no payout (bad for you)\n\n"
        "VinhaGuard **discloses this risk openly** and works hard to calibrate triggers so these "
        "mismatches are rare. We can't eliminate it, but transparency is our commitment."
    ),
    "how is the premium calculated": (
        "Three steps:\n"
        "1. **Risk assessment** — AI model analyzes 30+ years of climate data for your region\n"
        "2. **Historical trigger rate** — how often does the trigger fire?\n"
        "3. **Load, admin cost, and margin** — add the uncertainty buffer, fixed platform cost, and margin\n\n"
        "**Formula:** Premium = (Expected Payout + Risk Loading + Admin Cost) x (1 + Margin)\n\n"
        "See the **Pricing Explainer** page for an interactive calculator and full breakdown."
    ),
    "can i cancel": (
        "Yes, **you can cancel anytime**. \n\n"
        "- **Mid-season?** Prorated refund (you pay only for days insured)\n"
        "- **Next season?** Cancel and buy a fresh policy elsewhere\n\n"
        "No penalties, no lock-in. We only keep revenue for coverage you actually use."
    ),
    "which douro subregions are covered": (
        "The ML model currently uses **3 canonical IVDP risk profiles**:\n"
        "- **Baixo Corgo**\n"
        "- **Cima Corgo**\n"
        "- **Douro Superior**\n\n"
        "The demo also shows familiar place labels: **Pinhao**, **Regua**, and "
        "**Vila Nova de Foz Coa**. These are transparently mapped to the closest "
        "canonical IVDP profile for pricing."
    ),
    "what is a trigger": (
        "A trigger is the **objective climate condition** that activates automatic payment.\n\n"
        "**Examples:**\n"
        "- Heat: at least 5 days above 38°C during the growing season\n"
        "- Frost: 3 days below -2°C during budbreak/flowering (spring)\n"
        "- Combined: any of the above\n\n"
        "Triggers are **specific, measurable, and checked automatically** using official weather data. "
        "No guessing, no debate — climate data is the judge."
    ),
    "how does it work": (
        "**4-step process:**\n\n"
        "1️⃣ **Enter your details** (location, vineyard size, crop value)\n"
        "2️⃣ **Get a quote** (AI calculates risk & premium in seconds)\n"
        "3️⃣ **Buy a policy** (select trigger threshold, activate coverage)\n"
        "4️⃣ **Wait** — if trigger fires, payment is automatic within 72 hours\n\n"
        "Start with **Risk Assessment** page to calculate your quote."
    ),
    "is this a real insurance product": (
        "**Not yet.** VinhaGuard is a **prototype and proof-of-concept** built for the "
        "Nova SBE Advanced ML course.\n\n"
        "To become a real product, we would need:\n"
        "- Insurance licensing (Portugal + EU)\n"
        "- Reinsurance partnerships\n"
        "- Regulatory approval\n"
        "- Capital to cover claim payouts\n\n"
        "This demo shows **what's possible** — the technology and pricing logic are sound."
    ),
}


def faq_lookup(user_input: str) -> str | None:
    normalized = user_input.lower().replace("?", "").replace("!", "").strip()
    for key, answer in FAQ.items():
        if any(word in normalized for word in key.split()):
            return answer
    return None


def chatbot_respond(user_input: str) -> str:
    answer = faq_lookup(user_input)
    if answer:
        return answer
    return (
        "I don't have a specific answer to that question. "
        "Try asking about: insurance, premiums, regions, triggers, basis risk, or payment timing. "
        "Or contact our team for details."
    )


# Page layout
st.title("AI Assistant")
st.markdown(DISCLAIMER)
st.markdown("---")

# FAQ suggestions with better visual hierarchy
st.markdown("### Common Questions")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Product Basics:**
    - What is parametric insurance?
    - How does it work?
    - How is the premium calculated?
    """)

with col2:
    st.markdown("""
    **Coverage & Claims:**
    - When do I receive payment?
    - What is basis risk?
    - Can I cancel?
    """)

st.markdown("---")

# Chat interface
st.markdown("### Ask a Question")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# Chat input and response
if prompt := st.chat_input("Ask your question..."):
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)

    # Get response
    reply = chatbot_respond(prompt)
    full_reply = f"{reply}\n\n---\n\n{DISCLAIMER}"
    st.session_state.messages.append({"role": "assistant", "content": full_reply})

    # Display bot response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(full_reply)

st.markdown("---")
st.info("💡 This is a prototype chatbot with FAQ-based responses. All information is illustrative.", icon="ℹ️")
