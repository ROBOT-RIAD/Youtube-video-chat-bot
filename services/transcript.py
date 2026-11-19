
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)


def fetch_transcript(video_id, language):

    ytt_api = YouTubeTranscriptApi()

    transcript = ytt_api.fetch(
        video_id,
        languages=[language]
    )

    transcript_text = " ".join(
        snippet.text
        for snippet in transcript.snippets
    )

    if not transcript_text.strip():
        raise ValueError("Transcript is empty.")

    return transcript_text
