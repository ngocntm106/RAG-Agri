import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Helper to clean dict values for Neo4j compatibility
def clean_dict(d):
    cleaned = {}
    for k, v in d.items():
        if pd.isna(v):
            cleaned[k] = ""
        else:
            cleaned[k] = str(v)
    return cleaned

def main():
    print("=" * 60)
    print("BƯỚC 8: IMPORT KNOWLEDGE GRAPH VÀO NEO4J")
    print("=" * 60)
    
    env_path = os.path.join("ner_kb", ".env")
    if not os.path.exists(env_path):
        print(f"Lỗi: Không tìm thấy file cấu hình {env_path}")
        sys.exit(1)
        
    load_dotenv(env_path)
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    if not uri or not user or not password:
        print("Lỗi: Cấu hình kết nối Neo4j trong .env chưa đầy đủ.")
        sys.exit(1)
        
    # Input files
    docs_path = os.path.join("ner_kb", "cleaned_documents.csv")
    entities_path = os.path.join("ner_kb", "entities.csv")
    rels_path = os.path.join("ner_kb", "relationships.csv")
    
    for path in [docs_path, entities_path, rels_path]:
        if not os.path.exists(path):
            print(f"Lỗi: Không tìm thấy file {path}. Vui lòng chạy các bước trước.")
            sys.exit(1)
            
    docs_df = pd.read_csv(docs_path)
    entities_df = pd.read_csv(entities_path)
    rels_df = pd.read_csv(rels_path)
    
    print("Đang kết nối tới Neo4j...")
    driver = None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("Kết nối thành công.")
        
        session = driver.session(database=database)
        
        # 3. Tạo uniqueness constraints hợp lý
        print("\nĐang cấu hình Uniqueness Constraints...")
        constraints = {
            "document_id_unique": "CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "coquan_id_unique": "CREATE CONSTRAINT coquan_id_unique IF NOT EXISTS FOR (c:CoQuan) REQUIRE c.id IS UNIQUE",
            "nguoiky_id_unique": "CREATE CONSTRAINT nguoiky_id_unique IF NOT EXISTS FOR (n:NguoiKy) REQUIRE n.id IS UNIQUE",
            "doituong_id_unique": "CREATE CONSTRAINT doituong_id_unique IF NOT EXISTS FOR (d:DoiTuongApDung) REQUIRE d.id IS UNIQUE",
            "linhvuc_id_unique": "CREATE CONSTRAINT linhvuc_id_unique IF NOT EXISTS FOR (l:LinhVuc) REQUIRE l.id IS UNIQUE"
        }
        
        for name, query in constraints.items():
            try:
                session.run(query)
                print(f"  - Đã tạo/kiểm tra Constraint: {name}")
            except Exception as ce:
                print(f"  - Cảnh báo khi tạo Constraint '{name}': {ce}")
                
        # 5. Tạo các nút Document
        print("\nĐang nạp các nút Document...")
        doc_count = 0
        for _, row in docs_df.iterrows():
            props = clean_dict(row.to_dict())
            
            # Map doc id to string representation
            props['id'] = str(props['id']).strip()
            
            doc_query = """
            MERGE (d:Document {id: $id})
            SET d.title = $title,
                d.so_ky_hieu = $so_ky_hieu,
                d.ngay_ban_hanh = $ngay_ban_hanh,
                d.loai_van_ban = $loai_van_ban,
                d.ngay_co_hieu_luc = $ngay_co_hieu_luc,
                d.ngay_het_hieu_luc = $ngay_het_hieu_luc,
                d.nguon_thu_thap = $nguon_thu_thap,
                d.ngay_dang_cong_bao = $ngay_dang_cong_bao,
                d.nganh = $nganh,
                d.linh_vuc = $linh_vuc,
                d.co_quan_ban_hanh = $co_quan_ban_hanh,
                d.chuc_danh = $chuc_danh,
                d.nguoi_ky = $nguoi_ky,
                d.pham_vi = $pham_vi,
                d.tinh_trang_hieu_luc = $tinh_trang_hieu_luc,
                d.content_clean = $content_clean
            """
            session.run(doc_query, **props)
            doc_count += 1
        print(f"  -> Hoàn tất nạp {doc_count} nút Document.")
        
        # 5. Tạo các nút Entity (CoQuan, NguoiKy, DoiTuongApDung, LinhVuc)
        print("\nĐang nạp các nút Entity...")
        
        # Deduplicate to insert unique entity nodes
        unique_entities = entities_df.drop_duplicates(subset=["entity_id", "entity_type"])
        entity_count = 0
        
        entity_queries = {
            "CoQuan": "MERGE (e:CoQuan {id: $id}) SET e.name = $name",
            "NguoiKy": "MERGE (e:NguoiKy {id: $id}) SET e.name = $name",
            "DoiTuongApDung": "MERGE (e:DoiTuongApDung {id: $id}) SET e.name = $name",
            "LinhVuc": "MERGE (e:LinhVuc {id: $id}) SET e.name = $name"
        }
        
        for _, row in unique_entities.iterrows():
            entity_id = str(row['entity_id']).strip()
            canonical_name = str(row['canonical_name']).strip()
            entity_type = str(row['entity_type']).strip()
            
            if entity_type in entity_queries:
                query = entity_queries[entity_type]
                session.run(query, id=entity_id, name=canonical_name)
                entity_count += 1
                
        print(f"  -> Hoàn tất nạp {entity_count} nút Entity.")
        
        # 6. Tạo các quan hệ (THAM_CHIEU, SUA_DOI_BO_SUNG, THAY_THE_BOI, BAN_HANH_BOI, KY_BOI, AP_DUNG_CHO, THUOC_LINH_VUC)
        print("\nĐang nạp các quan hệ...")
        rel_inserted_count = 0
        import_errors = []
        
        for idx, row in rels_df.iterrows():
            source = str(row['source']).strip()
            target = str(row['target']).strip()
            rel_type = str(row['relationship_type']).strip()
            method = str(row['method']).strip()
            confidence = float(row['confidence'])
            evidence = str(row['evidence']).strip()
            
            # 7. Nếu source hoặc target không tìm thấy, không tạo node rác; ghi lỗi import riêng
            # Verify node existence
            source_node = session.run("MATCH (n) WHERE n.id = $source RETURN id(n)", source=source).single()
            target_node = session.run("MATCH (n) WHERE n.id = $target RETURN id(n)", target=target).single()
            
            if not source_node:
                import_errors.append(f"Không tìm thấy source node '{source}' cho quan hệ {rel_type} -> '{target}'")
                continue
            if not target_node:
                import_errors.append(f"Không tìm thấy target node '{target}' cho quan hệ '{source}' -> {rel_type}")
                continue
                
            # 8. Import idempotent using MERGE
            rel_query = f"""
            MATCH (s) WHERE s.id = $source
            MATCH (t) WHERE t.id = $target
            MERGE (s)-[r:{rel_type}]->(t)
            SET r.method = $method,
                r.confidence = $confidence,
                r.evidence = $evidence
            """
            session.run(rel_query, source=source, target=target, method=method, confidence=confidence, evidence=evidence)
            rel_inserted_count += 1
            
        print(f"  -> Hoàn tất nạp {rel_inserted_count} quan hệ.")
        print(f"  -> Đã phát hiện và bỏ qua {len(import_errors)} quan hệ không hợp lệ.")
        
        # 9. Lấy thống kê dữ liệu sau import
        print("\n" + "=" * 60)
        print("THỐNG KÊ KẾT QUẢ IMPORT TRÊN NEO4J:")
        print("=" * 60)
        
        # Nodes count by Label
        labels = ["Document", "CoQuan", "NguoiKy", "DoiTuongApDung", "LinhVuc"]
        print("Số lượng nút theo nhãn (Labels):")
        for label in labels:
            c_res = session.run(f"MATCH (n:{label}) RETURN count(n) AS count").single()
            print(f"  - Nhãn ':{label}': {c_res['count']}")
            
        # Relationships count by Type
        rel_types = ["THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI", "BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"]
        print("\nSố lượng quan hệ theo loại (Types):")
        for rtype in rel_types:
            c_res = session.run(f"MATCH ()-[r:{rtype}]->() RETURN count(r) AS count").single()
            print(f"  - Quan hệ '[:{rtype}]': {c_res['count']}")
            
        print(f"\nSố lượng lỗi import ghi nhận: {len(import_errors)}")
        if import_errors:
            print("\nChi tiết các lỗi import đầu tiên:")
            for err in import_errors[:5]:
                print(f"  - {err}")
            if len(import_errors) > 5:
                print(f"  ... và {len(import_errors) - 5} lỗi khác.")
                
        print("\nTrạng thái xác minh: HOÀN TẤT BƯỚC 8. Đạt yêu cầu [PASS]")
        session.close()
        
    except Exception as e:
        print(f"\nLỗi trong quá trình nạp dữ liệu: {e}")
        print("Trạng thái: THẤT BẠI [FAIL]")
        sys.exit(1)
    finally:
        # 10. Đóng Neo4j driver đúng cách
        if driver:
            driver.close()
            print("Đã đóng kết nối Neo4j driver.")

if __name__ == "__main__":
    main()
