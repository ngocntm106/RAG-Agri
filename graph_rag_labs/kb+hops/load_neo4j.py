import os
import json
import pandas as pd
import re
from neo4j import GraphDatabase
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Database configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"  # Default password, can be changed by the user
NEO4J_DB = "kb-hops"         # Name of the database specified in the requirements

# Paths
WORKSPACE_DIR = r"c:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\kb+hops"
METADATA_CSV = os.path.join(WORKSPACE_DIR, "metadata.csv")
RELATIONSHIPS_CSV = os.path.join(WORKSPACE_DIR, "relationships.csv")
CHUNKS_WITH_EMBEDDINGS_JSON = os.path.join(WORKSPACE_DIR, "chunks_with_embeddings.json")

def clean_dict(d):
    """
    Helper to clean dict values for Neo4j compatibility (replace NaN/NaT with empty strings).
    """
    cleaned = {}
    for k, v in d.items():
        if pd.isna(v):
            cleaned[k] = ""
        else:
            cleaned[k] = v
    return cleaned

def create_vector_index(session):
    """
    Creates a vector search index on the 'embedding' property of 'Chunk' nodes.
    """
    print("Đang cấu hình Vector Index cho thuộc tính embedding của nút Chunk...")
    # Neo4j 5.x Vector Index syntax
    create_index_query = """
    CREATE VECTOR INDEX chunk_embeddings_idx IF NOT EXISTS
    FOR (c:Chunk) ON (c.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 384,
      `vector.similarity_function`: 'cosine'
    }}
    """
    try:
        session.run(create_index_query)
        print("Đã tạo hoặc kiểm tra thành công Vector Index: chunk_embeddings_idx")
    except Exception as e:
        print(f"Lưu ý: Không tạo được Vector Index tự động (có thể do phiên bản Neo4j cũ hơn): {e}")
        print("Bạn có thể cần tạo chỉ mục thủ công bằng lệnh thích hợp với phiên bản Neo4j của bạn.")

