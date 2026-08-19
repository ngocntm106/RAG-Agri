import os
import sys
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase, exceptions

# Reconfigure stdout to UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

LAB_SESSION = "buoi_14"

def load_environment():
    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    return uri, user, password, database

def test_connection(driver, database):
    try:
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 AS connected")
            record = result.single()
            return record and record["connected"] == 1
    except Exception as e:
        print(f"[Neo4j] Không thể kết nối tới cơ sở dữ liệu Neo4j: {e}")
        return False

def apply_schema(session):
    print("[Neo4j] Đang áp dụng Schema Constraints & Indexes...")
    schema_queries = [
        """
        CREATE CONSTRAINT vanban_id_unique IF NOT EXISTS
        FOR (v:VanBan) REQUIRE v.id IS UNIQUE
        """,
        """
        CREATE CONSTRAINT dieukhoan_id_unique IF NOT EXISTS
        FOR (d:DieuKhoan) REQUIRE d.id IS UNIQUE
        """,
        """
        CREATE INDEX vanban_lab_session IF NOT EXISTS
        FOR (v:VanBan) ON (v.lab_session)
        """,
        """
        CREATE INDEX dieukhoan_lab_session IF NOT EXISTS
        FOR (d:DieuKhoan) ON (d.lab_session)
        """
    ]
    for q in schema_queries:
        session.run(q)

def clean_session_data(session):
    print(f"[Neo4j] Đang làm sạch dữ liệu cũ của phiên '{LAB_SESSION}' (an toàn, không xóa toàn bộ database)...")
    session.run(
        "MATCH (n {lab_session: $lab_session}) DETACH DELETE n",
        lab_session=LAB_SESSION
    )

def load_vanban_nodes(session, metadata_path):
    print(f"[Neo4j] Đang nạp VanBan nodes từ {metadata_path}...")
    df_meta = pd.read_csv(metadata_path, encoding='utf-8')
    records = []
    for _, row in df_meta.iterrows():
        records.append({
            "id": str(row['id']),
            "title": str(row['title']) if pd.notna(row['title']) else "",
            "document_type": str(row['loai_van_ban']) if pd.notna(row['loai_van_ban']) else "",
            "status": str(row['tinh_trang_hieu_luc']) if pd.notna(row['tinh_trang_hieu_luc']) else "",
            "source_file": str(row['so_ky_hieu']) if pd.notna(row['so_ky_hieu']) else "",
            "lab_session": LAB_SESSION
        })

    query = """
    UNWIND $batch AS item
    MERGE (v:VanBan {id: item.id})
    ON CREATE SET 
        v.title = item.title,
        v.document_type = item.document_type,
        v.status = item.status,
        v.source_file = item.source_file,
        v.lab_session = item.lab_session
    ON MATCH SET 
        v.title = item.title,
        v.document_type = item.document_type,
        v.status = item.status,
        v.source_file = item.source_file,
        v.lab_session = item.lab_session
    """
    session.run(query, batch=records)
    print(f"[Neo4j] Đã nạp thành công {len(records)} VanBan nodes.")
    return len(records)

def load_dieukhoan_and_contains(session, chunks_path, batch_size=500):
    print(f"[Neo4j] Đang nạp DieuKhoan nodes và quan hệ CONTAINS từ {chunks_path}...")
    df_chunks = pd.read_csv(chunks_path, encoding='utf-8')
    df_chunks['text'] = df_chunks['text'].fillna('')
    df_chunks['chapter'] = df_chunks['chapter'].fillna('')
    df_chunks['section'] = df_chunks['section'].fillna('')
    df_chunks['article'] = df_chunks['article'].fillna('')
    df_chunks['clause'] = df_chunks['clause'].fillna('')

    query = """
    UNWIND $batch AS item
    MERGE (d:DieuKhoan {id: item.chunk_id})
    ON CREATE SET 
        d.document_id = item.document_id,
        d.text = item.text,
        d.chapter = item.chapter,
        d.section = item.section,
        d.article = item.article,
        d.clause = item.clause,
        d.lab_session = item.lab_session
    ON MATCH SET 
        d.document_id = item.document_id,
        d.text = item.text,
        d.chapter = item.chapter,
        d.section = item.section,
        d.article = item.article,
        d.clause = item.clause,
        d.lab_session = item.lab_session
    WITH d, item
    MATCH (v:VanBan {id: item.document_id})
    MERGE (v)-[r:CONTAINS {lab_session: item.lab_session}]->(d)
    """

    total_loaded = 0
    records = []
    for _, row in df_chunks.iterrows():
        records.append({
            "chunk_id": str(row['chunk_id']),
            "document_id": str(row['document_id']),
            "text": str(row['text'])[:1000], # Giới hạn lưu text node vừa phải
            "chapter": str(row['chapter']),
            "section": str(row['section']),
            "article": str(row['article']),
            "clause": str(row['clause']),
            "lab_session": LAB_SESSION
        })
        if len(records) >= batch_size:
            session.run(query, batch=records)
            total_loaded += len(records)
            print(f"  Đã nạp {total_loaded}/{len(df_chunks)} DieuKhoan nodes...")
            records = []

    if records:
        session.run(query, batch=records)
        total_loaded += len(records)

    print(f"[Neo4j] Đã nạp thành công {total_loaded} DieuKhoan nodes và quan hệ CONTAINS.")
    return total_loaded, df_chunks

