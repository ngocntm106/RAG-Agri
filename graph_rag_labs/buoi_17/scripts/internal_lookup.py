"""
Module: internal_lookup.py
Purpose: Use Case 1 - AI Tra cứu quy định nội bộ có phân quyền RBAC và ghi nhật ký kiểm toán (Audit Trail).
Dự án: Buổi 17 - RBAC, Audit Trail và AI Compliance Gap Checker.
"""

import os
import sys
import json
import uuid
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from buoi_17.scripts.secure_retrieval_adapter import SecureRetrieverAdapter
from buoi_17.scripts.audit_logger import AuditLogger

# Khởi tạo singleton instances
_adapter_instance = None
_logger_instance = None


def get_adapter() -> SecureRetrieverAdapter:
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = SecureRetrieverAdapter()
    return _adapter_instance


def get_logger() -> AuditLogger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AuditLogger()
    return _logger_instance


def generate_llm_answer(question: str, context_chunks: list[dict]) -> str:
    """
    Sinh câu trả lời RAG dựa tuyệt đối trên ngữ cảnh đã qua lọc RBAC.
    Đảm bảo nguyên tắc:
    - Nếu không có chunk hợp lệ -> Trả về thông báo chuẩn.
    - Không tự bịa thông tin ngoài ngữ cảnh.
    - Trích dẫn chính xác nguồn từ citation.
    """
    if not context_chunks:
        return "Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập."

    # Kiểm tra xem có thể gọi Gemini API nếu có API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if api_key and api_key != "YOUR_GEMINI_API_KEY_FREE":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
            model = genai.GenerativeModel(model_name)
            
            context_str = "\n\n".join([f"[{c['citation']}]\n{c['text']}" for c in context_chunks])
            prompt = f"""Bạn là Trợ lý AI tra cứu quy định nội bộ Agribank.
Nhiệm vụ của bạn là trả lời câu hỏi dựa TUYỆT ĐỐI VÀ CHỈ DỰA VÀO ngữ cảnh tài liệu được cung cấp dưới đây.

YÊU CẦU BẮT BUỘC:
1. Chỉ sử dụng thông tin có trong ngữ cảnh. Không suy diễn hoặc dùng kiến thức bên ngoài.
2. Với mỗi ý trả lời, BẮT BUỘC ghi rõ trích dẫn tương ứng dạng [tên_trích_dẫn].
3. Nếu ngữ cảnh không chứa đủ thông tin để trả lời, BẮT BUỘC trả về câu: 'Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập.'

NGỮ CẢNH TÀI LIỆU ĐÃ QUA LỌC RBAC:
{context_str}

CÂU HỎI: {question}

CÂU TRẢ LỜI:"""
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"[InternalLookup] Gọi Gemini API lỗi ({e}), chuyển sang chế độ Grounded Synthesizer...")

    # Chế độ Grounded Synthesizer (Fallback an toàn tuyệt đối khi không có API key)
    citations_used = []
    answer_bullets = []
    for c in context_chunks:
        cit = c.get("citation", "")
        text_snippet = c.get("text", "").strip()
        if len(text_snippet) > 200:
            text_snippet = text_snippet[:200] + "..."
        answer_bullets.append(f"- {text_snippet} [{cit}]")
        if cit:
            citations_used.append(cit)

    summary = (
        f"Căn cứ theo các quy định nội bộ được phép truy cập cho vai trò của bạn, "
        f"hệ thống ghi nhận thông tin liên quan đến câu hỏi '{question}':\n\n"
        + "\n".join(answer_bullets)
    )
    return summary


def internal_policy_lookup(
    question: str,
    user_role: str | list[str],
    top_k: int = 5,
    user_id_demo: str = "demo_user"
) -> dict:
    """
    Hàm chính cho Use Case 1: Tra cứu quy định nội bộ phân quyền RBAC.
    
    Returns dict:
        - question
        - user_role
        - answer
        - citations
        - document_ids
        - chunk_ids
        - access_scope
        - request_id
        - status
    """
    request_id = str(uuid.uuid4())
    adapter = get_adapter()
    logger = get_logger()

    # Chuẩn hóa user_role
    if isinstance(user_role, str):
        roles_list = [user_role]
    else:
        roles_list = list(user_role)

    # 1. Lấy ngữ cảnh qua SecureRetriever Adapter (Pre-Filtering RBAC)
    retrieved_chunks = adapter.retrieve(
        query=question,
        user_roles=roles_list,
        method="hybrid_rerank",
        top_k=top_k
    )

    # Đếm số chunk bị rào cản RBAC
    raw_bm25_admin = adapter._raw_retriever.search_bm25(query=question, user_roles=["Admin"], top_k=20)
    blocked_count = sum(
        1 for c in raw_bm25_admin 
        if not any(r in c.get("allowed_roles", []) for r in roles_list)
    )

    # 2. Kiểm tra quyền truy cập và sinh câu trả lời
    if not retrieved_chunks:
        answer = "Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập."
        status = "DENIED" if blocked_count > 0 else "SUCCESS"
        citations = []
        doc_ids = []
        chunk_ids = []
    else:
        answer = generate_llm_answer(question, retrieved_chunks)
        status = "SUCCESS"
        citations = list(dict.fromkeys([c["citation"] for c in retrieved_chunks if c.get("citation")]))
        doc_ids = list(dict.fromkeys([c["document_id"] for c in retrieved_chunks if c.get("document_id")]))
        chunk_ids = [c["chunk_id"] for c in retrieved_chunks if c.get("chunk_id")]

    # 3. Ghi vết kiểm toán (Audit Trail Log)
    logger.log_request(
        user_id_demo=user_id_demo,
        user_role=roles_list,
        query=question,
        action="INTERNAL_POLICY_LOOKUP",
        retrieval_method="Hybrid + Rerank (Secure)",
        retrieved_items=retrieved_chunks,
        rbac_blocked_count=blocked_count,
        status=status,
        request_id=request_id
    )

    access_scope = f"Scope [{', '.join(roles_list)}]"

    return {
        "request_id": request_id,
        "question": question,
        "user_role": roles_list,
        "access_scope": access_scope,
        "answer": answer,
        "citations": citations,
        "document_ids": doc_ids,
        "chunk_ids": chunk_ids,
        "retrieved_document_ids": doc_ids,
        "retrieved_chunk_ids": chunk_ids,
        "status": status,
        "rbac_blocked_count": blocked_count
    }


if __name__ == "__main__":
    # Chạy thử nghiệm nhanh
    demo_res = internal_policy_lookup(
        question="quy định về tuyển dụng và nâng lương cán bộ",
        user_role="HR",
        user_id_demo="usr_hr_test"
    )
    print("=== DEMO RUN RESULT ===")
    print("Request ID:", demo_res["request_id"])
    print("Answer:\n", demo_res["answer"])
    print("Citations:", demo_res["citations"])
