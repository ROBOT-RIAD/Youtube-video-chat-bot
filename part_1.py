from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    # max_tokens=None,
    # reasoning_format="parsed",
    # timeout=None,
    # max_retries=2,
)


#Indexing

# Step 1a
video_id = "LzmiunoPXOw" # only the ID, not full URL
try:
    # Create API instance
    ytt_api = YouTubeTranscriptApi()

    # Fetch transcript
    transcript = ytt_api.fetch(video_id, languages=["en"])

    # Convert transcript to plain text
    transcript_text = " ".join(
        snippet.text for snippet in transcript.snippets
    )
except TranscriptsDisabled:
    print("No captions available for this video.")


# print(transcript_text)

# Step 1b 

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript_text])

# print(len(chunks))

# print(chunks[0])

# Step 1c & 1d 

vector_store = FAISS.from_documents(chunks, embeddings)

# print(vector_store.index_to_docstore_id)
doc_id = vector_store.index_to_docstore_id[2]

# print(doc_id)
document = vector_store.get_by_ids([doc_id])
# print(document)

# Retrieval

# Step 2
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# print(retriever)

# print(retriever.invoke('What is Polite'))

# Augmentation
# Step 3

prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables = ['context', 'question']
)

# question          = "What is Stop Complaining"
# retrieved_docs    = retriever.invoke(question)


# context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)


# final_prompt = prompt.invoke({"context": context_text, "question": question})

# print(final_prompt)

# Generation

# Step 4 

def format_docs(retrieved_docs):
  context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
  return context_text


parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough()
})

# parallel_chain.invoke("What is Stop Complaining")

parser = StrOutputParser()

main_chain = parallel_chain | prompt | model | parser

answer = main_chain.invoke("What is Stop Complaining")
print(answer)