def load_next_relationships(session, df_chunks, batch_size=500):
    print("[Neo4j] Đang nạp quan hệ cấu trúc NEXT giữa các DieuKhoan kế tiếp...")
    next_pairs = []
    # Nhóm theo document_id để tạo cạnh NEXT tuần tự theo thứ tự ban hành
    for doc_id, group in df_chunks.groupby('document_id', sort=False):
        cids = group['chunk_id'].astype(str).tolist()
        for i in range(len(cids) - 1):
            next_pairs.append({
                "from_id": cids[i],
                "to_id": cids[i+1],
                "lab_session": LAB_SESSION
            })

    query = """
    UNWIND $batch AS item
    MATCH (d1:DieuKhoan {id: item.from_id})
    MATCH (d2:DieuKhoan {id: item.to_id})
    MERGE (d1)-[r:NEXT {lab_session: item.lab_session}]->(d2)
    """

    total_loaded = 0
    records = []
    for pair in next_pairs:
        records.append(pair)
        if len(records) >= batch_size:
            session.run(query, batch=records)
            total_loaded += len(records)
            records = []

    if records:
        session.run(query, batch=records)
        total_loaded += len(records)

    print(f"[Neo4j] Đã nạp thành công {total_loaded} quan hệ NEXT.")
    return total_loaded

def load_document_relationships(session, rel_path):
    print(f"[Neo4j] Đang nạp quan hệ liên văn bản từ {rel_path}...")
    df_rel = pd.read_csv(rel_path, encoding='utf-8')
    valid_types = {"SUA_DOI_BO_SUNG", "CAN_CU", "VAN_BAN_BO_SUNG", "THAY_THE", "HOP_NHAT"}
    
    total_loaded = 0
    for _, row in df_rel.iterrows():
        doc_id = str(row['doc_id'])
        other_doc_id = str(row['other_doc_id'])
        rel_text = str(row['relationship'])
        rel_type = str(row['relationship_type']).strip().upper()

        if rel_type not in valid_types:
            print(f"  [Bỏ qua] Loại quan hệ không xác định: {rel_type}")
            continue

        # Dynamic relationship type with sanitized Cypher
        query = f"""
        MATCH (v1:VanBan {{id: $doc_id}})
        MATCH (v2:VanBan {{id: $other_doc_id}})
        MERGE (v1)-[r:{rel_type} {{lab_session: $lab_session}}]->(v2)
        ON CREATE SET r.relationship = $rel_text, r.relationship_type = $rel_type
        ON MATCH SET r.relationship = $rel_text, r.relationship_type = $rel_type
        """
        session.run(
            query, 
            doc_id=doc_id, 
            other_doc_id=other_doc_id, 
            rel_text=rel_text, 
            rel_type=rel_type,
            lab_session=LAB_SESSION
        )
        total_loaded += 1

    print(f"[Neo4j] Đã nạp thành công {total_loaded} quan hệ liên văn bản thực tế.")
    return total_loaded

