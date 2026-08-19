"""
Script: secure_search_demo.py
Purpose: Demonstrate and test Secure Role-Based Access Control (RBAC) Retrieval Pipeline
         across different user roles and search methods.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output encoding and project root in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

from src.secure_retriever import SecureRetriever


def run_demo():
    print("=" * 80)
    print("         DEMO SECURE RETRIEVAL PIPELINE (RBAC) - BUỔI 15")
    print("=" * 80)

    retriever = SecureRetriever()

    test_scenarios = [
        {
            "title": "KỊCH BẢN 1: Truy vấn tài liệu Nhân sự (HR Sensitive)",
            "query": "Hồ sơ và tiêu chuẩn bổ nhiệm người quản lý, tổng giám đốc",
            "roles_to_test": [
                ["Guest"],
                ["Staff"],
                ["HR"],
                ["Admin"]
            ]
        },
        {
            "title": "KỊCH BẢN 2: Truy vấn tài liệu Nghiệp vụ Tín dụng & Quản trị Rủi ro",
            "query": "Hạn mức cấp tín dụng và tỷ lệ an toàn vốn cho vay",
            "roles_to_test": [
                ["Guest"],
                ["Staff"],
                ["Admin"]
            ]
        }
    ]

    for scenario in test_scenarios:
        print(f"\n{'='*80}\n>>> {scenario['title']}\nCâu hỏi: \"{scenario['query']}\"")
        print("=" * 80)

        for roles in scenario["roles_to_test"]:
            print(f"\n--- ĐÓNG VAI (ROLE): {roles} ---")
            results = retriever.retrieve(
                query=scenario["query"],
                user_roles=roles,
                method="hybrid_rerank",
                top_k=2,
                candidate_k=10
            )

            if not results:
                print("  [Không có kết quả nào phù hợp với quyền xem]")
                continue

            for r in results:
                print(f" • [Top {r['rank']}] Score: {r['score']} | Allowed Roles: {r['allowed_roles']}")
                print(f"   Trích dẫn : {r['citation']}")
                print(f"   Nội dung  : {r['text'][:120]}...\n")


if __name__ == "__main__":
    run_demo()
