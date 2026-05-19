import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.repo_loader import load_repo
from app.services.vectorstore import build_vectorstore
from app.services.rag import answer_question
import chromadb
from app.core.config import settings

router = APIRouter()

def repo_url_to_collection(repo_url: str) -> str:
    """Turn a repo URL into a valid ChromaDB collection name"""
    name = re.sub(r"https?://github\.com/", "", repo_url)
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return name[:60]


class IngestRequest(BaseModel):
    repo_url: str

class QuestionRequest(BaseModel):
    repo_url: str
    question: str


@router.post("/ingest")
def ingest_repo(req: IngestRequest):
    try:
        collection_name = repo_url_to_collection(req.repo_url)
        files = load_repo(req.repo_url)
        if not files:
            raise HTTPException(status_code=400, detail="No supported files found in repo.")
        build_vectorstore(files, collection_name)
        return {
            "status": "success",
            "collection": collection_name,
            "files_indexed": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
def ask_question(req: QuestionRequest):
    try:
        collection_name = repo_url_to_collection(req.repo_url)
        result = answer_question(req.question, collection_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
def list_collections():
    client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
    collections = client.list_collections()
    return {"collections": [c.name for c in collections]}


@router.get("/health")
def health():
    return {"status": "ok"}