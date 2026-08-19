"""Tests cho Bước 05: advanced_status, get_semantic_candidates, prepare_semantic.

Tất cả test chạy offline — mock Gemini embedding và dùng Chroma in-memory.
Không tải model, không gọi API thật, không generation.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BUOI08_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUOI08_DIR))

import advanced_rag
from advanced_rag import advanced_status, bm25_search, get_semantic_candidates

FIXTURE_PATH = BUOI08_DIR / "tests" / "fixtures" / "chunks_advanced_sample.json"


# ─────────────────────────────────────────────────────────────
# Helpers to build in-memory Chroma collection
# ─────────────────────────────────────────────────────────────

def _make_mock_vector(dim: int = 128, seed: int = 1) -> list:
    """Tạo vector giả đủ dài, không phải zero vector."""
    import math
    v = [math.sin(seed * (i + 1) * 0.1) for i in range(dim)]
    return v


def _make_mock_embedder(dim: int = 128) -> callable:
    """Trả về hàm embed trả vector khác nhau theo nội dung text."""
    counter = [0]

    def embedder(source: str, text: str) -> list:
        counter[0] += 1
        return _make_mock_vector(dim, seed=counter[0])

    return embedder


def _build_test_chroma_collection(
    chunks: list,
    collection_name: str = "test-col",
    strategy: str = "fixed-size",
    embedding_model: str = "test-model",
    embedding_dim: int = 128,
):
    """Xây dựng Chroma EphemeralClient collection có dữ liệu, trả (client, collection)."""
    import chromadb

    client = chromadb.EphemeralClient()
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass
    meta = {
        "strategy": strategy,
        "embedding_model": embedding_model,
        "embedding_dim": embedding_dim,
        "distance_metric": "cosine",
        "schema_version": "1",
    }
    col = client.create_collection(
        name=collection_name,
        metadata=meta,
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
    )
    embedder = _make_mock_embedder(embedding_dim)
    ids, docs, embeds, metas = [], [], [], []
    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        docs.append(chunk["text"])
        embeds.append(embedder(chunk["source"], chunk["text"]))
        metas.append({
            "source": chunk["source"],
            "strategy": chunk["strategy"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "chunk_id": chunk["chunk_id"],
            "embedding_model": embedding_model,
            "embedding_dim": embedding_dim,
        })
    col.upsert(ids=ids, documents=docs, embeddings=embeds, metadatas=metas)
    return client, col


def _load_fixture_chunks(strategy: str = "fixed-size") -> list:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [c for c in data if c["strategy"] == strategy]


# ─────────────────────────────────────────────────────────────
# Shared rag-config mock patch
# ─────────────────────────────────────────────────────────────

RAG_CONFIG_MOCK = {
    "gemini_api_key": "FAKE_KEY_FOR_TEST",
    "gemini_embedding_model": "test-model",
    "gemini_embedding_dim": 128,
    "gemini_generation_model": "test-gen",
    "default_top_k": 5,
    "rag_max_distance": 0.45,
}


# ─────────────────────────────────────────────────────────────
# 1. Semantic top-k, count và order đúng
# ─────────────────────────────────────────────────────────────

class TestSemanticTopK(unittest.TestCase):

    def setUp(self):
        self.chunks = _load_fixture_chunks("fixed-size")
        self.dim = 128
        self.model = "test-model"
        self.strategy = "fixed-size"
        self.col_name = "nhnn-fixed-size-128-" + __import__("hashlib").sha1(self.model.encode()).hexdigest()[:8]
        self.client, self.col = _build_test_chroma_collection(
            self.chunks, self.col_name, self.strategy, self.model, self.dim
        )

    def _do_query(self, question: str, k: int):
        embedder = _make_mock_embedder(self.dim)

        def query_embedder(source, text):
            return _make_mock_vector(self.dim, seed=99)

        with patch.object(
            __import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK
        ), patch.object(
            __import__("rag"), "get_chroma_client", return_value=self.client
        ):
            return get_semantic_candidates(
                question=question,
                candidate_k=k,
                strategy=self.strategy,
                query_embedder=query_embedder,
                chroma_client=self.client,
            )

    def test_returns_correct_count(self):
        """Số candidate trả về phải <= min(candidate_k, corpus_size)."""
        corpus_size = len(self.chunks)
        results = self._do_query("lãi suất", k=3)
        self.assertLessEqual(len(results), min(3, corpus_size))
        self.assertEqual(len(results), 3)

    def test_top_k_larger_than_corpus_clamped(self):
        """candidate_k > corpus_size phải clamp xuống corpus_size."""
        corpus_size = len(self.chunks)
        results = self._do_query("lãi suất", k=1000)
        self.assertEqual(len(results), corpus_size)

    def test_semantic_rank_sequential(self):
        """semantic_rank phải liên tiếp từ 1."""
        results = self._do_query("tổ chức tín dụng", k=4)
        ranks = [r["semantic_rank"] for r in results]
        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))

    def test_distance_non_decreasing(self):
        """Kết quả Chroma trả về theo thứ tự distance tăng dần (distance thấp hơn xếp trước)."""
        results = self._do_query("tổ chức tín dụng", k=4)
        distances = [r["semantic_distance"] for r in results]
        self.assertEqual(distances, sorted(distances))


# ─────────────────────────────────────────────────────────────
# 2. Metadata đầy đủ (7 fields theo contract)
# ─────────────────────────────────────────────────────────────

class TestSemanticMetadata(unittest.TestCase):

    def setUp(self):
        self.chunks = _load_fixture_chunks("fixed-size")
        self.dim = 128
        self.model = "test-model"
        self.strategy = "fixed-size"
        self.col_name = "nhnn-fixed-size-128-" + __import__("hashlib").sha1(self.model.encode()).hexdigest()[:8]
        self.client, _ = _build_test_chroma_collection(
            self.chunks, self.col_name, self.strategy, self.model, self.dim
        )

    def _do_query(self, question: str, k: int = 3):
        def query_embedder(source, text):
            return _make_mock_vector(self.dim, seed=42)

        with patch.object(
            __import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK
        ), patch.object(
            __import__("rag"), "get_chroma_client", return_value=self.client
        ):
            return get_semantic_candidates(
                question=question,
                candidate_k=k,
                strategy=self.strategy,
                query_embedder=query_embedder,
                chroma_client=self.client,
            )

    def test_all_required_fields_present(self):
        """Tất cả 7 field bắt buộc phải có trong mỗi candidate."""
        required = {"chunk_id", "text", "source", "page_start", "page_end",
                    "semantic_rank", "semantic_distance"}
        results = self._do_query("cơ cấu lại thời hạn trả nợ")
        for r in results:
            self.assertEqual(required & set(r.keys()), required,
                             f"Thiếu field trong: {r}")

    def test_distance_is_float(self):
        """semantic_distance phải là float."""
        results = self._do_query("tổ chức tín dụng")
        for r in results:
            self.assertIsInstance(r["semantic_distance"], float)

    def test_page_values_positive(self):
        """page_start và page_end phải là số nguyên dương."""
        results = self._do_query("lãi suất cho vay")
        for r in results:
            self.assertIsInstance(r["page_start"], int)
            self.assertIsInstance(r["page_end"], int)
            self.assertGreater(r["page_start"], 0)


# ─────────────────────────────────────────────────────────────
# 3. Collection metadata mismatch bị chặn
# ─────────────────────────────────────────────────────────────

class TestCollectionMismatch(unittest.TestCase):

    def _make_wrong_collection(self, wrong_field: str, wrong_value):
        """Tạo collection có metadata sai một field."""
        import chromadb, hashlib
        dim = 128
        model = "test-model"
        strategy = "fixed-size"
        col_name = "nhnn-fixed-size-128-" + hashlib.sha1(model.encode()).hexdigest()[:8]
        client = chromadb.EphemeralClient()
        try:
            client.delete_collection(name=col_name)
        except Exception:
            pass
        meta = {
            "strategy": strategy,
            "embedding_model": model,
            "embedding_dim": dim,
            "distance_metric": "cosine",
            "schema_version": "1",
        }
        meta[wrong_field] = wrong_value
        col = client.create_collection(
            name=col_name,
            metadata=meta,
            embedding_function=None,
            configuration={"hnsw": {"space": "cosine"}},
        )
        # Thêm 1 doc để collection không rỗng
        col.upsert(
            ids=["dummy"],
            documents=["dummy text"],
            embeddings=[_make_mock_vector(dim)],
            metadatas=[{"source": "x", "strategy": strategy,
                        "page_start": 1, "page_end": 1,
                        "chunk_id": "dummy", "embedding_model": model,
                        "embedding_dim": dim}],
        )
        return client

    def test_strategy_mismatch_raises(self):
        """Collection với strategy metadata sai phải raise ValueError."""
        client = self._make_wrong_collection("strategy", "wrong-strategy")

        def query_embedder(source, text):
            return _make_mock_vector(128)

        with patch.object(__import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=client):
            with self.assertRaises(ValueError) as ctx:
                get_semantic_candidates(
                    question="test", candidate_k=5,
                    strategy="fixed-size",
                    query_embedder=query_embedder,
                    chroma_client=client,
                )
            self.assertIn("mismatch", str(ctx.exception).lower())

    def test_embedding_model_mismatch_raises(self):
        """Collection với embedding_model metadata sai phải raise ValueError."""
        client = self._make_wrong_collection("embedding_model", "different-model")

        def query_embedder(source, text):
            return _make_mock_vector(128)

        with patch.object(__import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=client):
            with self.assertRaises(ValueError) as ctx:
                get_semantic_candidates(
                    question="test", candidate_k=5,
                    strategy="fixed-size",
                    query_embedder=query_embedder,
                    chroma_client=client,
                )
            self.assertIn("mismatch", str(ctx.exception).lower())

    def test_nonexistent_collection_raises(self):
        """Collection chưa tồn tại phải raise ValueError rõ."""
        import chromadb
        empty_client = chromadb.EphemeralClient()  # không có collection nào
        for col in empty_client.list_collections():
            try:
                name = col.name if hasattr(col, "name") else str(col)
                empty_client.delete_collection(name)
            except Exception:
                pass

        def query_embedder(source, text):
            return _make_mock_vector(128)

        with patch.object(__import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=empty_client):
            with self.assertRaises(ValueError) as ctx:
                get_semantic_candidates(
                    question="test", candidate_k=5,
                    strategy="fixed-size",
                    query_embedder=query_embedder,
                    chroma_client=empty_client,
                )
            self.assertIn("chưa tồn tại", str(ctx.exception))


# ─────────────────────────────────────────────────────────────
# 4. Status không tạo collection
# ─────────────────────────────────────────────────────────────

class TestStatusReadOnly(unittest.TestCase):

    def test_status_does_not_create_collection(self):
        """advanced_status không được tạo collection mới trong Chroma."""
        import chromadb
        empty_client = chromadb.EphemeralClient()
        for col in empty_client.list_collections():
            try:
                name = col.name if hasattr(col, "name") else str(col)
                empty_client.delete_collection(name)
            except Exception:
                pass
        before_count = len(empty_client.list_collections())

        config_no_key = dict(RAG_CONFIG_MOCK, gemini_api_key="")

        with patch.object(__import__("rag"), "load_config", return_value=config_no_key), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=empty_client), \
             patch.object(__import__("rag"), "load_chunks", return_value=([], {"valid_chunks": 0})):
            info = advanced_status(strategy="hierarchical", chroma_client=empty_client)

        after_count = len(empty_client.list_collections())
        self.assertEqual(before_count, after_count,
                         "advanced_status đã tạo collection — vi phạm read-only contract")
        self.assertFalse(info["collection_exists"])

    def test_status_returns_all_keys(self):
        """advanced_status phải trả về đủ các key chuẩn."""
        expected_keys = {
            "strategy", "corpus_size", "bm25_ready",
            "semantic_collection_name", "collection_exists", "collection_count",
            "embedding_model", "embedding_dim", "api_key_present",
            "reranker_model", "reranker_cache_exists",
        }
        import chromadb
        empty_client = chromadb.EphemeralClient()
        for col in empty_client.list_collections():
            try:
                name = col.name if hasattr(col, "name") else str(col)
                empty_client.delete_collection(name)
            except Exception:
                pass
        with patch.object(__import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=empty_client), \
             patch.object(__import__("rag"), "load_chunks", return_value=([], {"valid_chunks": 0})):
            info = advanced_status(strategy="hierarchical", chroma_client=empty_client)
        self.assertEqual(expected_keys, set(info.keys()))

    def test_status_with_existing_collection(self):
        """Status phải báo collection_exists=True và đếm đúng khi có data."""
        chunks = _load_fixture_chunks("fixed-size")
        import hashlib
        col_name = "nhnn-fixed-size-128-" + hashlib.sha1(b"test-model").hexdigest()[:8]
        client, _ = _build_test_chroma_collection(
            chunks, col_name, "fixed-size", "test-model", 128
        )
        with patch.object(__import__("rag"), "load_config", return_value=RAG_CONFIG_MOCK), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=client), \
             patch.object(__import__("rag"), "load_chunks",
                          return_value=(chunks, {"valid_chunks": len(chunks)})):
            info = advanced_status(strategy="fixed-size", chroma_client=client)
        self.assertTrue(info["collection_exists"])
        self.assertEqual(info["collection_count"], len(chunks))
        self.assertTrue(info["bm25_ready"])


# ─────────────────────────────────────────────────────────────
# 5. Không có key → không dùng vector giả, phải fail
# ─────────────────────────────────────────────────────────────

class TestNoKeyNoFallback(unittest.TestCase):

    def test_missing_api_key_raises_without_embedder(self):
        """Thiếu API key và không truyền query_embedder phải raise ValueError."""
        config_no_key = dict(RAG_CONFIG_MOCK, gemini_api_key="")
        import chromadb
        client = chromadb.EphemeralClient()

        with patch.object(__import__("rag"), "load_config", return_value=config_no_key), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=client):
            with self.assertRaises(ValueError) as ctx:
                get_semantic_candidates(
                    question="test", candidate_k=5, strategy="fixed-size",
                    query_embedder=None,  # Không truyền embedder
                    chroma_client=client,
                )
            self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    def test_with_mock_embedder_no_key_succeeds_if_collection_exists(self):
        """Nếu có mock embedder (test scenario), không cần API key để query."""
        chunks = _load_fixture_chunks("fixed-size")
        import hashlib
        col_name = "nhnn-fixed-size-128-" + hashlib.sha1(b"test-model").hexdigest()[:8]
        client, _ = _build_test_chroma_collection(
            chunks, col_name, "fixed-size", "test-model", 128
        )
        config_no_key = dict(RAG_CONFIG_MOCK, gemini_api_key="")

        def mock_embedder(source, text):
            return _make_mock_vector(128, seed=7)

        with patch.object(__import__("rag"), "load_config", return_value=config_no_key), \
             patch.object(__import__("rag"), "get_chroma_client", return_value=client):
            # Vẫn pass vì query_embedder được cung cấp (test mode)
            results = get_semantic_candidates(
                question="tổ chức tín dụng", candidate_k=3,
                strategy="fixed-size",
                query_embedder=mock_embedder,
                chroma_client=client,
            )
        self.assertGreater(len(results), 0)


# ─────────────────────────────────────────────────────────────
# 6. Không gọi generation
# ─────────────────────────────────────────────────────────────

class TestNoGeneration(unittest.TestCase):

    def test_semantic_candidates_does_not_call_generation(self):
        """get_semantic_candidates không được gọi bất kỳ generation function nào."""
        import inspect
        source = inspect.getsource(advanced_rag.get_semantic_candidates)
        # Các từ khóa liên quan đến generation
        generation_indicators = [
            "generate_content", "_build_generation_prompt",
            "query_knowledge", "generation_model",
        ]
        for indicator in generation_indicators:
            self.assertNotIn(indicator, source,
                             f"get_semantic_candidates có reference đến '{indicator}'")

    def test_advanced_status_does_not_call_generation(self):
        """advanced_status không được tham chiếu đến generation."""
        import inspect
        source = inspect.getsource(advanced_rag.advanced_status)
        self.assertNotIn("generate_content", source)
        self.assertNotIn("query_knowledge", source)

    def test_bm25_search_does_not_use_embeddings(self):
        """bm25_search không được gọi create_embedding_service."""
        import inspect
        source = inspect.getsource(advanced_rag.bm25_search)
        self.assertNotIn("create_embedding_service", source)
        self.assertNotIn("google.genai", source)


if __name__ == "__main__":
    unittest.main()
