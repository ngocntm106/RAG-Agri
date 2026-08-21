"""
Script: test_adapter.py
Purpose: Kiểm thử 4 điều kiện an toàn RBAC của SecureRetrieverAdapter cho Buổi 17.
"""

import os
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from buoi_17.scripts.secure_retrieval_adapter import SecureRetrieverAdapter


def run_verification_tests():
    adapter = SecureRetrieverAdapter()
    # Tìm kiếm với câu hỏi nhắm trực tiếp vào văn bản quy định nhân sự bảo mật
    query = "chế độ nâng lương bổ nhiệm và phụ cấp nhân sự"

    print("==================================================")
    print("CHẠY THỬ NGHIỆM KIỂM THỬ AN TOÀN RBAC CHUYÊN SÂU")
    print("==================================================\n")

    # 1. Role HR (Authorized)
    hr_results = adapter.retrieve(query=query, user_roles=["HR"], top_k=5)
    print(f"[TEST 1] Role HR nhận được {len(hr_results)} chunks.")
    
    # Lấy chunk giới hạn riêng cho HR (không công khai cho Staff/Guest)
    hr_only_chunks = [c for c in hr_results if "Guest" not in c["allowed_roles"] and "Staff" not in c["allowed_roles"]]
    if not hr_only_chunks:
        # Nếu top 5 chưa có chunk nhạy cảm HR, lấy trực tiếp qua BM25 HR
        bm25_hr = adapter.search_bm25(query="nâng lương cán bộ", user_roles=["HR"], top_k=10)
        hr_only_chunks = [c for c in bm25_hr if "Guest" not in c["allowed_roles"] and "Staff" not in c["allowed_roles"]]

    assert hr_only_chunks, "Cần có ít nhất 1 chunk giới hạn HR để làm target test"
    target_hr_chunk = hr_only_chunks[0]
    target_id = target_hr_chunk["chunk_id"]

    print(f"  -> Target HR Restricted Chunk ID: {target_id}")
    print(f"  -> Title: {target_hr_chunk['title'][:60]}...")
    print(f"  -> Citation: {target_hr_chunk['citation']}")
    print(f"  -> Allowed Roles: {target_hr_chunk['allowed_roles']}\n")

    # 2. Role Staff & Guest (Unauthorized for HR restricted chunk)
    staff_results = adapter.retrieve(query=query, user_roles=["Staff"], top_k=10)
    guest_results = adapter.retrieve(query=query, user_roles=["Guest"], top_k=10)

    staff_ids = [c["chunk_id"] for c in staff_results]
    guest_ids = [c["chunk_id"] for c in guest_results]

    in_staff = target_id in staff_ids
    in_guest = target_id in guest_ids

    print("[TEST 2] Lọc bỏ Chunk cấm đối với Staff & Guest:")
    print(f"  -> Target HR Chunk xuất hiện trong Staff (Top 10)? {in_staff}")
    print(f"  -> Target HR Chunk xuất hiện trong Guest (Top 10)? {in_guest}")
    assert not in_staff and not in_guest, "LỖI AN TOÀN: Chunk cấm HR lọt vào Staff/Guest!"
    print("  -> RESULT: PASS! Chunk cấm bị loại bỏ hoàn toàn đối với vai trò không có quyền.\n")

    # 3. Context Safety Check
    staff_context = "\n\n".join([f"[{c['citation']}]\n{c['text']}" for c in staff_results])
    guest_context = "\n\n".join([f"[{c['citation']}]\n{c['text']}" for c in guest_results])

    print("[TEST 3] Kiểm tra Context an toàn đưa vào LLM:")
    print(f"  -> Target HR Chunk ID trong Staff Context? {target_id in staff_context}")
    print(f"  -> Target HR Chunk ID trong Guest Context? {target_id in guest_context}")
    assert target_id not in staff_context and target_id not in guest_context, "LỖI RÒ RỈ: Target chunk lọt vào Context!"
    print("  -> RESULT: PASS! LLM Context an toàn 100%, không bị rò rỉ dữ liệu cấm.\n")

    # 4. Field Preservation Check
    print("[TEST 4] Kiểm tra bảo toàn Citation, Document ID, Chunk ID:")
    all_results = [("HR", hr_results), ("Staff", staff_results), ("Guest", guest_results)]
    for role_name, rlist in all_results:
        for idx, item in enumerate(rlist, 1):
            assert item["chunk_id"], f"Missing chunk_id in {role_name} rank {idx}"
            assert item["document_id"], f"Missing document_id in {role_name} rank {idx}"
            assert item["citation"], f"Missing citation in {role_name} rank {idx}"
            assert item["access_decision"] == "ALLOWED", f"Invalid decision in {role_name} rank {idx}"
            print(f"  -> [{role_name} Rank {idx}] chunk_id={item['chunk_id'][:8]}... | doc_id={item['document_id']} | decision={item['access_decision']}")

    print("\n==================================================")
    print("TẤT CẢ 4 BÀI KIỂM THỬ AN TOÀN ĐÃ PASS HOÀN HẢO!")
    print("==================================================")


if __name__ == "__main__":
    run_verification_tests()
