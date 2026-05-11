from pathlib import Path
import json
import faiss
import numpy as np
from app.rag.models import Chunk, SearchResult
from app.rag.embeddings import embed_texts


class FaissStore:
    def __init__(self, name: str, base_dir: Path):
        self.name = name
        self.base_dir = base_dir
        self.index_path = base_dir / f"{name}.faiss"
        self.meta_path = base_dir / f"{name}.json"
        self.index = None
        self.chunks: list[Chunk] = []
        self.load()

    def load(self) -> None:
        if self.index_path.exists() and self.meta_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            raw = json.loads(self.meta_path.read_text(encoding="utf-8"))
            self.chunks = [Chunk(**item) for item in raw]
        else:
            self.index = None
            self.chunks = []

    def save(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_text(
            json.dumps([c.model_dump() for c in self.chunks], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def rebuild(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        if not chunks:
            self.index = None
            self.save()
            return
        vectors = embed_texts([c.text for c in chunks])
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        self.index = index
        self.save()

    def add(self, chunks: list[Chunk]) -> None:
        all_chunks = self.chunks + chunks
        self.rebuild(all_chunks)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if self.index is None or not self.chunks:
            return []
        vector = embed_texts([query])
        scores, indices = self.index.search(vector, top_k)
        results: list[SearchResult] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx]
            results.append(
                SearchResult(
                    id=chunk.id,
                    text=chunk.text,
                    score=float(score),
                    metadata=chunk.metadata,
                )
            )
        return results
