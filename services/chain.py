
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)

from langchain_core.output_parsers import StrOutputParser

from config.settings import RAG_PROMPT
from services.retriever import create_retriever


def create_chain(vector_store, model):

    retriever = create_retriever(
        vector_store,
        model
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
        | RAG_PROMPT
        | model
        | parser
    )

    main_chain.get_graph().print_ascii()

    return main_chain
