import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rag  # noqa: E402


class LoaderValidatorTests(unittest.TestCase):
    def write_json(self, payload):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "data.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_loader_reads_json_list(self) -> None:
        fixture_path = Path(__file__).resolve().parent / "fixtures" / "chunks_sample.json"
        chunks, stats = rag.load_chunks(input_path=str(fixture_path), strategy="hierarchical")

        self.assertEqual(len(chunks), 3)
        self.assertEqual(stats["files_read"], 1)
        self.assertEqual(stats["selected_records"], 3)
        self.assertEqual(stats["valid_chunks"], 3)

    def test_loader_reads_object_with_chunks(self) -> None:
        payload = {
            "chunks": [
                {
                    "chunk_id": "x1",
                    "strategy": "hierarchical",
                    "source": "s.pdf",
                    "page_start": 1,
                    "page_end": 1,
                    "text": "text"
                }
            ]
        }
        path = self.write_json(payload)
        chunks, stats = rag.load_chunks(input_path=str(path), strategy="hierarchical")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(stats["valid_chunks"], 1)

    def test_loader_only_selects_strategy(self) -> None:
        payload = [
            {
                "chunk_id": "a",
                "strategy": "semantic",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "t1"
            },
            {
                "chunk_id": "b",
                "strategy": "fixed-size",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "t2"
            },
        ]
        path = self.write_json(payload)
        chunks, stats = rag.load_chunks(input_path=str(path), strategy="fixed-size")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["chunk_id"], "b")
        self.assertEqual(stats["selected_records"], 1)

    def test_loader_missing_required_field_fails(self) -> None:
        payload = [
            {
                "chunk_id": "x",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "text": "t"
            }
        ]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_invalid_field_type_fails(self) -> None:
        payload = [
            {
                "chunk_id": 123,
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "t"
            }
        ]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_boolean_page_number_fails(self) -> None:
        payload = [
            {
                "chunk_id": "x",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": True,
                "page_end": 1,
                "text": "t"
            }
        ]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_page_start_greater_than_page_end_fails(self) -> None:
        payload = [
            {
                "chunk_id": "x",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 2,
                "page_end": 1,
                "text": "t"
            }
        ]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_skips_empty_text_and_counts(self) -> None:
        payload = [
            {
                "chunk_id": "x",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": ""
            },
            {
                "chunk_id": "y",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "ok"
            },
        ]
        path = self.write_json(payload)
        chunks, stats = rag.load_chunks(input_path=str(path), strategy="hierarchical")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(stats["empty_text_skipped"], 1)

    def test_loader_duplicate_chunk_id_fails(self) -> None:
        payload = [
            {
                "chunk_id": "x",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "t"
            },
            {
                "chunk_id": "x",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "t"
            },
        ]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_rejects_non_json_object_record(self) -> None:
        payload = ["not-an-object"]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")


if __name__ == "__main__":
    unittest.main()
