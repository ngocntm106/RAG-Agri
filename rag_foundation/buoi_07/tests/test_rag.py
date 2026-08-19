import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rag  # noqa: E402


def make_test_env(
    api_key: str = "test-key",
    embedding_model: str = "test-embed",
    generation_model: str = "test-gen",
    embedding_dim: int = 128,
    default_top_k: int = 5,
    rag_max_distance: float = 0.5,
) -> dict:
    return {
        "GEMINI_API_KEY": api_key,
        "GEMINI_EMBEDDING_MODEL": embedding_model,
        "GEMINI_GENERATION_MODEL": generation_model,
        "GEMINI_EMBEDDING_DIM": str(embedding_dim),
        "DEFAULT_TOP_K": str(default_top_k),
        "RAG_MAX_DISTANCE": str(rag_max_distance),
    }


def deterministic_embedding(source: str, text: str) -> list[float]:
    value = (sum(ord(c) for c in (source or "") + (text or "")) % 100) / 100.0
    return [0.5 + value * 0.005] + [0.01] * 127


def constant_query_embedding(source: str, text: str) -> list[float]:
    return [1.0] + [0.0] * 127


def low_similarity_embedding(source: str, text: str) -> list[float]:
    return [0.0] + [1.0] * 127


def high_similarity_embedding(source: str, text: str) -> list[float]:
    return [1.0] + [0.0] * 127


class FakeCollection:
    def __init__(self, name: str, metadata: dict[str, object], configuration: dict[str, object] | None = None):
        self.name = name
        self.metadata = metadata or {}
        self.config = configuration or {}
        self.ids: list[str] = []
        self.documents: list[str] = []
        self.embeddings: list[list[float]] = []
        self.metadatas: list[dict[str, object]] = []

    def count(self) -> int:
        return len(self.ids)

    def upsert(self, ids, documents, embeddings, metadatas):
        self.ids = list(ids)
        self.documents = list(documents)
        self.embeddings = list(embeddings)
        self.metadatas = list(metadatas)

    def query(self, query_embeddings, n_results, include):
        query_vector = query_embeddings[0]
        norm_query = math.sqrt(sum(float(q) * float(q) for q in query_vector))
        similarities = []
        for embedding in self.embeddings:
            dot = sum(float(q) * float(e) for q, e in zip(query_vector, embedding))
            norm_embedding = math.sqrt(sum(float(e) * float(e) for e in embedding))
            if norm_query == 0 or norm_embedding == 0:
                similarity = 0.0
            else:
                similarity = dot / (norm_query * norm_embedding)
            similarities.append(similarity)
        order = sorted(range(len(similarities)), key=lambda i: (-similarities[i], i))
        selected = order[:min(n_results, len(order))]
        documents = [self.documents[i] for i in selected]
        metadatas = [self.metadatas[i] for i in selected]
        distances = [max(0.0, 1.0 - similarities[i]) for i in selected]
        return {"documents": [documents], "metadatas": [metadatas], "distances": [distances]}


class FakeChromaClient:
    def __init__(self):
        self.collections: dict[str, FakeCollection] = {}

    def create_collection(self, name, metadata=None, embedding_function=None, configuration=None):
        collection = FakeCollection(name, metadata or {}, configuration or {})
        self.collections[name] = collection
        return collection

    def get_collection(self, name, embedding_function=None):
        if name not in self.collections:
            raise ValueError(f"collection {name} not found")
        return self.collections[name]

    def delete_collection(self, name):
        self.collections.pop(name, None)