def load_data():
    # 1. Load data files
    print("Đang đọc dữ liệu metadata.csv...")
    if not os.path.exists(METADATA_CSV):
        print(f"Lỗi: Không tìm thấy {METADATA_CSV}")
        return
    meta_df = pd.read_csv(METADATA_CSV)
    
    print("Đang đọc dữ liệu relationships.csv...")
    if not os.path.exists(RELATIONSHIPS_CSV):
        print(f"Lỗi: Không tìm thấy {RELATIONSHIPS_CSV}")
        return
    rel_df = pd.read_csv(RELATIONSHIPS_CSV)
    
    print("Đang đọc dữ liệu chunks_with_embeddings.json...")
    if not os.path.exists(CHUNKS_WITH_EMBEDDINGS_JSON):
        print(f"Lỗi: Không tìm thấy {CHUNKS_WITH_EMBEDDINGS_JSON}. Vui lòng chạy Bước 2 trước.")
        return
    with open(CHUNKS_WITH_EMBEDDINGS_JSON, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    print(f"Đã đọc: {len(meta_df)} documents, {len(rel_df)} document relationships, và {len(chunks)} chunks.")
    
    # Connect to Neo4j
    print(f"Đang kết nối tới Neo4j tại địa chỉ {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        print(f"Lỗi: Không kết nối được tới Neo4j. Chi tiết: {e}")
        print("Vui lòng kiểm tra lại dịch vụ Neo4j và cấu hình tài khoản/mật khẩu.")
        return

    # Use database if configured, or default database
    # Check if database kb-hops exists, or just run on standard database session
    try:
        session = driver.session(database=NEO4J_DB)
        # Quick query to test if database works
        session.run("MATCH (n) RETURN count(n) LIMIT 1").single()
    except Exception:
        print(f"Cảnh báo: Không thể truy cập cơ sở dữ liệu '{NEO4J_DB}' trực tiếp. Sẽ sử dụng cơ sở dữ liệu mặc định của hệ thống.")
        session = driver.session()

    try:
        # Clear existing data in database
        print("Đang dọn dẹp dữ liệu cũ trong cơ sở dữ liệu...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # 2. Ingest (:Document) nodes
        print("Đang nạp các nút Document...")
        doc_batch = []
        for _, row in meta_df.iterrows():
            props = clean_dict(row.to_dict())
            props['id'] = str(props['id'])
            doc_batch.append(props)
            
        doc_query = """
        UNWIND $batch AS doc
        MERGE (d:Document {id: doc.id})
        SET d += doc
        """
        session.run(doc_query, batch=doc_batch)
        print(f"  Đã nạp {len(doc_batch)} tài liệu (Document).")
        
        # 3. Ingest document relationships
        print("Đang nạp mối quan hệ giữa các tài liệu Document...")
        # Group relationships by relationship_type to run parameterized queries
        rel_groups = {}
        for _, row in rel_df.iterrows():
            r_type = str(row['relationship_type']).strip()
            # Clean type
            r_type = re.sub(r'[^a-zA-Z0-9_]', '', r_type)
            if r_type not in rel_groups:
                rel_groups[r_type] = []
            rel_groups[r_type].append({
                "doc_id": str(row['doc_id']),
                "other_doc_id": str(row['other_doc_id'])
            })
            
        for r_type, rel_list in rel_groups.items():
            rel_query = f"""
            UNWIND $batch AS item
            MATCH (d1:Document {{id: item.doc_id}})
            MATCH (d2:Document {{id: item.other_doc_id}})
            MERGE (d1)-[:{r_type}]->(d2)
            """
            session.run(rel_query, batch=rel_list)
            print(f"  Đã nạp {len(rel_list)} quan hệ loại: {r_type}")
            
        # 4. Ingest (:Chunk) nodes
        print("Đang nạp các nút Chunk...")
        chunk_batch = []
        for c in chunks:
            chunk_batch.append({
                "id": str(c['id']),
                "content": str(c.get('content', '') or ''),
                "title": str(c.get('title', '') or ''),
                "type": str(c.get('type', '') or ''),
                "embedding": c.get('embedding', [])
            })
            
        chunk_query = """
        UNWIND $batch AS item
        MERGE (c:Chunk {id: item.id})
        SET c.content = item.content,
            c.title = item.title,
            c.type = item.type,
            c.embedding = item.embedding
        """
        # Execute chunk insertion in batches of 1000 to keep transaction memory low
        chunk_batch_size = 1000
        for i in range(0, len(chunk_batch), chunk_batch_size):
            sub_batch = chunk_batch[i : i + chunk_batch_size]
            session.run(chunk_query, batch=sub_batch)
        print(f"  Đã nạp {len(chunk_batch)} phân đoạn (Chunk).")
        
        # 5. Ingest [:PART_OF] relationships (Chunk -> Document)
        print("Đang nạp mối quan hệ [:PART_OF]...")
        part_of_batch = []
        for c in chunks:
            part_of_batch.append({
                "chunk_id": str(c['id']),
                "doc_id": str(c['doc_id'])
            })
            
        part_of_query = """
        UNWIND $batch AS item
        MATCH (c:Chunk {id: item.chunk_id})
        MATCH (d:Document {id: item.doc_id})
        MERGE (c)-[:PART_OF]->(d)
        """
        for i in range(0, len(part_of_batch), chunk_batch_size):
            sub_batch = part_of_batch[i : i + chunk_batch_size]
            session.run(part_of_query, batch=sub_batch)
        print(f"  Đã tạo các quan hệ PART_OF.")
        
        # 6. Ingest [:PARENT_OF] relationships (hierarchical structure)
        print("Đang nạp mối quan hệ [:PARENT_OF]...")
        parent_of_doc_batch = [] # Parent is Document
        parent_of_chunk_batch = [] # Parent is Chunk
        
        # All documents from meta_df
        existing_doc_ids = set(meta_df['id'].astype(str).tolist())
        
        for c in chunks:
            parent_id = c.get('parent_id')
            if not parent_id:
                continue
                
            item = {
                "parent_id": str(parent_id),
                "child_id": str(c['id'])
            }
            if parent_id in existing_doc_ids:
                parent_of_doc_batch.append(item)
            else:
                parent_of_chunk_batch.append(item)
                
        parent_doc_query = """
        UNWIND $batch AS item
        MATCH (parent:Document {id: item.parent_id})
        MATCH (child:Chunk {id: item.child_id})
        MERGE (parent)-[:PARENT_OF]->(child)
        """
        for i in range(0, len(parent_of_doc_batch), chunk_batch_size):
            sub_batch = parent_of_doc_batch[i : i + chunk_batch_size]
            session.run(parent_doc_query, batch=sub_batch)
            
        parent_chunk_query = """
        UNWIND $batch AS item
        MATCH (parent:Chunk {id: item.parent_id})
        MATCH (child:Chunk {id: item.child_id})
        MERGE (parent)-[:PARENT_OF]->(child)
        """
        for i in range(0, len(parent_of_chunk_batch), chunk_batch_size):
            sub_batch = parent_of_chunk_batch[i : i + chunk_batch_size]
            session.run(parent_chunk_query, batch=sub_batch)
            
        print(f"  Đã tạo các quan hệ PARENT_OF (tổng cộng {len(parent_of_doc_batch) + len(parent_of_chunk_batch)} quan hệ).")
        
        # 7. Ingest [:NEXT] relationships (sibling sequential reader flow)
        print("Đang nạp mối quan hệ [:NEXT]...")
        next_batch = []
        for c in chunks:
            next_id = c.get('next_id')
            if next_id:
                next_batch.append({
                    "c1_id": str(c['id']),
                    "c2_id": str(next_id)
                })
                
        next_query = """
        UNWIND $batch AS item
        MATCH (c1:Chunk {id: item.c1_id})
        MATCH (c2:Chunk {id: item.c2_id})
        MERGE (c1)-[:NEXT]->(c2)
        """
        for i in range(0, len(next_batch), chunk_batch_size):
            sub_batch = next_batch[i : i + chunk_batch_size]
            session.run(next_query, batch=sub_batch)
        print(f"  Đã tạo các quan hệ NEXT (tổng cộng {len(next_batch)} quan hệ).")

        # 8. Create Vector Search Index
        create_vector_index(session)
        
        # Verification Summary
        print("\n" + "="*80)
        print("KẾT QUẢ NẠP DỮ LIỆU VÀO CƠ SỞ DỮ LIỆU ĐỒ THỊ NEO4J:")
        print("="*80)
        
        doc_count = session.run("MATCH (d:Document) RETURN count(d) AS count").single()["count"]
        chunk_count = session.run("MATCH (c:Chunk) RETURN count(c) AS count").single()["count"]
        rel_doc_count = session.run("MATCH (d1:Document)-[r]->(d2:Document) RETURN count(r) AS count").single()["count"]
        part_of_count = session.run("MATCH ()-[r:PART_OF]->() RETURN count(r) AS count").single()["count"]
        parent_of_count = session.run("MATCH ()-[r:PARENT_OF]->() RETURN count(r) AS count").single()["count"]
        next_count = session.run("MATCH ()-[r:NEXT]->() RETURN count(r) AS count").single()["count"]
        
        print(f"Số lượng nút Document: {doc_count} (Kỳ vọng: 15)")
        print(f"Số lượng nút Chunk: {chunk_count}")
        print(f"Số lượng quan hệ giữa các tài liệu Document: {rel_doc_count} (Kỳ vọng: 8)")
        print(f"Số lượng quan hệ PART_OF: {part_of_count}")
        print(f"Số lượng quan hệ PARENT_OF: {parent_of_count}")
        print(f"Số lượng quan hệ NEXT: {next_count}")
        
        print("\nChi tiết quan hệ giữa các tài liệu Document:")
        result = session.run("MATCH (d1:Document)-[r]->(d2:Document) RETURN type(r) AS type, count(r) AS count")
        for record in result:
            print(f"  - [{record['type']}]: {record['count']}")
            
        print("\nTrạng thái: Hoàn tất nạp dữ liệu vào cơ sở dữ liệu Neo4j.")
        
    finally:
        session.close()
        driver.close()

if __name__ == "__main__":
    load_data()
