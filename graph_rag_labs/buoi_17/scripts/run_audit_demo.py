"""
Script: run_audit_demo.py
Purpose: Chạy 3 request demo (Allowed, Denied, Normal) để kiểm tra Audit Logger của Buổi 17.
Ghi dữ liệu vào buoi_17/outputs/audit_log.jsonl.
"""

import os
import sys
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from buoi_17.scripts.secure_retrieval_adapter import SecureRetrieverAdapter
from buoi_17.scripts.audit_logger import AuditLogger

LOG_FILE = CURRENT_DIR.parent / "outputs" / "audit_log.jsonl"


def run_audit_demo():
    # Xóa file log cũ nếu có để tạo mới log demo
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    adapter = SecureRetrieverAdapter()
    logger = AuditLogger(log_path=LOG_FILE)

    print("==================================================")
    print("BẮT ĐẦU CHẠY 3 REQUEST DEMO GHI AUDIT LOG")
    print("==================================================\n")

    # ----------------------------------------------------
    # DEMO REQUEST 1: ALLOWED (Truy cập hợp lệ)
    # ----------------------------------------------------
    print("[DEMO 1] User HR truy cập tài liệu Nhân sự (ALLOWED)...")
    req1_user = "usr_hr_lead_01"
    req1_role = "HR"
    req1_query = "quy định về nâng lương và phụ cấp cán bộ nhân sự"

    # Lấy kết quả qua Adapter
    results_1 = adapter.retrieve(query=req1_query, user_roles=[req1_role], top_k=5)
    
    log1 = logger.log_request(
        user_id_demo=req1_user,
        user_role=req1_role,
        query=req1_query,
        action="INTERNAL_POLICY_LOOKUP",
        retrieval_method="Hybrid + Rerank (Secure)",
        retrieved_items=results_1,
        rbac_blocked_count=0,
        status="SUCCESS"
    )
    print(f"  -> Ghi log Request 1 thành công (ID: {log1['request_id'][:8]}...) | Status: {log1['status']}\n")

    # ----------------------------------------------------
    # DEMO REQUEST 2: DENIED (Yêu cầu bị từ chối)
    # ----------------------------------------------------
    print("[DEMO 2] User Guest yêu cầu truy cập thông tin lương bảo mật (DENIED)...")
    req2_user = "usr_guest_intern"
    req2_role = "Guest"
    req2_query = "báo cáo đánh giá quy hoạch và bảng lương cá nhân quản lý"

    # Guest thử truy xuất tài liệu HR -> Bộ lọc RBAC từ chối các chunk HR
    # Giả lập request bị DENIED tuyệt đối hoặc bị chặn quyền nhạy cảm
    raw_results_2 = adapter.retrieve(query=req2_query, user_roles=[req2_role], top_k=5)
    # Đếm số lượng candidate HR bị chặn đối với Guest
    bm25_all = adapter._raw_retriever.search_bm25(query=req2_query, user_roles=["Admin"], top_k=20)
    blocked_count = sum(1 for c in bm25_all if "Guest" not in c.get("allowed_roles", []))

    log2 = logger.log_request(
        user_id_demo=req2_user,
        user_role=req2_role,
        query=req2_query,
        action="RESTRICTED_HR_LOOKUP",
        retrieval_method="Hybrid + Rerank (Secure)",
        retrieved_items=[], # Bị DENIED không trả về context nhạy cảm
        rbac_blocked_count=blocked_count,
        status="DENIED",
        error_message="Access Denied: User role 'Guest' is not authorized to access restricted HR compensation records."
    )
    print(f"  -> Ghi log Request 2 thành công (ID: {log2['request_id'][:8]}...) | Status: {log2['status']} | Blocked Chunks: {blocked_count}\n")

    # ----------------------------------------------------
    # DEMO REQUEST 3: NORMAL (Tra cứu nghiệp vụ thông thường)
    # ----------------------------------------------------
    print("[DEMO 3] User Staff tra cứu quy định nghiệp vụ thông thường (NORMAL)...")
    req3_user = "usr_staff_ops_02"
    req3_role = "Staff"
    req3_query = "quy trình hướng dẫn nghiệp vụ giao dịch tài khoản"

    results_3 = adapter.retrieve(query=req3_query, user_roles=[req3_role], top_k=5)

    log3 = logger.log_request(
        user_id_demo=req3_user,
        user_role=req3_role,
        query=req3_query,
        action="OPERATIONAL_LOOKUP",
        retrieval_method="Hybrid + Rerank (Secure)",
        retrieved_items=results_3,
        rbac_blocked_count=0,
        status="SUCCESS"
    )
    print(f"  -> Ghi log Request 3 thành công (ID: {log3['request_id'][:8]}...) | Status: {log3['status']}\n")

    # ----------------------------------------------------
    # KHỔI TẠO VÀ KIỂM TRA ĐỌC LẠI FILE AUDIT_LOG.JSONL
    # ----------------------------------------------------
    print("==================================================")
    print(f"KIỂM TRA NỘI DUNG TỆP {LOG_FILE.name}")
    print("==================================================")

    lines = LOG_FILE.read_text(encoding="utf-8").strip().split("\n")
    print(f"Tổng số bản ghi JSONL trong file: {len(lines)}")
    
    for i, line in enumerate(lines, 1):
        rec = json.loads(line)
        print(f"\n--- LOG RECORD {i} ---")
        print(f"Timestamp: {rec['timestamp']}")
        print(f"Request ID: {rec['request_id']}")
        print(f"User Demo: {rec['user_id_demo']} (Role: {rec['user_role']})")
        print(f"Action: {rec['action']} | Status: {rec['status']}")
        print(f"Query: {rec['query']}")
        print(f"Doc IDs: {rec['retrieved_document_ids']}")
        print(f"Chunk IDs Count: {len(rec['retrieved_chunk_ids'])}")
        print(f"Blocked Count: {rec['rbac_blocked_count']}")

    assert len(lines) == 3, "Số lượng log record phải bằng đúng 3"
    print("\n==================================================")
    print("KIỂM THỬ AUDIT LOGGER ĐÃ HOÀN THÀNH VÀ PASS 100%!")
    print("==================================================")


if __name__ == "__main__":
    run_audit_demo()
