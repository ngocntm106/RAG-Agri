"""
Script: load_secure_kg.py
Purpose: Load and update Role-Based Access Control (RBAC) security properties (allowed_roles)
         into Neo4j Graph Database without deleting existing graph structure.

Input: buoi_14/data/processed/chunks_secure.csv
Database Config: Read from buoi_14/.env via src.config
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
from neo4j import GraphDatabase, exceptions

# Ensure project root is in sys.path and stdout is UTF-8
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

from src.config import (
    get_neo4j_config,
    CHUNKS_SECURE_PATH,
    VALID_ROLES
)

LAB_SESSION = "buoi_15"


def get_driver():
    """Khởi tạo Neo4j Driver từ cấu hình .env cục bộ."""
    cfg = get_neo4j_config()
    print(f"[Neo4j Config] Đọc từ: {cfg['env_path']}")
    print(f"               URI: {cfg['uri']} | User: {cfg['user']} | Database: {cfg['database']}")
    driver = GraphDatabase.driver(
        cfg["uri"],
        auth=(cfg["user"], cfg["password"])
    )
    return driver, cfg["database"]


def test_connection(driver, database: str) -> bool:
    """Kiểm tra kết nối tới Neo4j."""
    try:
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 AS connected")
            rec = result.single()
            return bool(rec and rec["connected"] == 1)
    except Exception as e:
        print(f"\n[CẢNH BÁO] Không thể kết nối tới Neo4j ({e})")
        print("💡 HƯỚNG DẪN XỬ LÝ:")
        print(" 1. Mở 'Neo4j Desktop' trên máy tính.")
        print(" 2. Nhấn nút 'Start' trên DBMS/Database của bạn.")
        print(" 3. Kiểm tra cổng bolt://localhost:7687 và mật khẩu trong file 'buoi_14/.env'.\n")
        return False


def apply_schema(session):
    """Tạo indexes và constraints nếu chưa có để tối ưu truy vấn bảo mật."""
    print("[1/4] Đang áp dụng Index và Schema Constraints...")
    constraints_and_indexes = [
        "CREATE CONSTRAINT vanban_id_unique IF NOT EXISTS FOR (v:VanBan) REQUIRE v.id IS UNIQUE",
        "CREATE CONSTRAINT dieukhoan_id_unique IF NOT EXISTS FOR (d:DieuKhoan) REQUIRE d.id IS UNIQUE",
        "CREATE INDEX vanban_allowed_roles IF NOT EXISTS FOR (v:VanBan) ON (v.allowed_roles)",
        "CREATE INDEX dieukhoan_allowed_roles IF NOT EXISTS FOR (d:DieuKhoan) ON (d.allowed_roles)",
        "CREATE INDEX vanban_lab_session IF NOT EXISTS FOR (v:VanBan) ON (v.lab_session)",
        "CREATE INDEX dieukhoan_lab_session IF NOT EXISTS FOR (d:DieuKhoan) ON (d.lab_session)"
    ]
    for q in constraints_and_indexes:
        try:
            session.run(q)
        except Exception as ex:
            print(f"      [Ghi chú schema]: {ex}")


def update_secure_nodes(session, chunks_path: Path, batch_size: int = 500):
    """
    Nạp/Cập nhật thuộc tính allowed_roles (mảng chuỗi) cho các node DieuKhoan và VanBan.
    Sử dụng MERGE để không làm mất dữ liệu đồ thị hiện tại.
    """
    print(f"[2/4] Đang đọc dữ liệu phân quyền từ: {chunks_path}")
    if not chunks_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file {chunks_path}")

    df = pd.read_csv(chunks_path)
    total_rows = len(df)
    print(f"      Tổng số chunks cần cập nhật phân quyền: {total_rows:,}")

    # Chuẩn bị dữ liệu cập nhật theo batch
    print("[3/4] Đang cập nhật thuộc tính allowed_roles vào Neo4j (batch size: 500)...")

    # 1. Cập nhật DieuKhoan nodes
    dieukhoan_query = """
    UNWIND $batch AS item
    MERGE (d:DieuKhoan {id: item.chunk_id})
    ON CREATE SET
        d.document_id = item.document_id,
        d.text = item.text,
        d.chapter = item.chapter,
        d.section = item.section,
        d.article = item.article,
        d.clause = item.clause,
        d.allowed_roles = item.allowed_roles,
        d.lab_session = item.lab_session
    ON MATCH SET
        d.allowed_roles = item.allowed_roles,
        d.lab_session = item.lab_session
    WITH d, item
    MERGE (v:VanBan {id: item.document_id})
    ON CREATE SET
        v.title = item.title,
        v.source_file = item.source_file,
        v.lab_session = item.lab_session
    MERGE (v)-[r:CONTAINS]->(d)
    ON CREATE SET r.lab_session = item.lab_session
    """

    records = []
    updated_count = 0

    for _, row in df.iterrows():
        # Parse JSON allowed_roles to Native Python List
        raw_roles = row["allowed_roles"]
        roles_list = json.loads(raw_roles) if isinstance(raw_roles, str) else list(raw_roles)

        records.append({
            "chunk_id": str(row["chunk_id"]),
            "document_id": str(row["document_id"]),
            "title": str(row.get("title", "")) if pd.notna(row.get("title")) else "",
            "source_file": str(row.get("source_file", "")) if pd.notna(row.get("source_file")) else "",
            "text": str(row.get("text", ""))[:1000],
            "chapter": str(row.get("chapter", "")) if pd.notna(row.get("chapter")) else "",
            "section": str(row.get("section", "")) if pd.notna(row.get("section")) else "",
            "article": str(row.get("article", "")) if pd.notna(row.get("article")) else "",
            "clause": str(row.get("clause", "")) if pd.notna(row.get("clause")) else "",
            "allowed_roles": roles_list,
            "lab_session": LAB_SESSION
        })

        if len(records) >= batch_size:
            session.run(dieukhoan_query, batch=records)
            updated_count += len(records)
            print(f"      Đã cập nhật: {updated_count:>5,} / {total_rows:,} chunks...")
            records = []

    if records:
        session.run(dieukhoan_query, batch=records)
        updated_count += len(records)
        print(f"      Đã cập nhật: {updated_count:>5,} / {total_rows:,} chunks...")

    # 2. Cập nhật allowed_roles tổng hợp cho các node VanBan
    print("      Đang tổng hợp và gán quyền allowed_roles cho các node VanBan...")
    vanban_role_query = """
    MATCH (v:VanBan)-[:CONTAINS]->(d:DieuKhoan)
    WHERE d.allowed_roles IS NOT NULL
    WITH v, apoc.coll.toSet(apoc.coll.flatten(collect(d.allowed_roles))) AS combined_roles
    SET v.allowed_roles = combined_roles, v.lab_session = $lab_session
    RETURN count(v) AS updated_vanban
    """
    
    # Fallback query if APOC is not installed
    vanban_role_query_standard = """
    MATCH (v:VanBan)-[:CONTAINS]->(d:DieuKhoan)
    WHERE d.allowed_roles IS NOT NULL
    UNWIND d.allowed_roles AS role
    WITH v, collect(DISTINCT role) AS distinct_roles
    SET v.allowed_roles = distinct_roles, v.lab_session = $lab_session
    RETURN count(v) AS updated_vanban
    """
    
    try:
        res = session.run(vanban_role_query_standard, lab_session=LAB_SESSION)
        rec = res.single()
        print(f"      Đã gán allowed_roles cho {rec['updated_vanban']} node VanBan.")
    except Exception as ex:
        print(f"      Ghi chú cập nhật VanBan: {ex}")


def verify_secure_kg(session):
    """
    Thực thi các truy vấn kiểm thử nhanh để xác minh thông tin phân quyền trong Neo4j.
    """
    print("\n[4/4] === KIỂM TRA & XÁC MINH DỮ LIỆU ĐỒ THỊ BẢO MẬT (VERIFICATION) ===")

    # 1. Đếm số node có chứa thuộc tính allowed_roles
    q1 = """
    MATCH (n)
    WHERE n:VanBan OR n:DieuKhoan
    RETURN 
        labels(n)[0] AS node_type,
        count(n) AS total_nodes,
        count(n.allowed_roles) AS nodes_with_allowed_roles
    ORDER BY node_type DESC
    """
    print("\n1. Thống kê số lượng node có gắn thẻ bảo mật (allowed_roles):")
    res1 = session.run(q1)
    for r in res1:
        print(f" • Node Label [{r['node_type']:<10}]: Tổng số = {r['total_nodes']:>5,}, Có allowed_roles = {r['nodes_with_allowed_roles']:>5,}")

    # 2. Phân bố các nhóm quyền trên node DieuKhoan
    q2 = """
    MATCH (d:DieuKhoan)
    WHERE d.allowed_roles IS NOT NULL
    RETURN d.allowed_roles AS roles, count(d) AS chunk_count
    ORDER BY chunk_count DESC
    """
    print("\n2. Phân bố các nhóm quyền trên DieuKhoan nodes:")
    res2 = session.run(q2)
    for r in res2:
        roles_str = str(r["roles"])
        print(f" • Quyền {roles_str:<35}: {r['chunk_count']:>5,} chunks")

    # 3. Lấy thử 1 node VanBan và 3 node DieuKhoan liên kết để kiểm chứng
    q3 = """
    MATCH (v:VanBan)-[:CONTAINS]->(d:DieuKhoan)
    WHERE d.allowed_roles IS NOT NULL
    WITH v, collect(d)[..3] AS sample_dieukhoan
    RETURN 
        v.id AS doc_id,
        v.title AS doc_title,
        v.allowed_roles AS doc_roles,
        [d IN sample_dieukhoan | {id: d.id, article: d.article, roles: d.allowed_roles}] AS sample_chunks
    LIMIT 1
    """
    print("\n3. Mẫu kiểm chứng 1 VanBan và các DieuKhoan liên kết:")
    res3 = session.run(q3)
    record = res3.single()
    if record:
        print(f" [VĂN BẢN]: ID = {record['doc_id']}")
        print(f"  Tiêu đề: {str(record['doc_title'])[:80]}...")
        print(f"  Allowed Roles (Văn bản): {record['doc_roles']}")
        print(f"  Các Điều khoản con mẫu (DieuKhoan):")
        for chunk in record["sample_chunks"]:
            print(f"    - Chunk ID: {chunk['id']}")
            print(f"      Điều khoản: {chunk['article']}")
            print(f"      Allowed Roles: {chunk['roles']}")
    else:
        print("  (Chưa tìm thấy liên kết mẫu)")

    print("\n[SUCCESS] Kiểm tra đồ thị phân quyền Neo4j hoàn tất thành công!")


def main():
    driver, database = get_driver()
    try:
        if not test_connection(driver, database):
            return

        with driver.session(database=database) as session:
            apply_schema(session)
            update_secure_nodes(session, CHUNKS_SECURE_PATH)
            verify_secure_kg(session)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
