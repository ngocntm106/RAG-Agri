import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app  # noqa: E402


class AppStatusTests(unittest.TestCase):
    def test_resolve_collection_state_uses_latest_status(self) -> None:
        with mock.patch.object(app, "build_status_info", return_value=({"collection_exists": True, "record_count": 7}, None)):
            status_info, collection_exists, record_count, status_error = app.resolve_collection_state("hierarchical", {"gemini_embedding_model": "m", "gemini_embedding_dim": 128})

        self.assertTrue(collection_exists)
        self.assertEqual(record_count, 7)
        self.assertIsNone(status_error)
        self.assertEqual(status_info["record_count"], 7)


if __name__ == "__main__":
    unittest.main()
