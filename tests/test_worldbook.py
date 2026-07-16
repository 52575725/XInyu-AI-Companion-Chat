import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import server
from worldbook import WorldbookMemoryStore, create_namespace, normalize_memory_update, normalize_namespace


def memory(content, *, keywords=None, importance=60, replace_keywords=None, action="upsert"):
    return {
        "action": action,
        "content": content,
        "type": "用户资料",
        "keywords": keywords or [],
        "importance": importance,
        "replace_keywords": replace_keywords or [],
    }


class WorldbookMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.store = WorldbookMemoryStore(Path(self.tempdir.name) / "worldbook.sqlite3")
        self.namespace = create_namespace()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_namespace_is_random_normalized_and_validated(self):
        generated = create_namespace()

        self.assertEqual(len(generated), 32)
        self.assertEqual(normalize_namespace(generated), generated)
        self.assertEqual(normalize_namespace("not-a-memory-id"), "")

    def test_memories_are_isolated_between_browsers(self):
        other = create_namespace()
        self.store.apply_updates(self.namespace, [memory("用户住在广州")])
        self.store.apply_updates(other, [memory("用户住在成都")])

        self.assertEqual(self.store.list_contents(self.namespace), ["用户住在广州"])
        self.assertEqual(self.store.list_contents(other), ["用户住在成都"])

    def test_legacy_string_memory_is_imported_and_near_duplicate_is_merged(self):
        self.store.import_legacy(self.namespace, ["用户喜欢旧电影"])
        self.store.apply_updates(self.namespace, [memory("用户很喜欢旧电影", importance=80)])

        stored = self.store.list_contents(self.namespace)

        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0], "用户很喜欢旧电影")

    def test_correction_replaces_old_topic_memory(self):
        self.store.apply_updates(
            self.namespace,
            [memory("用户在广州工作", keywords=["工作城市", "广州"])],
        )

        stored = self.store.apply_updates(
            self.namespace,
            [memory("用户现在在深圳工作", keywords=["工作城市", "深圳"], replace_keywords=["工作城市"])],
        )

        self.assertEqual(stored, ["用户现在在深圳工作"])

    def test_forget_removes_matching_memory_only(self):
        self.store.apply_updates(
            self.namespace,
            [
                memory("用户喜欢旧电影", keywords=["电影偏好"]),
                memory("用户住在广州", keywords=["居住城市"]),
            ],
        )

        stored = self.store.apply_updates(
            self.namespace,
            [memory("", action="forget", keywords=["电影偏好"])],
        )

        self.assertEqual(stored, ["用户住在广州"])

    def test_search_prefers_relevant_memory(self):
        self.store.apply_updates(
            self.namespace,
            [
                memory("用户喜欢旧电影", keywords=["电影", "旧电影"]),
                memory("用户不喜欢香菜", keywords=["食物", "香菜"]),
            ],
        )

        results = self.store.search(self.namespace, "周末想找一部电影看", limit=1)

        self.assertEqual(results, ["用户喜欢旧电影"])

    def test_search_does_not_inject_unrelated_memory(self):
        self.store.apply_updates(
            self.namespace,
            [memory("用户不喜欢香菜", keywords=["食物", "香菜"])],
        )

        results = self.store.search(self.namespace, "最近工作有点忙", limit=8)

        self.assertEqual(results, [])

    def test_structured_update_is_clamped(self):
        update = normalize_memory_update(memory("用户喜欢夜跑", importance=999))

        self.assertEqual(update["importance"], 100)
        self.assertEqual(update["action"], "upsert")

    def test_server_prepares_retrieved_context_and_migrates_browser_memory(self):
        data = {
            "memory_id": self.namespace,
            "latest_message": "今晚看电影吗",
            "memories": ["用户喜欢旧电影"],
            "messages": [],
        }

        with patch("server.WORLD_BOOK", self.store):
            enriched, namespace = server.prepare_memory_context(data)

        self.assertEqual(namespace, self.namespace)
        self.assertEqual(enriched["retrieved_memories"], ["用户喜欢旧电影"])


if __name__ == "__main__":
    unittest.main()
