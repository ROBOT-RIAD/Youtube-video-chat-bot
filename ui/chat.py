
import streamlit as st


def render_chat():

    # Chat History
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # User Input
    user_question = st.chat_input(
        "Ask something about this video..."
    )

    if user_question:

        st.session_state.messages.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):

            st.markdown(user_question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    answer = st.session_state.main_chain.invoke(
                        user_question
                    )

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:

                    st.error(
                        f"Something went wrong: {str(e)}"
                    )
