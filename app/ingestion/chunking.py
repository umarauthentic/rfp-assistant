from app.rag.models import Chunk
import hashlib
from pathlib import Path


def _chunk_text(text: str, max_chars: int = 1600, overlap: int = 200) -> list[str]:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def make_chunks(file_path: Path, text_parts: list[str]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for part_idx, part in enumerate(text_parts):
        for chunk_idx, chunk_text in enumerate(_chunk_text(part)):
            raw_id = f"{file_path.name}:{part_idx}:{chunk_idx}:{chunk_text[:80]}"
            chunk_id = hashlib.sha1(raw_id.encode("utf-8")).hexdigest()
            chunks.append(
                Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    metadata={
                        "source": file_path.name,
                        "path": str(file_path),
                        "part_index": part_idx,
                        "chunk_index": chunk_idx,
                        "file_type": file_path.suffix.lower(),
                    },
                )
            )
    return chunks
