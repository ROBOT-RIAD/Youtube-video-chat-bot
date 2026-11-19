
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


def create_vector_store(transcript_text, embeddings):

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
