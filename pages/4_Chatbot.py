import streamlit as st

st.set_page_config(page_title="Chatbot – VinhaGuard", page_icon="🍷", layout="wide")

DISCLAIMER = (
    "_Este chatbot fornece apenas informações gerais. "
    "Consulte um consultor de seguros para aconselhamento vinculativo._"
)

FAQ: dict[str, str] = {
    "o que e seguro parametrico": (
        "Um seguro paramétrico paga automaticamente quando um indicador climático objetivo "
        "— como dias acima de 38°C ou geadas — ultrapassa um limiar pré-acordado. "
        "Não é necessário perito ou inspeção à exploração."
    ),
    "quando recebo o pagamento": (
        "O pagamento é acionado automaticamente quando os dados climáticos oficiais confirmam "
        "que o gatilho foi ativado. O processamento demora normalmente menos de 72 horas."
    ),
    "o que e risco de base": (
        "O risco de base ocorre quando o gatilho é ativado mas a sua vinha não sofreu perdas reais, "
        "ou quando sofreu perdas mas o gatilho não foi ativado. "
        "A VinhaGuard minimiza este risco calibrando os gatilhos com dados históricos de 30+ anos."
    ),
    "como e calculado o premio": (
        "O prémio é calculado com base na probabilidade de risco estimada pelo nosso modelo de IA, "
        "no valor segurado, nas perdas históricas quando o gatilho dispara, e numa margem de risco "
        "e custos administrativos. Consulte a página 'Pricing Explainer' para detalhes."
    ),
    "posso cancelar": (
        "Sim, pode cancelar a apólice a qualquer momento. Consulte as condições gerais da apólice "
        "para detalhes sobre reembolsos proporcionais."
    ),
    "quais sao as sub regioes cobertas": (
        "A VinhaGuard cobre seis sub-regiões do Douro: Baixo Corgo, Cima Corgo, Douro Superior, "
        "Pinhão, Régua e Vila Nova de Foz Côa."
    ),
    "o que e um gatilho": (
        "O gatilho é a condição climática objetiva que, quando atingida, ativa o pagamento automático. "
        "Por exemplo: 14 dias consecutivos acima de 38°C durante a véraison, ou 3 dias com geada "
        "abaixo de -2°C durante a floração."
    ),
    "como funciona": (
        "Seleciona a sua sub-região, área da vinha e valor segurado. O nosso modelo de IA estima "
        "a probabilidade de risco climático e calcula o prémio. Se o gatilho disparar durante a época, "
        "o pagamento é processado automaticamente — sem papelada."
    ),
}


def faq_lookup(user_input: str) -> str | None:
    normalized = (
        user_input.lower()
        .replace("é", "e").replace("ê", "e").replace("à", "a").replace("ã", "a")
        .replace("ç", "c").replace("ó", "o").replace("ô", "o").replace("ú", "u")
        .replace("í", "i").replace("á", "a").replace("â", "a")
        .replace("?", "").replace("!", "").replace(",", "").strip()
    )
    for key, answer in FAQ.items():
        if any(word in normalized for word in key.split()):
            return answer
    return None


def chatbot_respond(user_input: str) -> str:
    answer = faq_lookup(user_input)
    if answer:
        return answer
    return (
        "Desculpe, não tenho uma resposta para essa pergunta no momento. "
        "Por favor contacte a nossa equipa para mais informações sobre a VinhaGuard."
    )


st.title("Assistente VinhaGuard")
st.markdown(DISCLAIMER)
st.markdown("---")

st.markdown("""
**Perguntas frequentes / Suggested questions:**
- O que é um seguro paramétrico?
- Quando recebo o pagamento?
- O que é o risco de base?
- Como é calculado o prémio?
- Posso cancelar?
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Faça a sua pergunta em Português..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    reply = chatbot_respond(prompt)
    full_reply = f"{reply}\n\n{DISCLAIMER}"
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
    st.chat_message("assistant").write(full_reply)
