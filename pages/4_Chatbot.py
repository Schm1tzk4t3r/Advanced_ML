import streamlit as st

st.set_page_config(page_title="Chatbot - VinhaGuard", page_icon="🍷", layout="wide")

DISCLAIMER = (
    "_This chatbot provides general information only. "
    "Consult an insurance advisor for binding advice._"
)

FAQ: dict[str, str] = {
    "what is parametric insurance": (
        "Parametric insurance pays automatically when an objective climate indicator "
        "— such as days above 38°C or frost events — crosses a pre-agreed threshold. "
        "No adjuster or farm inspection is needed."
    ),
    "when do i receive payment": (
        "Payment is triggered automatically when official climate data confirms "
        "that the trigger condition has been met. Processing typically takes less than 72 hours."
    ),
    "what is basis risk": (
        "Basis risk occurs when the trigger fires but your vineyard doesn't suffer real losses, "
        "or when you suffer losses but the trigger doesn't fire. "
        "VinhaGuard minimises basis risk by calibrating triggers using 30+ years of historical data."
    ),
    "how is the premium calculated": (
        "The premium is calculated based on the AI model's estimated risk probability, "
        "your insured value, historical losses when the trigger fires, and margins for risk "
        "and administrative costs. See the 'Pricing Explainer' page for details."
    ),
    "can i cancel": (
        "Yes, you can cancel your policy at any time. "
        "Consult your policy terms for details on prorated refunds."
    ),
    "which douro subregions are covered": (
        "VinhaGuard covers six Douro sub-regions: Baixo Corgo, Cima Corgo, Douro Superior, "
        "Pinhão, Régua, and Vila Nova de Foz Côa."
    ),
    "what is a trigger": (
        "A trigger is the objective climate condition that, when met, activates automatic payment. "
        "For example: 14 consecutive days above 38°C during veraison, or 3 days with frost "
        "below -2°C during flowering."
    ),
    "how does it work": (
        "Select your sub-region, vineyard area, and insured value. Our AI model estimates "
        "climate risk probability and calculates the premium. If the trigger fires during the season, "
        "payment is processed automatically — no paperwork required."
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
        "I don't have an answer to that question at the moment. "
        "Please contact our team for more information about VinhaGuard."
    )


st.title("VinhaGuard Assistant")
st.markdown(DISCLAIMER)
st.markdown("---")

st.markdown("""
**Frequently Asked Questions:**
- What is parametric insurance?
- When do I receive payment?
- What is basis risk?
- How is the premium calculated?
- Can I cancel?
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    reply = chatbot_respond(prompt)
    full_reply = f"{reply}\n\n{DISCLAIMER}"
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.chat_message("assistant").write(full_reply)
