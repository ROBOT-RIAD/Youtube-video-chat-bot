
from urllib.parse import urlparse, parse_qs


def extract_video_id(video_input):

    video_input = video_input.strip()

    parsed_url = urlparse(video_input)

    # youtube.com/watch?v=VIDEO_ID
    if "youtube.com" in parsed_url.netloc:

        if parsed_url.path == "/watch":

            video_id = parse_qs(
                parsed_url.query
            ).get("v", [None])[0]

            if not video_id:
                raise ValueError("Invalid YouTube URL.")

            return video_id

        # youtube.com/embed/VIDEO_ID
        if parsed_url.path.startswith("/embed/"):

            return parsed_url.path.split("/embed/")[1].split("/")[0]

        # youtube.com/shorts/VIDEO_ID
        if parsed_url.path.startswith("/shorts/"):

            return parsed_url.path.split("/shorts/")[1].split("/")[0]

        raise ValueError("Invalid YouTube URL.")

    # youtu.be/VIDEO_ID
    if parsed_url.netloc == "youtu.be":

        video_id = parsed_url.path.strip("/").split("/")[0]

        if not video_id:
            raise ValueError("Invalid YouTube URL.")

        return video_id

    # Direct video ID
    return video_input
