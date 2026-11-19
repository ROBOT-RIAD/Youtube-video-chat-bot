import streamlit as st

from dotenv import load_dotenv

from services.llm import load_model
from services.embeddings import load_embeddings

from ui.sidebar import render_sidebar
from ui.video import render_video
from ui.chat import render_chat


# Load Environment Variables
load_dotenv()


# Page Configuration
st.set_page_config(
    page_title="YouTube AI Chatbot",
    page_icon="🎥",
    layout="wide"
)


# Initialize Session State
def initialize_session_state():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "video_id" not in st.session_state:
        st.session_state.video_id = None

    if "main_chain" not in st.session_state:
        st.session_state.main_chain = None

    if "video_input" not in st.session_state:
        st.session_state.video_input = ""


# Initialize App
initialize_session_state()


# Load AI Models
embeddings = load_embeddings()
model = load_model()


# Sidebar
render_sidebar(
    embeddings,
    model
)


# Main UI
st.title("🎥 YouTube Video AI Chatbot")

st.caption(
    "Ask anything about your YouTube video."
)


if not st.session_state.main_chain:

    st.info(
        "👈 First, enter a YouTube Video ID or URL "
        "from the sidebar and click Process Video."
    )

    st.stop()


# Video Section
render_video(
    st.session_state.video_id
)

st.divider()


# Chat Section
render_chat()









