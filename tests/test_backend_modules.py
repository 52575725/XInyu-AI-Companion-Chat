import unittest

import server
from backend_config import APP_VERSION
from model_client import endpoint_url, extract_content
from request_payload import sanitize_chat_payload


class BackendModuleBoundaryTests(unittest.TestCase):
    def test_server_remains_a_thin_compatible_entry_point(self):
        self.assertTrue(callable(server.call_model))
        self.assertTrue(hasattr(server, "Handler"))

    def test_model_client_normalizes_endpoint_and_content(self):
        self.assertEqual(endpoint_url("https://api.example.com"), "https://api.example.com/chat/completions")
        self.assertEqual(
            endpoint_url("https://api.example.com/chat/completions"),
            "https://api.example.com/chat/completions",
        )
        self.assertEqual(
            extract_content({"choices": [{"message": {"content": [{"text": "你"}, {"text": "好"}]}}]}),
            "你好",
        )

    def test_payload_validation_is_available_without_importing_engine(self):
        clean = sanitize_chat_payload({"latest_message": " 你好 ", "messages": []})

        self.assertEqual(clean["latest_message"], "你好")
        self.assertEqual(clean["messages"], [])

    def test_runtime_version_is_exposed(self):
        self.assertEqual(APP_VERSION, "2026.07.17.3")


if __name__ == "__main__":
    unittest.main()