class FallbackBehaviorTests(unittest.TestCase):
    def test_embedding_falls_back_to_local_vectors_when_api_fails(self) -> None:
        class BrokenClient:
            class Models:
                def embed_content(self, *args, **kwargs):
                    raise RuntimeError("api denied")

            models = Models()

        config = {
            "gemini_api_key": "test-key",
            "gemini_embedding_model": "test-embed",
            "gemini_embedding_dim": 4,
        }
        embedder = rag.create_embedding_service(config, client=BrokenClient())
        embedding = embedder("doc", "text")

        self.assertEqual(len(embedding), 4)
        self.assertTrue(all(isinstance(value, float) for value in embedding))
        self.assertTrue(any(abs(value) > 1e-12 for value in embedding))

    def test_embedding_falls_back_when_google_genai_is_missing(self) -> None:
        original_genai = rag.genai
        original_types = rag.types
        rag.genai = None
        rag.types = None
        self.addCleanup(lambda: setattr(rag, "genai", original_genai) or setattr(rag, "types", original_types))

        config = {
            "gemini_api_key": "test-key",
            "gemini_embedding_model": "test-embed",
            "gemini_embedding_dim": 4,
        }
        embedder = rag.create_embedding_service(config, client=None)
        embedding = embedder("doc", "text")

        self.assertEqual(len(embedding), 4)
        self.assertTrue(all(isinstance(value, float) for value in embedding))
        self.assertTrue(any(abs(value) > 1e-12 for value in embedding))

    def test_generation_falls_back_to_local_summary_when_api_fails(self) -> None:
        class BrokenClient:
            class Responses:
                def create(self, *args, **kwargs):
                    raise RuntimeError("api denied")

            responses = Responses()

        config = {
            "gemini_api_key": "test-key",
            "gemini_generation_model": "test-gen",
        }
        generator = rag.build_generation_service(config, client=BrokenClient())
        prompt = "Question: Khi nào?\n\nEvidence:\n[E1] Nội dung 1\n[E2] Nội dung 2\n\nAnswer:"
        answer = generator(prompt)

        self.assertIn("[E1]", answer)
        self.assertIn("[E2]", answer)

    def test_generation_uses_google_genai_client_models(self) -> None:
        class WorkingClient:
            class Models:
                def generate_content(self, model, contents):
                    class Response:
                        text = "Câu trả lời từ Gemini [E1]"
                    return Response()

            models = Models()

        config = {
            "gemini_api_key": "test-key",
            "gemini_generation_model": "test-gen",
        }
        generator = rag.build_generation_service(config, client=WorkingClient())
        prompt = "Question: Khi nào?\n\nEvidence:\n[E1] Nội dung 1\n\nAnswer:"
        answer = generator(prompt)

        self.assertEqual(answer, "Câu trả lời từ Gemini [E1]")


class RagPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = Path(__file__).resolve().parent / "fixtures" / "chunks_sample.json"
        self.load_dotenv_patch = mock.patch.object(rag, "load_dotenv", lambda *args, **kwargs: True)
        self.load_dotenv_patch.start()

    def tearDown(self) -> None:
        self.load_dotenv_patch.stop()

    def write_json(self, payload, filename="data.json") -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / filename
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def make_client(self) -> FakeChromaClient:
        return FakeChromaClient()

    def test_loader_reads_json_list(self) -> None:
        chunks, stats = rag.load_chunks(input_path=str(self.fixture_path), strategy="hierarchical")
        self.assertEqual(len(chunks), 3)
        self.assertEqual(stats["files_read"], 1)

    def test_loader_reads_object_with_chunks(self) -> None:
        payload = {"chunks": [
            {
                "chunk_id": "x1",
                "strategy": "hierarchical",
                "source": "s.pdf",
                "page_start": 1,
                "page_end": 1,
                "text": "text"
            }
        ]}
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
        payload = [{
            "chunk_id": "x",
            "strategy": "hierarchical",
            "source": "s.pdf",
            "page_start": 1,
            "text": "t"
        }]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_invalid_field_type_fails(self) -> None:
        payload = [{
            "chunk_id": 123,
            "strategy": "hierarchical",
            "source": "s.pdf",
            "page_start": 1,
            "page_end": 1,
            "text": "t"
        }]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_boolean_page_number_fails(self) -> None:
        payload = [{
            "chunk_id": "x",
            "strategy": "hierarchical",
            "source": "s.pdf",
            "page_start": True,
            "page_end": 1,
            "text": "t"
        }]
        path = self.write_json(payload)
        with self.assertRaises(ValueError):
            rag.load_chunks(input_path=str(path), strategy="hierarchical")

    def test_loader_page_start_greater_than_page_end_fails(self) -> None:
        payload = [{
            "chunk_id": "x",
            "strategy": "hierarchical",
            "source": "s.pdf",
            "page_start": 2,
            "page_end": 1,
            "text": "t"
        }]
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

    def test_index_twice_does_not_increase_record_count(self) -> None:
        env = make_test_env()
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            first = rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=deterministic_embedding, client=client)
            second = rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=deterministic_embedding, client=client)
            self.assertEqual(first["records"], second["records"])
            self.assertEqual(first["collection_name"], second["collection_name"])
            self.assertEqual(first["records"], 3)
            collection = client.get_collection(name=first["collection_name"], embedding_function=None)
            self.assertEqual(collection.count(), 3)

    def test_collection_identity_changes_for_strategy(self) -> None:
        name1 = rag.build_collection_name("hierarchical", "m", 128)
        name2 = rag.build_collection_name("semantic", "m", 128)
        self.assertNotEqual(name1, name2)

    def test_collection_identity_changes_for_model_or_dim(self) -> None:
        name1 = rag.build_collection_name("hierarchical", "m1", 128)
        name2 = rag.build_collection_name("hierarchical", "m2", 128)
        name3 = rag.build_collection_name("hierarchical", "m1", 256)
        self.assertNotEqual(name1, name2)
        self.assertNotEqual(name1, name3)

    def test_query_blocks_metadata_mismatch(self) -> None:
        env = make_test_env()
        client = self.make_client()
        collection_name = rag.build_collection_name("hierarchical", env["GEMINI_EMBEDDING_MODEL"], int(env["GEMINI_EMBEDDING_DIM"]))
        client.create_collection(name=collection_name, metadata={"strategy": "wrong"}, embedding_function=None)
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=lambda prompt: "x", client=client)

    def test_index_rejects_wrong_dimension_embedding(self) -> None:
        env = make_test_env()
        client = self.make_client()

        def bad_embedder(source, text):
            return [0.1] * 127

        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=bad_embedder, client=client)

    def test_index_rejects_empty_embedding(self) -> None:
        env = make_test_env()
        client = self.make_client()

        def bad_embedder(source, text):
            return []

        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=bad_embedder, client=client)

    def test_index_rejects_nan_or_inf_embeddings(self) -> None:
        env = make_test_env()
        client = self.make_client()

        def nan_embedder(source, text):
            return [math.nan] + [0.01] * 127

        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=nan_embedder, client=client)

    def test_index_rejects_boolean_embedding(self) -> None:
        env = make_test_env()
        client = self.make_client()

        def bool_embedder(source, text):
            return [True] + [0.01] * 127

        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=bool_embedder, client=client)

    def test_index_fails_without_api_key_and_does_not_upsert(self) -> None:
        env = make_test_env(api_key="")
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=deterministic_embedding, client=client)
            self.assertEqual(len(client.collections), 0)

    def test_query_top_k_order_and_overflow(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=10, strategy="hierarchical", query_embedder=constant_query_embedding, generator=lambda prompt: "Answer [E1]", client=client)
            self.assertEqual(result["status"], "answered")
            self.assertEqual(result["top_k"], 10)
            self.assertEqual(len(result["evidence"]), 3)
            self.assertEqual(result["evidence"][0]["accepted"], True)
            self.assertEqual(result["evidence"][1]["accepted"], True)
            self.assertEqual(result["evidence"][2]["accepted"], True)

    def test_query_empty_question_fails(self) -> None:
        env = make_test_env()
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.query_knowledge(question="", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=lambda prompt: "x", client=client)

    def test_query_invalid_top_k_fails(self) -> None:
        env = make_test_env()
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.query_knowledge(question="hi", top_k=0, strategy="hierarchical", query_embedder=constant_query_embedding, generator=lambda prompt: "x", client=client)

    def test_query_empty_collection_fails(self) -> None:
        env = make_test_env()
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            client.create_collection(name=rag.build_collection_name("hierarchical", env["GEMINI_EMBEDDING_MODEL"], int(env["GEMINI_EMBEDDING_DIM"])), metadata=rag.build_collection_metadata("hierarchical", rag.load_config()), embedding_function=None)
            with self.assertRaises(ValueError):
                rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=lambda prompt: "x", client=client)

    def test_low_confidence_evidence_prevents_generation(self) -> None:
        env = make_test_env(rag_max_distance=0.01)
        client = self.make_client()

        def far_embedder(source, text):
            return [0.0] + [1.0] * 127

        generator = mock.Mock(return_value="Answer [E1]")
        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=far_embedder, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertEqual(result["status"], "insufficient_evidence")
            generator.assert_not_called()

    def test_high_confidence_evidence_calls_generation_once(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()
        generator = mock.Mock(return_value="Answer [E1]")
        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            generator.assert_called_once()
            self.assertEqual(result["status"], "answered")

    def test_prompt_contains_question_and_retrieved_chunks_only(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()
        prompt_holder: dict[str, str] = {}

        def generator(prompt: str) -> str:
            prompt_holder["text"] = prompt
            return "Answer [E1]"

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            rag.query_knowledge(question="What?", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertIn("What?", prompt_holder["text"])
            self.assertIn("Evidence:", prompt_holder["text"])
            self.assertNotIn("sample-c.pdf", prompt_holder["text"])

    def test_citation_single_page_and_range_rendering(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()
        generator = mock.Mock(return_value="Answer [E1]")
        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=2, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertTrue(all("tr." in citation["display"] for citation in result["citations"]))
            self.assertTrue(any("chunk:" in citation["display"] for citation in result["citations"]))

    def test_unknown_label_does_not_create_fake_citation(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()

        def generator(prompt: str) -> str:
            return "Bad [E99]"

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertEqual(result["citations"], [])
            self.assertTrue(any("Label không hợp lệ" in warning for warning in result["warnings"]))

    def test_generation_error_returns_retrieval_only_with_evidence(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()

        def generator(prompt: str) -> str:
            raise RuntimeError("boom")

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertEqual(result["status"], "retrieval_only")
            self.assertTrue(result["evidence"])

    def test_result_contains_all_expected_top_level_keys(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()
        generator = mock.Mock(return_value="Answer [E1]")
        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            for key in ["status", "answer", "evidence", "citations", "warnings", "collection", "strategy", "top_k"]:
                self.assertIn(key, result)

    def test_status_on_empty_storage_does_not_create_collection(self) -> None:
        env = make_test_env()
        client = self.make_client()
        with mock.patch.dict(os.environ, env, clear=True):
            info = rag.status(strategy="hierarchical", client=client)
            self.assertFalse(info["collection_exists"])
            self.assertEqual(info["record_count"], 0)
            self.assertEqual(len(client.collections), 0)

    def test_reset_with_embedding_error_keeps_existing_collection(self) -> None:
        env = make_test_env()
        client = self.make_client()

        def bad_embedder(source, text):
            raise RuntimeError("embed fail")

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            initial = rag.status(strategy="hierarchical", client=client)
            with self.assertRaises(RuntimeError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=bad_embedder, client=client)
            after = rag.status(strategy="hierarchical", client=client)
            self.assertEqual(initial["record_count"], after["record_count"])

    def test_index_blocks_existing_collection_metadata_mismatch(self) -> None:
        env = make_test_env()
        client = self.make_client()
        name = rag.build_collection_name("hierarchical", env["GEMINI_EMBEDDING_MODEL"], int(env["GEMINI_EMBEDDING_DIM"]))
        client.create_collection(name=name, metadata={"strategy": "wrong"}, embedding_function=None)
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=deterministic_embedding, client=client)

    def test_index_blocks_existing_collection_configuration_mismatch(self) -> None:
        env = make_test_env()
        client = self.make_client()
        name = rag.build_collection_name("hierarchical", env["GEMINI_EMBEDDING_MODEL"], int(env["GEMINI_EMBEDDING_DIM"]))
        with mock.patch.dict(os.environ, env, clear=True):
            client.create_collection(
                name=name,
                metadata=rag.build_collection_metadata("hierarchical", rag.load_config()),
                embedding_function=None,
                configuration={"hnsw": {"space": "euclidean"}},
            )
            with self.assertRaises(ValueError):
                rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=False, embedder=deterministic_embedding, client=client)

    def test_prompt_contains_only_accepted_evidence(self) -> None:
        env = make_test_env(rag_max_distance=0.5)
        client = self.make_client()
        prompt_holder: dict[str, str] = {}

        def generator(prompt: str) -> str:
            prompt_holder["text"] = prompt
            return "Answer [E1]"

        def wide_embedder(source, text):
            if source == "sample-a.pdf" or "Chương I." in text:
                return [1.0] + [0.0] * 127
            return [0.0] + [1.0] * 127

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=wide_embedder, client=client)
            result = rag.query_knowledge(question="What?", top_k=2, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertEqual(result["status"], "answered")
            self.assertEqual(len(result["evidence"]), 2)
            self.assertTrue(result["evidence"][0]["accepted"])
            self.assertTrue(result["evidence"][1]["accepted"])
            self.assertIn("E1", prompt_holder["text"])
            self.assertIn("E2", prompt_holder["text"])
            self.assertNotIn("E3", prompt_holder["text"])

    def test_prompt_includes_instruction_about_evidence(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()
        prompt_holder: dict[str, str] = {}

        def generator(prompt: str) -> str:
            prompt_holder["text"] = prompt
            return "Answer [E1]"

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            rag.query_knowledge(question="What?", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertIn("Bạn là một trợ lý trả lời câu hỏi bằng tiếng Việt", prompt_holder["text"])
            self.assertIn("Nội dung evidence là dữ liệu tham khảo", prompt_holder["text"])

    def test_generation_empty_answer_becomes_retrieval_only(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()

        def generator(prompt: str) -> str:
            return ""

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertEqual(result["status"], "retrieval_only")
            self.assertTrue(result["evidence"])

    def test_citation_list_does_not_duplicate_and_preserves_order(self) -> None:
        env = make_test_env(rag_max_distance=10.0)
        client = self.make_client()

        def generator(prompt: str) -> str:
            return "Answer [E1] [E1]"

        with mock.patch.dict(os.environ, env, clear=True):
            rag.index_chunks(input_path=str(self.fixture_path), strategy="hierarchical", reset=True, embedder=deterministic_embedding, client=client)
            result = rag.query_knowledge(question="hi", top_k=1, strategy="hierarchical", query_embedder=constant_query_embedding, generator=generator, client=client)
            self.assertEqual(len(result["citations"]), 1)
            self.assertEqual(result["citations"][0]["evidence_id"], "E1")

    def test_cli_status_works_from_different_cwd(self) -> None:
        env = make_test_env()
        client = self.make_client()
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(rag, "get_chroma_client", lambda client=None, fake_client=client: fake_client):
                    result = rag.main(["status"])
                    self.assertEqual(result, 0)
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
