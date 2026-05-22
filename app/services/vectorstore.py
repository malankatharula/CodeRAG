from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.core.config import settings


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


def build_vectorstore(files: list[dict], collection_name: str) -> Chroma:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
    )

    docs = []
    metadatas = []

    for file in files:
        chunks = splitter.split_text(file["content"])
        for chunk in chunks:
            docs.append(chunk)
            metadatas.append({"source": file["path"]})

    print(f"Total chunks: {len(docs)}")

    embeddings = get_embeddings()
    vectorstore = Chroma.from_texts(
        texts=docs,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=collection_name,
        persist_directory=settings.CHROMA_PATH
    )
    return vectorstore


def load_vectorstore(collection_name: str) -> Chroma:
    embeddings = get_embeddings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH
    )