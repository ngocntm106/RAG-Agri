"""Tests cho Bước 04: tokenize_vi_legal, build_bm25_index, bm25_search.

Tất cả test chạy offline. Không gọi Gemini, Chroma hoặc reranker.
"""

import json
import sys
import unittest
from pathlib import Path

# Đảm bảo import được advanced_rag từ buoi_08/
BUOI08_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUOI08_DIR))

from advanced_rag import bm25_search, build_bm25_index, tokenize_vi_legal

FIXTURE_PATH = BUOI08_DIR / "tests" / "fixtures" / "chunks_advanced_sample.json"


def _load_fixture_chunks(strategy: str = None) -> list:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if strategy:
        return [c for c in data if c["strategy"] == strategy]
    return data


# ──────────────────────────────────────────────────────────────────────────────
# 1. Tokenizer giữ dấu tiếng Việt
# ──────────────────────────────────────────────────────────────────────────────
class TestTokenizerVietnamese(unittest.TestCase):

    def test_vietnamese_diacritics_preserved(self):
        """Tokenizer giữ nguyên chữ tiếng Việt có dấu."""
        tokens = tokenize_vi_legal("cơ cấu lại thời hạn trả nợ")
        self.assertIn("cơ", tokens)
        self.assertIn("cấu", tokens)
        self.assertIn("thời", tokens)
        self.assertIn("hạn", tokens)
        self.assertIn("trả", tokens)
        self.assertIn("nợ", tokens)

    def test_nfc_normalization(self):
        """NFC normalization: cùng ký tự nhưng decomposed form phải match."""
        import unicodedata
        # "nợ" ở dạng NFC
        nfc_text = unicodedata.normalize("NFC", "cơ cấu trả nợ")
        # "nợ" ở dạng NFD (decomposed)
        nfd_text = unicodedata.normalize("NFD", "cơ cấu trả nợ")
        tokens_nfc = tokenize_vi_legal(nfc_text)
        tokens_nfd = tokenize_vi_legal(nfd_text)
        # Cả hai phải cho ra token giống nhau (vì hàm luôn normalize về NFC trước)
        self.assertEqual(tokens_nfc, tokens_nfd)

    def test_casefold(self):
        """Tokenizer casefolding: chữ hoa thành chữ thường."""
        tokens = tokenize_vi_legal("Điều KHOẢN")
        self.assertIn("điều", tokens)
        self.assertIn("khoản", tokens)

    def test_input_type_error(self):
        """Input không phải str phải raise TypeError."""
        with self.assertRaises(TypeError):
            tokenize_vi_legal(123)
        with self.assertRaises(TypeError):
            tokenize_vi_legal(None)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Tokenizer giữ số Điều/Khoản
# ──────────────────────────────────────────────────────────────────────────────
class TestTokenizerLegalNumbers(unittest.TestCase):

    def test_dieu_khoan_numbers(self):
        """Token 'điều', '7', 'khoản', '2' phải có mặt sau tokenize."""
        tokens = tokenize_vi_legal("Điều 7, Khoản 2")
        self.assertIn("điều", tokens)
        self.assertIn("7", tokens)
        self.assertIn("khoản", tokens)
        self.assertIn("2", tokens)

    def test_legal_reference_full(self):
        """Số văn bản như '02' và '2023' phải được giữ lại."""
        tokens = tokenize_vi_legal("Thông tư 02/2023/TT-NHNN")
        self.assertIn("02", tokens)
        self.assertIn("2023", tokens)
        self.assertIn("tt", tokens)
        self.assertIn("nhnn", tokens)

    def test_punctuation_removed(self):
        """Dấu câu thuần (dấu phẩy, dấu chấm) không được trở thành token."""
        tokens = tokenize_vi_legal("Điều 7, Khoản 2.")
        self.assertNotIn(",", tokens)
        self.assertNotIn(".", tokens)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Corpus và query dùng cùng preprocessing
# ──────────────────────────────────────────────────────────────────────────────
class TestCorpusQueryConsistency(unittest.TestCase):

    def test_same_function_for_corpus_and_query(self):
        """build_bm25_index và bm25_search đều gọi tokenize_vi_legal."""
        chunks = [
            {
                "chunk_id": "T1", "strategy": "fixed-size",
                "source": "doc.pdf", "page_start": 1, "page_end": 1,
                "text": "Điều 7 Khoản 2 quy định về lãi suất",
            },
            {
                "chunk_id": "T2", "strategy": "fixed-size",
                "source": "doc.pdf", "page_start": 2, "page_end": 2,
                "text": "Ngân hàng thương mại và tổ chức tín dụng",
            },
        ]
        # Nếu cùng preprocessing thì query chứa exact term sẽ match corpus
        results = bm25_search("Điều 7 Khoản 2", chunks, candidate_k=2)
        self.assertEqual(results[0]["chunk_id"], "T1")

    def test_query_tokens_subset_of_corpus(self):
        """Chunk chứa token truy vấn phải có bm25_rank=1.

        BM25Okapi có thể trả score âm khi corpus nhỏ (IDF behavior),
        nên không kiểm tra score > 0 – chỉ kiểm tra thứ hạng.
        """
        chunks = [
            {
                "chunk_id": "MATCH", "strategy": "fixed-size",
                "source": "doc.pdf", "page_start": 1, "page_end": 1,
                "text": "cơ cấu lại thời hạn trả nợ",
            },
            {
                "chunk_id": "NOMATCH", "strategy": "fixed-size",
                "source": "doc.pdf", "page_start": 2, "page_end": 2,
                "text": "bánh mì bột mì men nở",
            },
        ]
        results = bm25_search("cơ cấu", chunks, candidate_k=2)
        self.assertEqual(results[0]["chunk_id"], "MATCH")


