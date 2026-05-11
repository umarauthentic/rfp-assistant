from datetime import datetime, timezone
import hashlib
import json

from app.config import get_settings
from app.rag.models import Chunk, SaveAnswerRequest
from app.rag.vector_store import FaissStore


def save_qa_to_disk(request: SaveAnswerRequest) -> dict:
    settings = get_settings()
    settings.qa_memory_dir.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat()
    raw_id = f"{request.question}:{request.answer}:{created_at}"
    qa_id = hashlib.sha1(raw_id.encode("utf-8")).hexdigest()

    item = {
        "id": qa_id,
        "question": request.question,
        "answer": request.answer,
        "tags": request.tags,
        "approved": request.approved,
        "source_docs": request.source_docs,
        "created_at": created_at,
    }

    path = settings.qa_memory_dir / f"{qa_id}.json"
    path.write_text(
        json.dumps(item, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return item


def list_memory_items() -> list[dict]:
    settings = get_settings()
    settings.qa_memory_dir.mkdir(parents=True, exist_ok=True)

    items = []

    for path in settings.qa_memory_dir.glob("*.json"):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
            if "question" in item and "answer" in item:
                items.append(item)
        except Exception:
            continue

    return sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)


def load_qa_chunks() -> list[Chunk]:
    chunks = []

    for item in list_memory_items():
        text = f"Question: {item.get('question', '')}\nAnswer: {item.get('answer', '')}"

        chunks.append(
            Chunk(
                id=item.get("id", ""),
                text=text,
                metadata={
                    "type": "qa_memory",
                    "question": item.get("question", ""),
                    "answer": item.get("answer", ""),
                    "tags": item.get("tags", []),
                    "approved": item.get("approved", True),
                    "source_docs": item.get("source_docs", []),
                    "created_at": item.get("created_at", ""),
                },
            )
        )

    return chunks


def rebuild_memory_index() -> int:
    settings = get_settings()
    chunks = load_qa_chunks()

    store = FaissStore("qa_memory", settings.vector_path)
    store.rebuild(chunks)

    return len(chunks)