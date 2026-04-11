from __future__ import annotations

import unittest

from trevixa.encode.python.api_entrypoint import TrevixaApi
from trevixa.encode.python.model_manager import LocalModelRuntime, LocalModelSpec


class RuntimeTests(unittest.TestCase):
    def test_max_four_models(self) -> None:
        runtime = LocalModelRuntime(lambda p, s: f"{s.name}:{p}")
        runtime.configure([
            LocalModelSpec("A", "1"),
            LocalModelSpec("B", "1"),
            LocalModelSpec("C", "1"),
            LocalModelSpec("D", "1"),
        ])
        self.assertEqual(len(runtime.list_models()), 4)
        with self.assertRaises(ValueError):
            runtime.configure([
                LocalModelSpec("A", "1"),
                LocalModelSpec("B", "1"),
                LocalModelSpec("C", "1"),
                LocalModelSpec("D", "1"),
                LocalModelSpec("E", "1"),
            ])

    def test_session_history(self) -> None:
        api = TrevixaApi()
        _ = api.chat_text("hello world", session_id="s1")
        history = api.sessions.history("s1")
        self.assertGreaterEqual(len(history), 2)

    def test_local_parallel(self) -> None:
        api = TrevixaApi()
        api.set_local_models(["A", "B", "C", "D"])
        result = api.chat_text("@local-all test")
        self.assertIn("[A v0.2.0", result)
        self.assertIn("[D v0.2.0", result)


if __name__ == "__main__":
    unittest.main()
