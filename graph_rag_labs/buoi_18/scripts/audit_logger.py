"""
Module: audit_logger.py
Purpose: Ghi vết kiểm toán (Audit Trail) cho toàn bộ request tra cứu RAG và RBAC trong Buổi 17.
Định dạng lưu trữ: JSON Lines (jsonl).
"""

import os
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "outputs" / "audit_log.jsonl"


class AuditLogger:
    """
    Quản lý ghi log kiểm toán an ninh cho hệ thống RAG RBAC.
    """

    def __init__(self, log_path: str | Path | None = None):
        if log_path is None:
            log_path = DEFAULT_LOG_PATH
        
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _sanitize_dict(self, data: dict) -> dict:
        """Loại bỏ thông tin nhạy cảm (passwords, API keys, secrets) trước khi ghi log."""
        sensitive_keys = {"password", "api_key", "secret", "token", "hf_token", "neo4j_password"}
        sanitized = {}
        for k, v in data.items():
            if k.lower() in sensitive_keys or any(sk in k.lower() for sk in sensitive_keys):
                sanitized[k] = "***REDACTED***"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    def log_request(
        self,
        user_id_demo: str,
        user_role: str | list[str],
        query: str,
        action: str = "RETRIEVAL_QUERY",
        retrieval_method: str = "Hybrid + Rerank (Secure)",
        retrieved_items: list[dict] | None = None,
        rbac_blocked_count: int = 0,
        status: str = "SUCCESS",
        request_id: str | None = None,
        error_message: str | None = None
    ) -> dict:
        """
        Ghi một sự kiện kiểm toán (Audit Event) vào tệp audit_log.jsonl.
        """
        if request_id is None:
            request_id = str(uuid.uuid4())

        if retrieved_items is None:
            retrieved_items = []

        # Chuẩn hóa user_role
        if isinstance(user_role, list):
            roles_list = user_role
        else:
            roles_list = [user_role]

        # Trích xuất danh sách IDs từ retrieved_items
        doc_ids = list(dict.fromkeys([str(item.get("document_id", "")) for item in retrieved_items if item.get("document_id")]))
        chunk_ids = [str(item.get("chunk_id", "")) for item in retrieved_items if item.get("chunk_id")]
        citations = [str(item.get("citation", "")) for item in retrieved_items if item.get("citation")]

        # Tạo record audit
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "user_id_demo": user_id_demo,
            "user_role": roles_list,
            "action": action,
            "query": query,
            "retrieval_method": retrieval_method,
            "retrieved_document_ids": doc_ids,
            "retrieved_chunk_ids": chunk_ids,
            "citation_ids": citations,
            "rbac_blocked_count": rbac_blocked_count,
            "status": status
        }

        if error_message:
            event["error_message"] = error_message

        # Lọc thông tin nhạy cảm
        safe_event = self._sanitize_dict(event)

        # Ghi append vào file JSONL
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(safe_event, ensure_ascii=False) + "\n")

        return safe_event


def get_audit_logger(log_path: str | Path | None = None) -> AuditLogger:
    """Helper factory function cho AuditLogger."""
    return AuditLogger(log_path=log_path)
