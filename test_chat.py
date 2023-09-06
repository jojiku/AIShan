import streamlit as st
from src.consultants.one_shot_consultant import OneShotConsultant, ConsultantInterface

consultant = OneShotConsultant()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def add_message(role: str, content: str) -> None:
    st.session_state["messages"].append({"role": role, "content": content})

def display_chat(chat: list):
    for msg in chat:
        st.chat_message(msg["role"]).write(msg["content"])

def get_bot_answer(chat: list) -> str:

    global consultant

    response = consultant.get_answer(chat)

    if isinstance(response, str):
        return response
    elif callable(response):
        return response()
    elif isinstance(response, ConsultantInterface):
        consultant = response

        return get_bot_answer(chat)
    else:
        return "Что-то пошло не так"


if __name__ == "__main__":

    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

        if st.button("Отчистить чат"):
            st.session_state["messages"] = []

    st.title("Тестовый бот") 

    if not st.session_state["messages"]:
        add_message(role="assistant", content="Привет, как я могу помочь?")

    display_chat(st.session_state["messages"][-10:])

    if client_text := st.chat_input():
        add_message(role = "user", content = client_text)
        st.chat_message("user").write(client_text)

        msg = get_bot_answer(st.session_state["messages"])

        add_message(role = "assistant", content = msg)
        st.chat_message("assistant").write(msg)