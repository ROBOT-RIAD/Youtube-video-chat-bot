
import streamlit as st

from config.settings import LANGUAGE_OPTIONS
from utils.youtube import extract_video_id

from services.transcript import fetch_transcript
from services.vector_store import create_vector_store
from services.chain import create_chain


def render_sidebar(embeddings, model):

    with st.sidebar:

        st.title("🎥 YouTube AI")
        st.caption("Chat with any YouTube video")

        st.divider()

        st.subheader("Add New Video")

        video_input = st.text_input(
            "YouTube Video ID or URL",
            placeholder="Enter YouTube video ID..."
        )

        language_name = st.selectbox(
            "Select Video Transcript Language",
            options=list(LANGUAGE_OPTIONS.keys())
        )

        if st.button(
            "Process Video",
            use_container_width=True
        ):

            if not video_input.strip():

                st.warning("Please enter a YouTube Video ID.")

            else:

                try:

                    with st.spinner("Processing YouTube video..."):

                        new_video_id = extract_video_id(
                            video_input
                        )

                        language = LANGUAGE_OPTIONS[language_name]

                        transcript_text = fetch_transcript(
                            new_video_id,
                            language
                        )

                        vector_store = create_vector_store(
                            transcript_text,
                            embeddings
                        )

                        new_chain = create_chain(
                            vector_store,
                            model
                        )

                        st.session_state.video_id = new_video_id

                        st.session_state.main_chain = new_chain

                        st.session_state.messages = []

                        st.session_state.video_input = video_input

                    st.success("Video processed successfully!")

                    st.rerun()

                except Exception as e:

                    st.error(f"Error: {str(e)}")

        st.divider()

        if st.session_state.video_id:

            st.success("Video Loaded")

            st.write(
                f"Video ID: `{st.session_state.video_id}`"
            )

            if st.button(
                "🗑️ New Chat",
                use_container_width=True
            ):

                st.session_state.messages = []

                st.rerun()

            if st.button(
                "🔄 Reset Video",
                use_container_width=True
            ):

                st.session_state.video_id = None

                st.session_state.main_chain = None

                st.session_state.messages = []

                st.session_state.video_input = ""

                st.rerun()
