"""
Module: secure_retrieval.py
Purpose: Adapter cho Buổi 17 để tái sử dụng 100% SecureRetriever từ Buổi 16 (buoi_14/src/secure_retriever.py).
Không sửa đổi hay sao chép lại mã nguồn của Buổi 16.
"""

import os
import sys
from pathlib import Path

# Cấu hình đường dẫn tới root dự án và buoi_14
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
BUOI_14_DIR = PROJECT_ROOT / "buoi_14"

# Nạp buoi_14 vào sys.path để import trực tiếp SecureRetriever
if str(BUOI_14_DIR) not in sys.path:
    sys.path.insert(0, str(BUOI_14_DIR))

# Xử lý token HuggingFace môi trường nếu token bị hết hạn
if os.getenv("HF_TOKEN") == "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":
    os.environ.pop("HF_TOKEN", None)

try:
    from src.secure_retriever import SecureRetriever
    from src.config import VALID_ROLES, ROLE_GUEST, validate_roles
except ImportError as e:
    raise ImportError(f"[Adapter Buổi 17] Không thể nạp SecureRetriever từ {BUOI_14_DIR}: {e}")


class SecureRetrieverAdapter:
    """
    Adapter wrapper cho SecureRetriever nhằm cung cấp interface chuẩn hóa cho Buổi 17
    (Use Case 1: Tra cứu quy định nội bộ phân quyền & Use Case 2: AI Compliance Gap).
    """

    def __init__(self, corpus_path: str | Path | None = None):
        if corpus_path is None:
            corpus_path = BUOI_14_DIR / "data" / "processed" / "chunks_secure.csv"
        
        self.corpus_path = Path(corpus_path)
        self._retriever = SecureRetriever(corpus_path=self.corpus_path)

    def retrieve(
        self,
        query: str,
        user_roles: list[str] | str,
        method: str = "hybrid_rerank",
        top_k: int = 5,
        candidate_k: int = 20
    ) -> list[dict]:
        """
        Gửi yêu cầu truy xuất tới SecureRetriever gốc.
        Đảm bảo RBAC Pre-Filtering được thực thi nghiêm ngặt trước khi trả về dữ liệu.
        """
        return self._retriever.retrieve(
            query=query,
            user_roles=user_roles,
            method=method,
            top_k=top_k,
            candidate_k=candidate_k
        )

    def search_bm25(self, query: str, user_roles: list[str] | str, top_k: int = 5) -> list[dict]:
        return self._retriever.search_bm25(query=query, user_roles=user_roles, top_k=top_k)

    def search_dense(self, query: str, user_roles: list[str] | str, top_k: int = 5) -> list[dict]:
        return self._retriever.search_dense(query=query, user_roles=user_roles, top_k=top_k)

    def search_hybrid(self, query: str, user_roles: list[str] | str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
        return self._retriever.search_hybrid(query=query, user_roles=user_roles, top_k=top_k, candidate_k=candidate_k)


def get_secure_retriever(corpus_path: str | Path | None = None) -> SecureRetrieverAdapter:
    """Hàm helper để khởi tạo Adapter cho Buổi 17."""
    return SecureRetrieverAdapter(corpus_path=corpus_path)
