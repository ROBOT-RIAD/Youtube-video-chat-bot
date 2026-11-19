
import streamlit as st


def render_video(video_id):

    video_url = (
        f"https://www.youtube.com/watch?v={video_id}"
    )

    st.video(video_url)
