from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled ,NoTranscriptFound
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
import streamlit as st
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_classic.retrievers import MultiQueryRetriever

load_dotenv()

# Configuration
st.set_page_config(
    page_title="YouTube AI Chatbot",
    page_icon="🎥",
    layout="wide"
)


# Helper Functions
def extract_video_id(video_input):

    video_input = video_input.strip()

    # Handle full YouTube URLs
    if "youtube.com" in video_input:

        from urllib.parse import urlparse, parse_qs

        parsed_url = urlparse(video_input)

        video_id = parse_qs(parsed_url.query).get("v", [None])[0]

        if not video_id:
            raise ValueError("Invalid YouTube URL.")

        return video_id

    elif "youtu.be/" in video_input:

        from urllib.parse import urlparse

        parsed_url = urlparse(video_input)

        return parsed_url.path.strip("/").split("/")[0]

    elif "youtube.com/embed/" in video_input:

        return video_input.split("embed/")[1].split("?")[0]

    # Handle video ID directly
    return video_input



#model
@st.cache_resource
def load_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2"
    )


@st.cache_resource
def load_model():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.2
    )

embeddings = load_embeddings()
model = load_model()


prompt = PromptTemplate(
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

multi_query_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
    You are an expert query rewriter.

    The user may ask questions in:
    - Banglish (Bengali written in English letters)
    - Bengali
    - English
    - Hindi

    Generate 3 different search queries for the given question.

    Rules:
    1. Convert Banglish into proper Bengali.
    2. Generate an English version of the query.
    3. Preserve important names, technical terms and keywords.
    4. Keep the original meaning.
    5. Each query must be on a separate line.
    6. Do not answer the question.

    Original question:
    {question}
    """
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



def create_vector_store(transcript_text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.create_documents(
        [transcript_text]
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    return vector_store


def create_chain(vector_store):

    base_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=model,
        prompt=multi_query_prompt
    )

    def format_docs(retrieved_docs):

        return "\n\n".join(
            doc.page_content
            for doc in retrieved_docs
        )

    parallel_chain = RunnableParallel({

        "context": retriever | RunnableLambda(format_docs),

        "question": RunnablePassthrough()

    })

    parser = StrOutputParser()

    main_chain = (
        parallel_chain
        | prompt
        | model
        | parser
    )

    return main_chain

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "video_id" not in st.session_state:
    st.session_state.video_id = None

if "main_chain" not in st.session_state:
    st.session_state.main_chain = None

if "video_input" not in st.session_state:
    st.session_state.video_input = ""

# Sidebar

with st.sidebar:
    st.title("🎥 YouTube AI")
    st.caption("Chat with any YouTube video")
    st.divider()
    st.subheader("Add New Video")
    video_input = st.text_input(
        "YouTube Video ID or URL",
        placeholder="Enter YouTube video ID..."
    )

    language_options = {
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

    language_name = st.selectbox(
        "Select Video Transcript Language",
        options=list(language_options.keys())
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

                    new_video_id = extract_video_id(video_input)
                    language = language_options[language_name]

                    transcript_text = fetch_transcript(
                        new_video_id,
                        language
                    )

                    vector_store = create_vector_store(
                        transcript_text
                    )

                    new_chain = create_chain(
                        vector_store
                    )

                    # Update current video
                    st.session_state.video_id = new_video_id

                    st.session_state.main_chain = new_chain

                    st.session_state.messages = []

                    st.session_state.video_input = video_input

                st.success("Video processed successfully!")

                st.rerun()

            except TranscriptsDisabled:

                st.error(
                    "Captions are disabled for this video."
                )

            except NoTranscriptFound:

                st.error(
                    "No English transcript found for this video."
                )

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



# # Main UI
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


# =====================================
# Display Video
# =====================================

video_url = (
    f"https://www.youtube.com/watch?v="
    f"{st.session_state.video_id}"
)

st.video(video_url)

st.divider()


# =====================================
# Chat History
# =====================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =====================================
# User Input
# =====================================

user_question = st.chat_input(
    "Ask something about this video..."
)


if user_question:

    # Show user question

    st.session_state.messages.append({

        "role": "user",

        "content": user_question

    })

    with st.chat_message("user"):

        st.markdown(user_question)


    # Generate AI response

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
