from langchain_groq import ChatGroq
import streamlit as st


@st.cache_resource
def load_model():

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.2
    )
