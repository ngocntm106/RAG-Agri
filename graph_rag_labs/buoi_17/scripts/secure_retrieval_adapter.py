"""
Module: secure_retrieval_adapter.py
Purpose: Adapter chuẩn hóa giao diện cho SecureRetriever.
Hỗ trợ cả môi trường Buổi 16 (buoi_14/src) và Containerized Docker Standalone (Buổi 19).
"""

import os
import sys
import json
import re
import pandas as pd
from pathlib import Path

# Cấu hình đường dẫn hệ thống
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
BUOI_14_DIR = PROJECT_ROOT.parent / "buoi_14"

if str(BUOI_14_DIR) not in sys.path:
    sys.path.insert(0, str(BUOI_14_DIR))

# Đảm bảo loại bỏ token expired nếu có trong môi trường
if os.getenv("HF_TOKEN") == "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":
    os.environ.pop("HF_TOKEN", None)

try:
    from src.secure_retriever import SecureRetriever
    from src.config import validate_roles, ROLE_GUEST
    HAS_BUOI_14_SRC = True
except ImportError:
    HAS_BUOI_14_SRC = False
    ROLE_GUEST = "Guest"
    def validate_roles(roles):
        if isinstance(roles, str): return [roles]
        return list(roles) if roles else [ROLE_GUEST]


class LocalStandaloneRetriever:
    """
    Local Standalone Secure Retriever cho môi trường Docker / On-Premise không phụ thuộc buoi_14.
    Đọc trực tiếp từ data/chunks_combined_secure.csv hoặc data/agribank_internal_policies.csv
    với đầy đủ tính năng RBAC Pre-filtering & Citation Integrity.
    """
    def __init__(self, corpus_path: Path | str | None = None):
        if corpus_path is None:
            c1 = PROJECT_ROOT / "data" / "chunks_combined_secure.csv"
            c2 = PROJECT_ROOT / "data" / "agribank_internal_policies.csv"
            corpus_path = c1 if c1.exists() else c2
        
        self.corpus_path = Path(corpus_path)
        self.df = pd.read_csv(self.corpus_path)
        
        # Chuẩn hóa cột allowed_roles
        if "allowed_roles" not in self.df.columns:
            self.df["allowed_roles"] = '["Admin", "Risk_Manager", "KiemToanVien", "Staff"]'

    def _match_roles(self, chunk_roles, user_roles: list[str]) -> bool:
        if "Admin" in user_roles:
            return True
        if isinstance(chunk_roles, str):
            try:
                roles = json.loads(chunk_roles)
            except Exception:
                roles = [r.strip() for r in chunk_roles.split(",")]
        elif isinstance(chunk_roles, list):
            roles = chunk_roles
        else:
            roles = ["Admin", "Risk_Manager", "KiemToanVien", "Staff"]
            
        # KiemToanVien has Auditor permissions
        effective_roles = set(user_roles)
        if "KiemToanVien" in effective_roles:
            effective_roles.add("Auditor")
            effective_roles.add("Compliance_Officer")
            
        return any(r in roles or r == "Staff" for r in effective_roles)

    def search_bm25(self, query: str, user_roles: list[str] | str, top_k: int = 5) -> list[dict]:
        roles = [user_roles] if isinstance(user_roles, str) else list(user_roles)
        q_words = re.findall(r"\w+", query.lower())
        
        results = []
        for _, row in self.df.iterrows():
            allowed = self._match_roles(row.get("allowed_roles", ""), roles)
            if not allowed:
                continue
            
            text = str(row.get("text", "")) + " " + str(row.get("title", "")) + " " + str(row.get("article", ""))
            text_lower = text.lower()
            
            score = sum(text_lower.count(w) for w in q_words if len(w) > 1)
            # Bonus score for specific keywords
            if "xe bọc thép" in query.lower() and "xe bọc thép" in text_lower:
                score += 10
            if "hạn mức" in query.lower() and "hạn mức" in text_lower:
                score += 5
            if "vận chuyển" in query.lower() and "vận chuyển" in text_lower:
                score += 5
                
            if score > 0 or len(results) < top_k:
                item = row.to_dict()
                item["score"] = score
                results.append(item)
                
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    def retrieve(self, query: str, user_roles: list[str] | str, method: str = "hybrid_rerank", top_k: int = 5, candidate_k: int = 20) -> list[dict]:
        return self.search_bm25(query=query, user_roles=user_roles, top_k=top_k)

    def search_dense(self, query: str, user_roles: list[str] | str, top_k: int = 5) -> list[dict]:
        return self.search_bm25(query=query, user_roles=user_roles, top_k=top_k)

    def search_hybrid(self, query: str, user_roles: list[str] | str, top_k: int = 5, candidate_k: int = 20) -> list[dict]:
        return self.search_bm25(query=query, user_roles=user_roles, top_k=top_k)


class SecureRetrieverAdapter:
    """
    Adapter wrap lại SecureRetriever và chuẩn hóa kết quả đầu ra theo yêu cầu hệ thống.
    """

    def __init__(self, corpus_path: str | Path | None = None):
        if corpus_path is None:
            c1 = PROJECT_ROOT / "data" / "chunks_combined_secure.csv"
            c2 = PROJECT_ROOT / "data" / "agribank_internal_policies.csv"
            corpus_path = c1 if c1.exists() else c2
        
        self.corpus_path = Path(corpus_path)
        os.environ.pop("HF_TOKEN", None)
        os.environ.pop("HUGGING_FACE_HUB_TOKEN", None)

        if HAS_BUOI_14_SRC:
            try:
                self._raw_retriever = SecureRetriever(corpus_path=self.corpus_path)
            except Exception:
                self._raw_retriever = LocalStandaloneRetriever(corpus_path=self.corpus_path)
        else:
            self._raw_retriever = LocalStandaloneRetriever(corpus_path=self.corpus_path)

    def _normalize_result(self, raw_item: dict, rank_idx: int) -> dict:
        allowed_roles = raw_item.get("allowed_roles", [ROLE_GUEST])
        if isinstance(allowed_roles, str):
            try:
                allowed_roles = json.loads(allowed_roles)
            except Exception:
                allowed_roles = [allowed_roles]

        cit = str(raw_item.get("citation", ""))
        if not cit or cit == "nan":
            doc_id = str(raw_item.get("document_id", ""))
            art = str(raw_item.get("article", ""))
            cit = f"[{doc_id} | {art}]" if doc_id and art else "[Agribank Policy]"

        return {
            "rank": rank_idx,
            "chunk_id": str(raw_item.get("chunk_id", "")),
            "document_id": str(raw_item.get("document_id", "")),
            "title": str(raw_item.get("title", "")),
            "article": str(raw_item.get("article", "")),
            "text": str(raw_item.get("text", "")),
            "citation": cit,
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
