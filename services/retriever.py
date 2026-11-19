
from langchain_classic.retrievers import MultiQueryRetriever

from config.settings import MULTI_QUERY_PROMPT


def create_retriever(vector_store, model):

    base_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=model,
        prompt=MULTI_QUERY_PROMPT
    )

    return retriever
