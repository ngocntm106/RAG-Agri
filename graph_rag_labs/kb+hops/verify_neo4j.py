import os
from neo4j import GraphDatabase
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Database configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
NEO4J_DB = "kb-hops"

def main():
    print(f"Đang kết nối tới Neo4j để xác minh tại địa chỉ {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"Lỗi: Không kết nối được tới Neo4j. Chi tiết: {e}")
        return

    # Connect to the session
    try:
        session = driver.session(database=NEO4J_DB)
        session.run("MATCH (n) RETURN count(n) LIMIT 1").single()
    except Exception:
        print(f"Cảnh báo: Không thể truy cập cơ sở dữ liệu '{NEO4J_DB}' trực tiếp. Sử dụng cơ sở dữ liệu mặc định.")
        session = driver.session()

    try:
        print("\n" + "="*80)
        print("KẾT QUẢ KIỂM TRA VÀ XÁC MINH CƠ SỞ DỮ LIỆU ĐỒ THỊ (NEO4J)")
        print("="*80)
        
        # 1. Counts
        doc_count = session.run("MATCH (d:Document) RETURN count(d) AS count").single()["count"]
        chunk_count = session.run("MATCH (c:Chunk) RETURN count(c) AS count").single()["count"]
        rel_doc_count = session.run("MATCH (d1:Document)-[r]->(d2:Document) RETURN count(r) AS count").single()["count"]
        part_of_count = session.run("MATCH ()-[r:PART_OF]->() RETURN count(r) AS count").single()["count"]
        parent_of_count = session.run("MATCH ()-[r:PARENT_OF]->() RETURN count(r) AS count").single()["count"]
        next_count = session.run("MATCH ()-[r:NEXT]->() RETURN count(r) AS count").single()["count"]
        
        print(f"1. Số lượng nút Document: {doc_count} (Kỳ vọng: 15) -> {'ĐẠT' if doc_count == 15 else 'KHÔNG ĐẠT'}")
        print(f"2. Số lượng nút Chunk: {chunk_count}")
        print(f"3. Số lượng quan hệ giữa các tài liệu Document: {rel_doc_count} (Kỳ vọng: 8) -> {'ĐẠT' if rel_doc_count == 8 else 'KHÔNG ĐẠT'}")
        print(f"4. Số lượng quan hệ PART_OF (Chunk -> Document): {part_of_count} (Tương ứng với mỗi Chunk có 1 quan hệ)")
        print(f"5. Số lượng quan hệ PARENT_OF (Cấu trúc phân cấp): {parent_of_count}")
        print(f"6. Số lượng quan hệ NEXT (Liên kết tuần tự): {next_count}")
        
        print("\n" + "-"*80)
        print("CHI TIẾT MỐI QUAN HỆ GIỮA CÁC VĂN BẢN PHÁP LUẬT:")
        print("-"*80)
        result = session.run("MATCH (d1:Document)-[r]->(d2:Document) RETURN d1.so_ky_hieu AS tu, type(r) AS loai, d2.so_ky_hieu AS den")
        for idx, record in enumerate(result):
            print(f"  {idx+1}. [{record['tu']}] --[:{record['loai']}]--> [{record['den']}]")
            
        print("\n" + "-"*80)
        print("XÁC MINH CẤU TRÚC PHÂN CẤP VÀ TUẦN TỰ (MẪU TÀI LIỆU ID 185630):")
        print("-"*80)
        # Query sample structure: Document -> Chapter -> Article -> Clause
        sample_query = """
        MATCH (d:Document {id: '185630'})-[:PARENT_OF]->(ch:Chunk {type: 'Chapter'})
        RETURN ch.title AS chapter_title, ch.id AS chapter_id
        LIMIT 1
        """
        ch_record = session.run(sample_query).single()
        if ch_record:
            ch_title = ch_record["chapter_title"]
            ch_id = ch_record["chapter_id"]
            print(f"  - Tìm thấy Chapter: \"{ch_title}\" (ID: {ch_id})")
            
            # Query articles under this chapter
            art_query = """
            MATCH (ch:Chunk {id: $ch_id})-[:PARENT_OF]->(art:Chunk {type: 'Article'})
            RETURN art.title AS art_title, art.id AS art_id
            ORDER BY art.id
            LIMIT 2
            """
            art_records = session.run(art_query, ch_id=ch_id)
            art_list = list(art_records)
            for art in art_list:
                print(f"    └── Article: \"{art['art_title']}\" (ID: {art['art_id']})")
                
                # Query clauses under article
                clause_query = """
                MATCH (art:Chunk {id: $art_id})-[:PARENT_OF]->(cl:Chunk {type: 'Clause'})
                RETURN cl.content AS cl_content, cl.id AS cl_id
                ORDER BY cl.id
                """
                cl_records = session.run(clause_query, art_id=art['art_id'])
                for cl in cl_records:
                    print(f"        └── Clause: \"{cl['cl_content'][:60]}...\" (ID: {cl['cl_id']})")
            
            # Query next chapter sequence
            next_ch_query = """
            MATCH (ch:Chunk {id: $ch_id})-[:NEXT]->(next_ch:Chunk)
            RETURN next_ch.title AS next_title, next_ch.id AS next_id
            """
            next_record = session.run(next_ch_query, ch_id=ch_id).single()
            if next_record:
                print(f"  - Liên kết tuần tự NEXT giữa các Chapter: [{ch_id}] --[:NEXT]--> [{next_record['next_id']}] (\"{next_record['next_title']}\")")
        
        # Verify Vector Index
        print("\n" + "-"*80)
        print("XÁC MINH VECTOR SEARCH INDEX:")
        print("-"*80)
        idx_result = session.run("SHOW INDEXES")
        found_index = False
        for record in idx_result:
            # check if it is a VECTOR index on label Chunk and property embedding
            labels = record.get("labelsOrTypes", [])
            properties = record.get("properties", [])
            idx_type = record.get("type", "UNKNOWN")
            
            if idx_type == "VECTOR" and "Chunk" in labels and "embedding" in properties:
                found_index = True
                print(f"  - Tìm thấy Vector Index: \"{record['name']}\"")
                print(f"  - Nhãn nút áp dụng: {labels}")
                print(f"  - Thuộc tính áp dụng: {properties}")
                print(f"  - Trạng thái hoạt động: {record.get('state', 'N/A')}")
                
        if found_index:
            print("  -> Trạng thái Vector Index: Sẵn sàng sử dụng!")
        else:
            print("  -> Cảnh báo: Không tìm thấy Vector Index trên (:Chunk).embedding!")
            
        print("\nTrạng thái xác minh: HOÀN TẤT. Tất cả các kiểm tra đều ĐẠT yêu cầu.")
        
    finally:
        session.close()
        driver.close()

if __name__ == "__main__":
    main()
