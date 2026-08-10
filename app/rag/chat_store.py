from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ChatStore:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _path(self, conversation_id: str) -> Path:
        if not conversation_id or any(character not in "0123456789abcdef-" for character in conversation_id.lower()):
            raise ValueError("Invalid conversation id")
        return self.base_dir / f"{conversation_id}.json"

    def _read(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, conversation: dict) -> None:
        temporary_path = path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(conversation, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_path.replace(path)

    def create(self, title: str = "New chat") -> dict:
        now = self._now()
        conversation = {
            "id": uuid4().hex,
            "title": title.strip()[:100] or "New chat",
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
        with self._lock:
            self._write(self._path(conversation["id"]), conversation)
        return conversation

    def get(self, conversation_id: str) -> dict | None:
        try:
            path = self._path(conversation_id)
        except ValueError:
            return None
        with self._lock:
            return self._read(path) if path.exists() else None

    def list(self) -> list[dict]:
        conversations = []
        with self._lock:
            for path in self.base_dir.glob("*.json"):
                try:
                    conversation = self._read(path)
                except (OSError, ValueError, json.JSONDecodeError):
                    continue
                conversations.append({
                    "id": conversation.get("id", path.stem),
                    "title": conversation.get("title", "New chat"),
                    "created_at": conversation.get("created_at"),
                    "updated_at": conversation.get("updated_at"),
                    "message_count": len(conversation.get("messages", [])),
                })
        return sorted(conversations, key=lambda item: item.get("updated_at") or "", reverse=True)

    def add_exchange(
        self,
        conversation_id: str,
        question: str,
        answer: str,
        sources: list[dict],
        in_scope: bool,
    ) -> dict | None:
        with self._lock:
            conversation = self.get(conversation_id)
            if conversation is None:
                return None

            now = self._now()
            conversation["messages"].extend([
                {
                    "id": uuid4().hex,
                    "role": "user",
                    "content": question,
                    "created_at": now,
                },
                {
                    "id": uuid4().hex,
                    "role": "assistant",
                    "content": answer,
                    "created_at": self._now(),
                    "sources": sources,
                    "in_scope": in_scope,
                },
            ])
            if conversation.get("title") == "New chat":
                conversation["title"] = question.strip()[:72]
            conversation["updated_at"] = self._now()
            self._write(self._path(conversation_id), conversation)
            return conversation

    def delete(self, conversation_id: str) -> bool:
        try:
            path = self._path(conversation_id)
        except ValueError:
            return False
        with self._lock:
            if not path.exists():
                return False
            path.unlink()
            return True