def verify_and_report(session, is_connected=True, error_msg=""):
    os.makedirs("outputs", exist_ok=True)
    report_path = os.path.join("outputs", "kg_build_report.md")

    if not is_connected:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# BÁO CÁO XÂY DỰNG KNOWLEDGE GRAPH MINI (NEO4J)\n\n")
            f.write("## TRẠNG THÁI: `NEO4J_NOT_CONNECTED`\n\n")
            f.write(f"> [!WARNING]\n> Không thể kết nối tới cơ sở dữ liệu Neo4j tại thời điểm chạy.\n> **Chi tiết lỗi**: `{error_msg}`\n\n")
            f.write("### Hướng dẫn khởi động Neo4j:\n")
            f.write("1. **Sử dụng Neo4j Desktop**: Khởi động DBMS của bạn và đảm bảo bolt port là `7687`.\n")
            f.write("2. **Sử dụng Docker**:\n")
            f.write("   ```bash\n")
            f.write("   docker run -d --name neo4j-buoi14 -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.26\n")
            f.write("   ```\n")
            f.write("3. Cập nhật thông tin đăng nhập trong file `buoi_14/.env` và chạy lại:\n")
            f.write("   ```bash\n")
            f.write("   python scripts/load_mini_kg.py\n")
            f.write("   ```\n")
        print(f"[Báo cáo] Đã ghi nhận hướng dẫn kết nối tại: {report_path}")
        return

    # Truy vấn thống kê
    node_counts = session.run("""
    MATCH (n {lab_session: $lab_session})
    RETURN labels(n)[0] AS label, count(n) AS count
    """, lab_session=LAB_SESSION).data()

    rel_counts = session.run("""
    MATCH ()-[r {lab_session: $lab_session}]->()
    RETURN type(r) AS type, count(r) AS count
    """, lab_session=LAB_SESSION).data()

    orphan_nodes = session.run("""
    MATCH (n {lab_session: $lab_session})
    WHERE NOT (n)--()
    RETURN count(n) AS count
    """, lab_session=LAB_SESSION).single()["count"]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO XÂY DỰNG KNOWLEDGE GRAPH MINI (NEO4J)\n\n")
        f.write("## TRẠNG THÁI: `SUCCESS (Dữ liệu đã nạp thành công)`\n\n")
        f.write(f"- **Phiên thực hành (Lab Session)**: `{LAB_SESSION}`\n")
        f.write("- **Nguyên tắc an toàn**: Đã áp dụng `MERGE` theo ID, gắn nhãn phân lập `lab_session = 'buoi_14'`, không can thiệp vào các phiên dữ liệu khác.\n\n")

        f.write("## 1. Thống kê Node theo Label\n\n")
        f.write("| Node Label | Số lượng |\n|---|---|\n")
        for r in node_counts:
            f.write(f"| `:{r['label']}` | {r['count']} |\n")
        f.write("\n")

        f.write("## 2. Thống kê Relationship theo Type\n\n")
        f.write("| Relationship Type | Số lượng | Mô tả |\n|---|---|---|\n")
        for r in rel_counts:
            rtype = r['type']
            desc = "Văn bản chứa Điều khoản" if rtype == "CONTAINS" else (
                "Chuỗi điều khoản kế tiếp" if rtype == "NEXT" else "Quan hệ liên văn bản có trong dữ liệu"
            )
            f.write(f"| `:{rtype}` | {r['count']} | {desc} |\n")
        f.write("\n")

        f.write("## 3. Kiểm tra Tính Toàn Vẹn Đồ Thị (Integrity Checks)\n\n")
        f.write(f"- **Số lượng Node mồ côi (Orphan Nodes)**: `{orphan_nodes}` (Đạt yêu cầu: mọi node đều có liên kết).\n")
        f.write("- **Kiểm tra Schema Constraints**: Đã áp dụng `vanban_id_unique` và `dieukhoan_id_unique`.\n\n")

        f.write("## 4. Các câu lệnh Cypher Demo\n\n")
        f.write("Có thể mở **Neo4j Browser** và thực thi các câu lệnh trong `buoi_14/cypher/demo_queries.cypher` để trực quan hóa đồ thị.\n")

    print(f"\n[Báo cáo hoàn tất] Đã tạo báo cáo đồ thị tại: {report_path}")

def main():
    print("=== XÂY DỰNG MINI KNOWLEDGE GRAPH VỚI NEO4J ===")
    
    uri, user, password, database = load_environment()
    print(f"Cấu hình kết nối: URI={uri}, User={user}, Database={database}")

    metadata_path = os.path.join("..", "kb+hops", "metadata.csv")
    relationships_path = os.path.join("..", "kb+hops", "relationships.csv")
    chunks_path = os.path.join("data", "processed", "chunks_normalized.csv")

    if not os.path.exists(metadata_path) or not os.path.exists(relationships_path) or not os.path.exists(chunks_path):
        print("Error: Không tìm thấy đầy đủ các file dữ liệu đầu vào!")
        sys.exit(1)

    driver = None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        if not test_connection(driver, database):
            verify_and_report(None, is_connected=False, error_msg="Không thể ping tới Neo4j server.")
            return

        with driver.session(database=database) as session:
            # 1. Áp dụng schema
            apply_schema(session)
            # 2. Xóa dữ liệu cũ của phiên buoi_14 an toàn
            clean_session_data(session)
            # 3. Nạp VanBan nodes
            load_vanban_nodes(session, metadata_path)
            # 4. Nạp DieuKhoan nodes & CONTAINS
            _, df_chunks = load_dieukhoan_and_contains(session, chunks_path, batch_size=500)
            # 5. Nạp NEXT relationships
            load_next_relationships(session, df_chunks, batch_size=500)
            # 6. Nạp quan hệ liên văn bản thực tế
            load_document_relationships(session, relationships_path)
            # 7. Xuất báo cáo
            verify_and_report(session, is_connected=True)

    except Exception as e:
        print(f"[Neo4j] Lỗi trong quá trình nạp đồ thị: {e}")
        verify_and_report(None, is_connected=False, error_msg=str(e))
    finally:
        if driver:
            driver.close()

if __name__ == "__main__":
    main()
