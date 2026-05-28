from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.vectorstore import load_vectorstore
from app.core.config import settings

SYSTEM_PROMPT = """You are an expert code assistant. You answer questions about a codebase using only the provided code context.
Be precise, technical, and reference specific files and functions when relevant.
If the answer is not in the context, say so clearly - do not make things up."""


def answer_question(question: str, collection_name: str) -> dict:
    vectorstore = load_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    docs = retriever.invoke(question)
    context = "\n\n".join([
        f"### File: {d.metadata['source']}\n{d.page_content}"
        for d in docs
    ])

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY,
        temperature=0.1
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
    ]

    response = llm.invoke(messages)

    sources = list({d.metadata["source"] for d in docs})

    return {
        "answer": response.content,
        "sources": sources
    }