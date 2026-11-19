
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st


@st.cache_resource
def load_embeddings():

    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2"
    )
