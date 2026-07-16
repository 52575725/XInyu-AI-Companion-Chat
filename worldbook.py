"""Persistent, per-conversation worldbook memory storage."""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


MEMORY_TYPES = {"用户资料", "偏好边界", "关系事件", "约定事项", "共同经历"}
NAMESPACE_PATTERN = re.compile(r"^[a-f0-9]{32}$")


def normalize_namespace(value: Any) -> str:
    raw = str(value or "").strip().lower().replace("-", "")
    return raw if NAMESPACE_PATTERN.fullmatch(raw) else ""


def create_namespace() -> str:
    return uuid.uuid4().hex


def _clean_text(value: Any, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _normalized_text(value: Any) -> str:
    return re.sub(r"[^0-9a-z\u3400-\u9fff]+", "", _clean_text(value).casefold())


def _clean_keywords(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value[:12]:
        clean = _clean_text(item, 24)
        if clean and clean not in result:
            result.append(clean)
    return result


def _search_units(value: Any) -> set[str]:
    text = _clean_text(value, 4000).casefold()
    units = set(re.findall(r"[a-z0-9]{2,}|[\u3400-\u9fff]{2,6}", text))
    chinese = "".join(re.findall(r"[\u3400-\u9fff]", text))
    units.update(chinese[index:index + 2] for index in range(max(0, len(chinese) - 1)))
    return {unit for unit in units if unit}


def normalize_memory_update(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str):
        content = _clean_text(value)
        if not content:
            return None
        return {
            "action": "upsert", "content": content, "type": "用户资料",
            "keywords": [], "importance": 60, "replace_keywords": [],
        }
    if not isinstance(value, dict):
        return None
    action = str(value.get("action", "upsert")).strip().lower()
    if action not in {"upsert", "forget"}:
        action = "upsert"
    content = _clean_text(value.get("content"))
    keywords = _clean_keywords(value.get("keywords"))
    replace_keywords = _clean_keywords(value.get("replace_keywords"))
    if action == "upsert" and not content:
        return None
    if action == "forget" and not keywords and not replace_keywords and not content:
        return None
    memory_type = str(value.get("type", "用户资料")).strip()
    if memory_type not in MEMORY_TYPES:
        memory_type = "用户资料"
    try:
        importance = int(value.get("importance", 60) or 60)
    except (TypeError, ValueError):
        importance = 60
    return {
        "action": action,
        "content": content,
        "type": memory_type,
        "keywords": keywords,
        "importance": max(1, min(importance, 100)),
        "replace_keywords": replace_keywords,
    }


class WorldbookMemoryStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    namespace TEXT NOT NULL,
                    content TEXT NOT NULL,
                    normalized_content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    keywords_json TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 60,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    last_used_at INTEGER,
                    use_count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(namespace, normalized_content)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace, importance DESC, updated_at DESC)"
            )

    @staticmethod
    def _row_keywords(row: sqlite3.Row) -> list[str]:
        try:
            value = json.loads(row["keywords_json"])
        except (json.JSONDecodeError, TypeError):
            return []
        return _clean_keywords(value)

    def _delete_matching(self, connection: sqlite3.Connection, namespace: str, terms: list[str]) -> None:
        normalized_terms = {_normalized_text(term) for term in terms if _normalized_text(term)}
        if not normalized_terms:
            return
        rows = connection.execute(
            "SELECT id, content, keywords_json FROM memories WHERE namespace = ?", (namespace,)
        ).fetchall()
        for row in rows:
            haystacks = {_normalized_text(row["content"])}
            haystacks.update(_normalized_text(keyword) for keyword in self._row_keywords(row))
            if any(term in haystack or haystack in term for term in normalized_terms for haystack in haystacks if haystack):
                connection.execute("DELETE FROM memories WHERE id = ?", (row["id"],))

    def apply_updates(self, namespace: str, updates: list[Any]) -> list[str]:
        namespace = normalize_namespace(namespace)
        if not namespace:
            return []
        normalized_updates = [normalize_memory_update(item) for item in updates[:3]]
        now = int(time.time())
        with self._connection() as connection:
            for update in normalized_updates:
                if not update:
                    continue
                delete_terms = update["replace_keywords"][:]
                if update["action"] == "forget":
                    delete_terms.extend(update["keywords"])
                    if update["content"]:
                        delete_terms.append(update["content"])
                    self._delete_matching(connection, namespace, delete_terms)
                    continue
                if delete_terms:
                    self._delete_matching(connection, namespace, delete_terms)

                content = update["content"]
                normalized = _normalized_text(content)
                if not normalized:
                    continue
                existing = connection.execute(
                    "SELECT * FROM memories WHERE namespace = ?", (namespace,)
                ).fetchall()
                duplicate = next(
                    (row for row in existing if row["normalized_content"] == normalized
                     or SequenceMatcher(None, row["normalized_content"], normalized).ratio() >= 0.9),
                    None,
                )
                keywords_json = json.dumps(update["keywords"], ensure_ascii=False)
                if duplicate:
                    connection.execute(
                        """
                        UPDATE memories SET content = ?, normalized_content = ?, memory_type = ?,
                            keywords_json = ?, importance = MAX(importance, ?), updated_at = ? WHERE id = ?
                        """,
                        (content, normalized, update["type"], keywords_json,
                         update["importance"], now, duplicate["id"]),
                    )
                else:
                    connection.execute(
                        """
                        INSERT INTO memories (
                            namespace, content, normalized_content, memory_type, keywords_json,
                            importance, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (namespace, content, normalized, update["type"], keywords_json,
                         update["importance"], now, now),
                    )
        return self.list_contents(namespace)

    def import_legacy(self, namespace: str, memories: Any) -> None:
        if isinstance(memories, list) and memories:
            self.apply_updates(namespace, memories[:20])

    def list_contents(self, namespace: str, limit: int = 20) -> list[str]:
        namespace = normalize_namespace(namespace)
        if not namespace:
            return []
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT content FROM memories WHERE namespace = ? ORDER BY importance DESC, updated_at DESC LIMIT ?",
                (namespace, max(1, min(limit, 50))),
            ).fetchall()
        return [str(row["content"]) for row in rows]

    def search(self, namespace: str, query: str, limit: int = 8) -> list[str]:
        namespace = normalize_namespace(namespace)
        if not namespace:
            return []
        query_text = _clean_text(query, 8000)
        query_normalized = _normalized_text(query_text)
        query_units = _search_units(query_text)
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM memories WHERE namespace = ? ORDER BY importance DESC, updated_at DESC LIMIT 200",
                (namespace,),
            ).fetchall()
            scored: list[tuple[float, sqlite3.Row]] = []
            for row in rows:
                keywords = self._row_keywords(row)
                content_units = _search_units(str(row["content"]) + " " + " ".join(keywords))
                overlap = len(query_units & content_units)
                direct = sum(1 for keyword in keywords if _normalized_text(keyword) in query_normalized)
                score = overlap * 5 + direct * 20 + int(row["importance"]) / 20
                if row["normalized_content"] in query_normalized or query_normalized in row["normalized_content"]:
                    score += 30
                if score >= 8 or int(row["importance"]) >= 90:
                    scored.append((score, row))
            scored.sort(key=lambda item: (-item[0], -int(item[1]["importance"]), -int(item[1]["updated_at"])))
            selected = scored[:max(1, min(limit, 20))]
            if selected:
                used_ids = [int(row["id"]) for _, row in selected]
                placeholders = ",".join("?" for _ in used_ids)
                connection.execute(
                    f"UPDATE memories SET last_used_at = ?, use_count = use_count + 1 WHERE id IN ({placeholders})",
                    (int(time.time()), *used_ids),
                )
        return [str(row["content"]) for _, row in selected]
