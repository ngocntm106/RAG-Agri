"""
Module: secure_retrieval_adapter.py
Purpose: Adapter chuẩn hóa giao diện cho SecureRetriever từ Buổi 16 (buoi_14/src/secure_retriever.py) cho Buổi 17.
Không sửa mã nguồn Buổi 16, không tạo retriever mới.
"""

import os
import sys
from pathlib import Path

# Cấu hình đường dẫn hệ thống để gọi module buoi_14
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
BUOI_14_DIR = PROJECT_ROOT / "buoi_14"

if str(BUOI_14_DIR) not in sys.path:
    sys.path.insert(0, str(BUOI_14_DIR))

# Đảm bảo loại bỏ token expired nếu có trong môi trường
if os.getenv("HF_TOKEN") == "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":
    os.environ.pop("HF_TOKEN", None)

try:
    from src.secure_retriever import SecureRetriever
    from src.config import validate_roles, ROLE_GUEST
except ImportError as e:
    raise ImportError(f"[SecureRetrieverAdapter] Không thể nạp SecureRetriever từ {BUOI_14_DIR}: {e}")


class SecureRetrieverAdapter:
    """
    Adapter wrap lại SecureRetriever cũ và chuẩn hóa kết quả đầu ra theo yêu cầu Buổi 17:
    - rank
    - chunk_id
    - document_id
    - title
    - article
    - citation
    - allowed_roles
    - access_decision ('ALLOWED')
    - retrieval_method
    """

    def __init__(self, corpus_path: str | Path | None = None):
        if corpus_path is None:
            corpus_path = BUOI_14_DIR / "data" / "processed" / "chunks_secure.csv"
        
        self.corpus_path = Path(corpus_path)
        # Clear token hết hạn trong os.environ trước khi nạp model
        os.environ.pop("HF_TOKEN", None)
        os.environ.pop("HUGGING_FACE_HUB_TOKEN", None)
        self._raw_retriever = SecureRetriever(corpus_path=self.corpus_path)

    def _normalize_result(self, raw_item: dict, rank_idx: int) -> dict:
        """
        Chuẩn hóa dictionary kết quả của một chunk theo schema bắt buộc của Buổi 17.
        """
        allowed_roles = raw_item.get("allowed_roles", [ROLE_GUEST])
        if isinstance(allowed_roles, str):
            import json
            try:
                allowed_roles = json.loads(allowed_roles)
            except Exception:
                allowed_roles = [allowed_roles]

        return {
            "rank": rank_idx,
            "chunk_id": str(raw_item.get("chunk_id", "")),
            "document_id": str(raw_item.get("document_id", "")),
            "title": str(raw_item.get("title", "")),
            "article": str(raw_item.get("article", "")),
            "text": str(raw_item.get("text", "")),
            "citation": str(raw_item.get("citation", "")),
            "allowed_roles": allowed_roles,
            "access_decision": "ALLOWED",
            "retrieval_method": str(raw_item.get("retrieval_method", "Secure Hybrid"))
        }

    def retrieve(
        self,
        query: str,
        user_roles: list[str] | str,
        method: str = "hybrid_rerank",
        top_k: int = 5,
        candidate_k: int = 20
    ) -> list[dict]:
        """
        Hàm retrieval chính chuẩn hóa 100% đầu ra.
        """
        raw_results = self._raw_retriever.retrieve(
            query=query,
            user_roles=user_roles,
            method=method,
            top_k=top_k,
            candidate_k=candidate_k
        )
        
        normalized = []
        for idx, item in enumerate(raw_results, 1):
            normalized.append(self._normalize_result(item, idx))
        return normalized

    def search_bm25(self, query: str, user_roles: list[str] | str, top_k: int = 5) -> list[dict]:
        raw_results = self._raw_retriever.search_bm25(query=query, user_roles=user_roles, top_k=top_k)
        return [self._normalize_result(item, idx) for idx, item in enumerate(raw_results, 1)]

    def search_dense(self, query: str, user_roles: list[str] | str, top_k: int = 5) -> list[dict]:
        raw_results = self._raw_retriever.search_dense(query=query, user_roles=user_roles, top_k=top_k)
        return [self._normalize_result(item, idx) for idx, item in enumerate(raw_results, 1)]

    def search_hybrid(self, query: str, user_roles: list[str] | str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
        raw_results = self._raw_retriever.search_hybrid(query=query, user_roles=user_roles, top_k=top_k, candidate_k=candidate_k)
        return [self._normalize_result(item, idx) for idx, item in enumerate(raw_results, 1)]


def get_adapter(corpus_path: str | Path | None = None) -> SecureRetrieverAdapter:
    """Factory function khởi tạo adapter."""
    return SecureRetrieverAdapter(corpus_path=corpus_path)