# ──────────────────────────────────────────────────────────────────────────────
# 4. Exact legal term xếp trên đoạn không chứa từ khóa
# ──────────────────────────────────────────────────────────────────────────────
class TestBM25Ranking(unittest.TestCase):

    def _make_chunks(self):
        return [
            {
                "chunk_id": "LEGAL", "strategy": "fixed-size",
                "source": "legal.pdf", "page_start": 1, "page_end": 1,
                "text": "Điều 15 Khoản 1 quy định về lãi suất cho vay theo cung cầu vốn thị trường",
            },
            {
                "chunk_id": "UNRELATED", "strategy": "fixed-size",
                "source": "other.pdf", "page_start": 5, "page_end": 5,
                "text": "Công thức làm bánh mì bột mì men nở nước ấm muối biển",
            },
        ]

    def test_exact_term_ranked_higher(self):
        """Chunk chứa thuật ngữ pháp lý phải xếp trước chunk ngoài phạm vi."""
        chunks = self._make_chunks()
        results = bm25_search("lãi suất cho vay Điều 15", chunks, candidate_k=2)
        chunk_ids = [r["chunk_id"] for r in results]
        self.assertEqual(chunk_ids[0], "LEGAL")

    def test_full_fixture_ranking(self):
        """Test với fixture thực tế: query 'Điều 3 Khoản 1' phải xếp ADV_01 hoặc ADV_02 đầu."""
        chunks = _load_fixture_chunks()
        results = bm25_search("Điều 3 Khoản 1 Thông tư 02/2023/TT-NHNN cơ cấu lại thời hạn trả nợ", chunks, candidate_k=5)
        top_ids = [r["chunk_id"] for r in results[:2]]
        self.assertTrue(
            "ADV_01" in top_ids or "ADV_02" in top_ids,
            f"Kỳ vọng ADV_01 hoặc ADV_02 trong top-2, nhận: {top_ids}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# 5. candidate_k lớn hơn corpus vẫn chạy
# ──────────────────────────────────────────────────────────────────────────────
class TestCandidateKClamp(unittest.TestCase):

    def test_k_larger_than_corpus(self):
        """candidate_k = 1000 với corpus 2 chunk phải trả 2 kết quả (không crash)."""
        chunks = [
            {
                "chunk_id": "X1", "strategy": "fixed-size",
                "source": "a.pdf", "page_start": 1, "page_end": 1,
                "text": "tổ chức tín dụng lãi suất",
            },
            {
                "chunk_id": "X2", "strategy": "fixed-size",
                "source": "b.pdf", "page_start": 1, "page_end": 1,
                "text": "ngân hàng thương mại",
            },
        ]
        results = bm25_search("lãi suất", chunks, candidate_k=1000)
        self.assertEqual(len(results), 2)

    def test_k_equals_one(self):
        """candidate_k = 1 phải trả đúng 1 kết quả."""
        chunks = _load_fixture_chunks()
        results = bm25_search("lãi suất", chunks, candidate_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["bm25_rank"], 1)

    def test_all_results_have_required_fields(self):
        """Tất cả kết quả phải có đủ 7 field theo contract."""
        required_fields = {"chunk_id", "text", "source", "page_start", "page_end", "bm25_rank", "bm25_score"}
        chunks = _load_fixture_chunks()
        results = bm25_search("tổ chức tín dụng", chunks, candidate_k=5)
        for r in results:
            self.assertEqual(set(r.keys()) & required_fields, required_fields, f"Thiếu field: {r}")


# ──────────────────────────────────────────────────────────────────────────────
# 6. Empty question fail
# ──────────────────────────────────────────────────────────────────────────────
class TestEmptyQuestion(unittest.TestCase):

    def _chunks(self):
        return _load_fixture_chunks()

    def test_empty_string_raises(self):
        """Câu hỏi rỗng phải raise ValueError."""
        with self.assertRaises(ValueError):
            bm25_search("", self._chunks(), candidate_k=5)

    def test_whitespace_only_raises(self):
        """Câu hỏi chỉ có khoảng trắng phải raise ValueError."""
        with self.assertRaises(ValueError):
            bm25_search("   \t\n  ", self._chunks(), candidate_k=5)

    def test_non_string_raises(self):
        """Câu hỏi không phải string phải raise ValueError."""
        with self.assertRaises(ValueError):
            bm25_search(None, self._chunks(), candidate_k=5)

    def test_only_punctuation_raises(self):
        """Câu hỏi chỉ là dấu câu (không có token) phải raise ValueError."""
        with self.assertRaises(ValueError):
            bm25_search(",,, ... ???", self._chunks(), candidate_k=5)

    def test_empty_corpus_raises(self):
        """Corpus rỗng phải raise ValueError."""
        with self.assertRaises(ValueError):
            bm25_search("lãi suất", [], candidate_k=5)


# ──────────────────────────────────────────────────────────────────────────────
# 7. Tie-break deterministic
# ──────────────────────────────────────────────────────────────────────────────
class TestTieBreak(unittest.TestCase):

    def test_tiebreak_same_score_uses_chunk_id_order(self):
        """Khi hai chunk có cùng score, chunk_id nhỏ hơn phải xếp trước."""
        # Dùng văn bản giống nhau để đảm bảo score bằng nhau
        same_text = "tổ chức tín dụng ngân hàng thương mại"
        chunks = [
            {
                "chunk_id": "ZZZ", "strategy": "fixed-size",
                "source": "a.pdf", "page_start": 1, "page_end": 1,
                "text": same_text,
            },
            {
                "chunk_id": "AAA", "strategy": "fixed-size",
                "source": "b.pdf", "page_start": 1, "page_end": 1,
                "text": same_text,
            },
        ]
        results = bm25_search("tổ chức tín dụng", chunks, candidate_k=2)
        self.assertEqual(results[0]["chunk_id"], "AAA")
        self.assertEqual(results[1]["chunk_id"], "ZZZ")

    def test_tiebreak_stable_across_multiple_runs(self):
        """Kết quả tie-break phải ổn định qua nhiều lần gọi."""
        same_text = "lãi suất cho vay tổ chức tín dụng"
        chunks = [
            {
                "chunk_id": f"C{i:03d}", "strategy": "fixed-size",
                "source": "x.pdf", "page_start": 1, "page_end": 1,
                "text": same_text,
            }
            for i in range(5, 0, -1)  # tạo thứ tự ngẫu nhiên
        ]
        results_1 = bm25_search("lãi suất", chunks, candidate_k=5)
        results_2 = bm25_search("lãi suất", chunks, candidate_k=5)
        ids_1 = [r["chunk_id"] for r in results_1]
        ids_2 = [r["chunk_id"] for r in results_2]
        self.assertEqual(ids_1, ids_2)
        # Phải sắp xếp theo chunk_id tăng dần khi score bằng nhau
        self.assertEqual(ids_1, sorted(ids_1))

    def test_rank_sequential(self):
        """bm25_rank phải liên tiếp từ 1."""
        chunks = _load_fixture_chunks()
        results = bm25_search("tổ chức tín dụng lãi suất", chunks, candidate_k=5)
        ranks = [r["bm25_rank"] for r in results]
        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))


