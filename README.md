# RFP RAG Assistant

A local-first RAG assistant for historical RFP questions and answers.

## What it does

- Ingests `.docx`, `.pptx`, `.xlsx`, `.txt`, and `.md` files.
- Creates local embeddings using Sentence Transformers.
- Stores vector indexes locally using FAISS.
- Uses Ollama locally for answer generation.
- Maintains a historical Q&A memory so approved answers can be reused.
- Exposes a FastAPI backend with Swagger UI.

## Main endpoints

- `GET /health`
- `POST /ingest/documents`
- `POST /query`
- `POST /memory/save`
- `GET /memory/list`
- `POST /upload`

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000/docs

