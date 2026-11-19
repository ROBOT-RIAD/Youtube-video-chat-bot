import streamlit as st
from langchain_core.prompts import PromptTemplate


st.set_page_config(
    page_title="YouTube AI Chatbot",
    page_icon="🎥",
    layout="wide"
)


LANGUAGE_OPTIONS = {
    "English": "en",
    "Bangla": "bn",
    "Hindi": "hi",
    "Arabic": "ar",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko",
    "Urdu": "ur",
    "Chinese": "zh"
}


RAG_PROMPT = PromptTemplate(
    template="""
    You are a helpful YouTube video assistant.

    Answer ONLY using the provided transcript context.

    If the answer is not available in the transcript,
    say: "I don't know based on this video."

    Keep your answer clear and easy to understand.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """,
    input_variables=["context", "question"]
)


MULTI_QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""
    You are an expert query rewriter.

    The user may ask questions in:
    - Banglish
    - Bengali
    - English
    - Hindi

    Generate 3 different search queries.

    Rules:
    1. Convert Banglish into proper Bengali.
    2. Generate an English version.
    3. Preserve important names and technical terms.
    4. Keep the original meaning.
    5. Each query must be on a separate line.
    6. Do not answer the question.

    Original question:
    {question}
    """
)