# ──────────────────────────────────────────────────────────────────────────────
# 8. Không gọi Gemini/Chroma/reranker
# ──────────────────────────────────────────────────────────────────────────────
class TestNoExternalCalls(unittest.TestCase):

    def test_bm25_search_does_not_import_google_genai(self):
        """bm25_search không được import google.genai trong quá trình thực thi."""
        import advanced_rag as arag
        import inspect
        source = inspect.getsource(arag.bm25_search)
        self.assertNotIn("google.genai", source)
        self.assertNotIn("genai.Client", source)

    def test_bm25_search_does_not_import_chromadb(self):
        """bm25_search không được import chromadb."""
        import advanced_rag as arag
        import inspect
        source = inspect.getsource(arag.bm25_search)
        self.assertNotIn("chromadb", source)

    def test_build_index_does_not_import_transformers(self):
        """build_bm25_index không được gọi transformers/torch."""
        import advanced_rag as arag
        import inspect
        source = inspect.getsource(arag.build_bm25_index)
        self.assertNotIn("transformers", source)
        self.assertNotIn("AutoModel", source)
        self.assertNotIn("AutoTokenizer", source)

    def test_bm25_search_no_network_calls(self):
        """bm25_search chạy hoàn toàn offline với fixture thực tế."""
        chunks = _load_fixture_chunks()
        # Nếu có network call thì test này sẽ treo hoặc lỗi
        results = bm25_search("Điều 3 Khoản 1 cơ cấu lại thời hạn trả nợ", chunks, candidate_k=5)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()
