from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.ingestion.loaders import iter_supported_files, load_file, SUPPORTED_EXTENSIONS
from app.ingestion.chunking import make_chunks
from app.rag.vector_store import FaissStore
from app.rag.models import QueryRequest, QueryResponse, SaveAnswerRequest
from app.rag.pipeline import answer_query
from app.rag.memory import save_qa_to_disk, rebuild_memory_index, list_memory_items
from dotenv import load_dotenv

load_dotenv()


settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "ollama_model": settings.ollama_model,
        "embedding_model": settings.embedding_model,
    }


@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        return {"success": False, "message": f"Unsupported file type: {suffix}"}

    destination = settings.documents_dir / file.filename

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "filename": file.filename,
        "path": str(destination),
    }


@app.post("/ingest/documents")
def ingest_documents():
    all_chunks = []
    files = list(iter_supported_files(settings.documents_dir))

    for file_path in files:
        text_parts = load_file(file_path)
        chunks = make_chunks(file_path, text_parts)
        all_chunks.extend(chunks)

    store = FaissStore("documents", settings.vector_path)
    store.rebuild(all_chunks)

    return {
        "success": True,
        "files_indexed": len(files),
        "chunks_indexed": len(all_chunks),
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    return answer_query(
        query=request.query,
        use_memory=request.use_memory,
        use_documents=request.use_documents,
    )


@app.post("/memory/save")
def save_answer(request: SaveAnswerRequest):
    item = save_qa_to_disk(request)
    total = rebuild_memory_index()

    return {
        "success": True,
        "saved": item,
        "memory_items_indexed": total,
    }


@app.post("/memory/rebuild")
def rebuild_memory():
    total = rebuild_memory_index()

    return {
        "success": True,
        "memory_items_indexed": total,
    }


@app.get("/memory/list")
def list_memory():
    return {
        "items": list_memory_items()
    }