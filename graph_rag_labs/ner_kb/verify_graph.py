import os
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 60)
    print("BƯỚC 9: KIỂM TRA VÀ ĐỐI CHIẾU KNOWLEDGE GRAPH SAU IMPORT")
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
        
    # Input files for comparison
    docs_path = os.path.join("ner_kb", "cleaned_documents.csv")
    entities_path = os.path.join("ner_kb", "entities.csv")
    rels_path = os.path.join("ner_kb", "relationships.csv")
    
    for path in [docs_path, entities_path, rels_path]:
        if not os.path.exists(path):
            print(f"Lỗi: Không tìm thấy file {path}.")
            sys.exit(1)
            
    docs_df = pd.read_csv(docs_path)
    entities_df = pd.read_csv(entities_path)
    rels_df = pd.read_csv(rels_path)
    
    # Calculate expected counts from CSVs
    expected_docs = len(docs_df)
    
    unique_entities = entities_df.drop_duplicates(subset=["entity_id", "entity_type"])
    expected_coquan = len(unique_entities[unique_entities['entity_type'] == "CoQuan"])
    expected_nguoiky = len(unique_entities[unique_entities['entity_type'] == "NguoiKy"])
    expected_doituong = len(unique_entities[unique_entities['entity_type'] == "DoiTuongApDung"])
    expected_linhvuc = len(unique_entities[unique_entities['entity_type'] == "LinhVuc"])
    expected_total_entities = len(unique_entities)
    
    expected_rels = rels_df['relationship_type'].value_counts().to_dict()
    expected_total_rels = len(rels_df)
    
    print("Đang truy vấn số liệu từ cơ sở dữ liệu Neo4j...")
    driver = None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        
        session = driver.session(database=database)
        
        # 1. Query Node counts
        actual_docs = session.run("MATCH (n:Document) RETURN count(n) AS count").single()["count"]
        actual_coquan = session.run("MATCH (n:CoQuan) RETURN count(n) AS count").single()["count"]
        actual_nguoiky = session.run("MATCH (n:NguoiKy) RETURN count(n) AS count").single()["count"]
        actual_doituong = session.run("MATCH (n:DoiTuongApDung) RETURN count(n) AS count").single()["count"]
        actual_linhvuc = session.run("MATCH (n:LinhVuc) RETURN count(n) AS count").single()["count"]
        
        # 2. Query Relationship counts
        actual_rels = {}
        for rtype in ["THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI", "BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"]:
            actual_rels[rtype] = session.run(f"MATCH ()-[r:{rtype}]->() RETURN count(r) AS count").single()["count"]
            
        actual_total_rels = sum(actual_rels.values())
        
        # 3. Print verification table
        print("\n" + "=" * 80)
        print(f"{'ĐỐI CHIẾU SỐ LIỆU':^80}")
        print("=" * 80)
        print(f"{'Hạng mục':<35} | {'Kỳ vọng (CSV)':<15} | {'Thực tế (Neo4j)':<15} | {'Trạng thái':<10}")
        print("-" * 80)
        
        # Document comparison
        doc_status = "PASS" if expected_docs == actual_docs else "FAIL"
        print(f"{'Nút :Document':<35} | {expected_docs:<15} | {actual_docs:<15} | {doc_status:<10}")
        
        # Entities comparison
        cq_status = "PASS" if expected_coquan == actual_coquan else "FAIL"
        print(f"{'Nút :CoQuan':<35} | {expected_coquan:<15} | {actual_coquan:<15} | {cq_status:<10}")
        
        nk_status = "PASS" if expected_nguoiky == actual_nguoiky else "FAIL"
        print(f"{'Nút :NguoiKy':<35} | {expected_nguoiky:<15} | {actual_nguoiky:<15} | {nk_status:<10}")
        
        dt_status = "PASS" if expected_doituong == actual_doituong else "FAIL"
        print(f"{'Nút :DoiTuongApDung':<35} | {expected_doituong:<15} | {actual_doituong:<15} | {dt_status:<10}")
        
        lv_status = "PASS" if expected_linhvuc == actual_linhvuc else "FAIL"
        print(f"{'Nút :LinhVuc':<35} | {expected_linhvuc:<15} | {actual_linhvuc:<15} | {lv_status:<10}")
        
        # Relationships comparison
        print("-" * 80)
        for rtype in ["THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI", "BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"]:
            exp_count = expected_rels.get(rtype, 0)
            act_count = actual_rels.get(rtype, 0)
            rel_status = "PASS" if exp_count == act_count else "FAIL"
            print(f"{f'Quan hệ [:{rtype}]':<35} | {exp_count:<15} | {act_count:<15} | {rel_status:<10}")
            
        print("-" * 80)
        tot_rel_status = "PASS" if expected_total_rels == actual_total_rels else "FAIL"
        print(f"{'Tổng số quan hệ (Relationships)':<35} | {expected_total_rels:<15} | {actual_total_rels:<15} | {tot_rel_status:<10}")
        print("=" * 80)
        
        # 3. Query some Document -> NguoiKy sample
        print("\n3. MẪU QUAN HỆ :Document -> :NguoiKy (5 mẫu):")
        nk_query = """
        MATCH (d:Document)-[r:KY_BOI]->(p:NguoiKy)
        RETURN d.so_ky_hieu AS doc, p.name AS signer
        LIMIT 5
        """
        nk_records = session.run(nk_query)
        for idx, rec in enumerate(nk_records):
            print(f"  {idx+1}. Văn bản [{rec['doc']}] được ký bởi: {rec['signer']}")
            
        # 4. Query some Document -> DoiTuongApDung sample
        print("\n4. MẪU QUAN HỆ :Document -> :DoiTuongApDung (5 mẫu):")
        dt_query = """
        MATCH (d:Document)-[r:AP_DUNG_CHO]->(o:DoiTuongApDung)
        RETURN d.so_ky_hieu AS doc, o.name AS target
        LIMIT 5
        """
        dt_records = session.run(dt_query)
        for idx, rec in enumerate(dt_records):
            print(f"  {idx+1}. Văn bản [{rec['doc']}] áp dụng cho: {rec['target']}")
            
        # 5. Query Document -> Document relationships sample
        print("\n5. MẪU QUAN HỆ :Document -> :Document (5 mẫu):")
        doc_doc_query = """
        MATCH (d1:Document)-[r:THAM_CHIEU|SUA_DOI_BO_SUNG|THAY_THE_BOI]->(d2:Document)
        RETURN d1.so_ky_hieu AS source, type(r) AS rel, d2.so_ky_hieu AS target
        LIMIT 5
        """
        doc_doc_records = session.run(doc_doc_query)
        for idx, rec in enumerate(doc_doc_records):
            print(f"  {idx+1}. [{rec['source']}] --[:{rec['rel']}]--> [{rec['target']}]")
            
        # Check overall PASS state
        all_passed = (
            expected_docs == actual_docs and
            expected_coquan == actual_coquan and
            expected_nguoiky == actual_nguoiky and
            expected_doituong == actual_doituong and
            expected_linhvuc == actual_linhvuc and
            expected_total_rels == actual_total_rels
        )
        
        print("\n" + "=" * 60)
        if all_passed:
            print("KẾT QUẢ ĐỐI CHIẾU: HOÀN TOÀN KHỚP [PASS]")
            sys.exit(0)
        else:
            print("KẾT QUẢ ĐỐI CHIẾU: CÓ SỰ CHÊNH LỆCH [FAIL]")
            sys.exit(1)
            
    except Exception as e:
        print(f"Lỗi truy vấn đồ thị kiểm tra: {e}")
        sys.exit(1)
    finally:
        if driver:
            driver.close()
            print("Đã đóng kết nối Neo4j driver.")

if __name__ == "__main__":
    main()
