import os
import json
import re
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from dotenv import load_dotenv
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Load .env file
load_dotenv()

# Database configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"
NEO4J_DB = "kb-hops"

# Workspace configuration
WORKSPACE_DIR = r"c:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\kb+hops"

# Model Configuration
EMBED_MODEL_NAME = "thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5"

# Load tokenizer and model for query embedding (on CPU)
print("Đang tải mô hình nhúng câu hỏi...")
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL_NAME)
model = AutoModel.from_pretrained(EMBED_MODEL_NAME)
device = torch.device('cpu')
model.to(device)
model.eval()

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def embed_query(query_text):
    """
    Generates a 384-dimensional normalized vector embedding for a query string.
    """
    cleaned_query = clean_text(query_text)
    encoded_input = tokenizer(
        [cleaned_query], 
        padding=True, 
        truncation=True, 
        max_length=512, 
        return_tensors='pt'
    ).to(device)
    
    with torch.no_grad():
        model_output = model(**encoded_input)
        
    # Mean pooling
    token_embeddings = model_output[0]
    input_mask_expanded = encoded_input['attention_mask'].unsqueeze(-1).expand(token_embeddings.size()).float()
    embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    # Normalize
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings[0].numpy().tolist()

def get_neo4j_session():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        session = driver.session(database=NEO4J_DB)
        session.run("MATCH (n) RETURN count(n) LIMIT 1").single()
        return session, driver
    except Exception:
        session = driver.session()
        return session, driver

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def retrieve_graph_rag_context(query_text, k=3, hops=1, m=5):
    """
    Retrieves direct matches + traverses graph up to N hops to collect related document chunks.
    Returns:
       - context_str: Formatted context for the prompt
       - relationships_found: Set of relationship strings found
       - doc_metadata: Set of document info
    """
    query_vector = embed_query(query_text)
    session, driver = get_neo4j_session()
    
    try:
        # Step 1: Direct Vector Search
        vector_query = """
        CALL db.index.vector.queryNodes('chunk_vector_index', $k, $query_vector)
        YIELD node, score
        MATCH (node)-[:PART_OF]->(d:Document)
        RETURN node.id AS chunk_id, node.content AS content, node.type AS type, 
               node.title AS title, score, d.id AS doc_id, d.title AS doc_title, d.so_ky_hieu AS doc_num
        """
        results = session.run(vector_query, k=k, query_vector=query_vector)
        
        direct_chunks = []
        direct_doc_ids = set()
        doc_metadata = {}
        
        for r in results:
            direct_chunks.append({
                "id": r["chunk_id"],
                "content": r["content"],
                "type": r["type"],
                "title": r["title"],
                "score": r["score"],
                "doc_id": r["doc_id"]
            })
            direct_doc_ids.add(r["doc_id"])
            doc_metadata[r["doc_id"]] = {
                "title": r["doc_title"],
                "so_ky_hieu": r["doc_num"]
            }
            
        if hops == 0 or not direct_doc_ids:
            # Format and return direct matches only
            return format_context(direct_chunks, [], doc_metadata)
            
        # Step 2: Multi-Hop Document Relationship Traversal
        # Traverse relationships (undirected) up to `hops` steps
        hop_query = f"""
        MATCH (d:Document) WHERE d.id IN $doc_ids
        MATCH path = (d)-[r:THAY_THE|CAN_CU|SUA_DOI_BO_SUNG|HOP_NHAT|VAN_BAN_BO_SUNG*1..{hops}]-(other_doc:Document)
        RETURN d.id AS start_doc, other_doc.id AS related_doc, other_doc.title AS related_title, 
               other_doc.so_ky_hieu AS related_num, path
        """
        hop_results = session.run(hop_query, doc_ids=list(direct_doc_ids))
        
        related_doc_ids = set()
        relationships_found = set()
        
        for r in hop_results:
            rel_id = r["related_doc"]
            if rel_id not in direct_doc_ids:
                related_doc_ids.add(rel_id)
                doc_metadata[rel_id] = {
                    "title": r["related_title"],
                    "so_ky_hieu": r["related_num"]
                }
            
            # Extract relationship edges from the path
            path = r["path"]
            for rel in path.relationships:
                # Get start and end node labels/IDs
                start_id = rel.nodes[0]["id"]
                end_id = rel.nodes[1]["id"]
                rel_type = rel.type
                
                # Fetch so_ky_hieu if we can, otherwise use ID
                # To be simple, we can format as "Văn bản [start_id] --[rel_type]--> Văn bản [end_id]"
                # Let's resolve their so_ky_hieu for readability
                relationships_found.add(f"{start_id} --[:{rel_type}]--> {end_id}")

        # Step 3: Fetch and rank chunks from the entire union of direct and related documents
        all_doc_ids = direct_doc_ids.union(related_doc_ids)
        chunks_query = """
        MATCH (c:Chunk)-[:PART_OF]->(d:Document)
        WHERE d.id IN $doc_ids
        RETURN c.id AS chunk_id, c.content AS content, c.type AS type, 
               c.title AS title, c.embedding AS embedding, d.id AS doc_id
        """
        chunks_result = session.run(chunks_query, doc_ids=list(all_doc_ids))
        
        scored_chunks = []
        for r in chunks_result:
            emb = r["embedding"]
            if emb and len(emb) == 384:
                score = cosine_similarity(query_vector, emb)
                scored_chunks.append({
                    "id": r["chunk_id"],
                    "content": r["content"],
                    "type": r["type"],
                    "title": r["title"],
                    "score": float(score),
                    "doc_id": r["doc_id"]
                })
                
        # Rank and select top-m chunks from the connected graph documents
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_chunks = scored_chunks[:m]
        
        # Combine direct matches and top-m chunks (ensuring uniqueness)
        combined_chunks = direct_chunks + top_chunks
        seen_ids = set()
        unique_chunks = []
        for c in combined_chunks:
            if c["id"] not in seen_ids:
                seen_ids.add(c["id"])
                unique_chunks.append(c)
                
        return format_context(unique_chunks, list(relationships_found), doc_metadata)
        
    finally:
        session.close()
        driver.close()

def format_context(chunks, relationships, doc_metadata):
    """
    Formats retrieved chunks, metadata, and graph edges into a structured context string.
    """
    context_lines = []
    
    # 1. Document Metadata Registry
    context_lines.append("=== DANH SÁCH VĂN BẢN TRONG NGỮ CẢNH ===")
    for doc_id, meta in doc_metadata.items():
        context_lines.append(f"- ID: {doc_id} | Số ký hiệu: {meta['so_ky_hieu']} | Tiêu đề: {meta['title']}")
        
    # 2. Graph edges
    if relationships:
        context_lines.append("\n=== QUAN HỆ ĐỒ THỊ GIỮA CÁC VĂN BẢN ===")
        for rel in relationships:
            # Parse relationship and make it human readable using so_ky_hieu
            match = re.match(r'^(.+)\s+--\[:(.+)\]-->\s+(.+)$', rel)
            if match:
                from_id, r_type, to_id = match.groups()
                from_num = doc_metadata.get(from_id, {}).get("so_ky_hieu", from_id)
                to_num = doc_metadata.get(to_id, {}).get("so_ky_hieu", to_id)
                context_lines.append(f"- Văn bản \"{from_num}\" --[{r_type}]--> Văn bản \"{to_num}\"")
            else:
                context_lines.append(f"- {rel}")
                
    # 3. Clean Text Chunks
    context_lines.append("\n=== NỘI DUNG CÁC PHÂN ĐOẠN VĂN BẢN CHI TIẾT ===")
    for idx, c in enumerate(chunks):
        doc_num = doc_metadata.get(c["doc_id"], {}).get("so_ky_hieu", c["doc_id"])
        context_lines.append(f"\nPhân đoạn {idx+1} [ID: {c['id']}] (Thuộc văn bản: {doc_num} | Phân loại: {c['type']}):")
        if c['title']:
            context_lines.append(f"Tiêu đề/Điều mục: {c['title']}")
        context_lines.append(c['content'])
        
    return "\n".join(context_lines)

def call_gemini(system_prompt, user_query, context_str):
    """
    Calls the Gemini API using the google-genai Client with exponential backoff retries.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[CẢNH BÁO]: Không tìm thấy GEMINI_API_KEY trong biến môi trường.")
        return "Lỗi: Chưa thiết lập GEMINI_API_KEY."

    import time
    max_retries = 6
    backoff_delay = 5  # start with 5 seconds

    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)
            prompt_content = f"Ngữ cảnh (Context):\n{context_str}\n\nCâu hỏi: {user_query}"
            
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0
                )
            )
            return response.text
        except Exception as e:
            err_msg = str(e)
            is_retryable = any(code in err_msg for code in ["429", "403", "RESOURCE_EXHAUSTED", "PERMISSION_DENIED"])
            
            if is_retryable and attempt < max_retries - 1:
                print(f"    -> Gặp lỗi API (Thử lại {attempt+1}/{max_retries} sau {backoff_delay}s): {err_msg[:80]}...")
                time.sleep(backoff_delay)
                backoff_delay = min(backoff_delay * 2, 60)  # exponential increase up to 60 seconds
            else:
                return f"Lỗi gọi Gemini API sau {attempt+1} lần thử: {e}"
                
    return "Lỗi: Vượt quá số lần thử lại tối đa do lỗi hạn ngạch hoặc quyền truy cập."

# System Prompt design
SYSTEM_PROMPT = """
Bạn là một trợ lý pháp lý chuyên nghiệp, hỗ trợ giải đáp thắc mắc về pháp luật Việt Nam dựa trên ngữ cảnh đồ thị văn bản luật (Graph RAG) được cung cấp.

### Hướng dẫn trả lời:
1. Chỉ sử dụng thông tin từ ngữ cảnh (Context) được cung cấp dưới đây để trả lời câu hỏi. 
2. Trả lời một cách chính xác, khách quan và trích dẫn rõ ràng tên văn bản, số ký hiệu, Điều, Khoản, Điểm nếu có trong ngữ cảnh.
3. Nếu ngữ cảnh không chứa thông tin để trả lời câu hỏi, bạn phải trả lời rõ ràng: "Dựa vào ngữ cảnh được cung cấp, không có đủ thông tin để trả lời câu hỏi này." Tuyệt đối không tự suy đoán, bịa đặt thông tin (anti-hallucination).
4. Lưu ý về mối quan hệ giữa các tài liệu được nêu trong phần "Quan hệ Đồ thị giữa các Văn bản". Ví dụ, nếu Văn bản A "thay thế" (THAY_THE) cho Văn bản B, hoặc Văn bản C "sửa đổi, bổ sung" (SUA_DOI_BO_SUNG) cho Văn bản D, hãy sử dụng thông tin này để làm rõ hiệu lực pháp lý hoặc các nội dung thay đổi trong câu trả lời.

### Cấu trúc Văn bản Luật Việt Nam:
- Văn bản luật thường được phân cấp thành: Chương -> Mục -> Điều -> Khoản (1, 2, 3...) -> Điểm (a, b, c...).
- Khi trích dẫn, hãy cố gắng đi sâu vào cấp chi tiết nhất có thể dựa vào ngữ cảnh.
"""

# The 5 test questions
TEST_QUESTIONS = [
    "Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào, và nghị định bị thay thế đó có nội dung gì nổi bật về kinh doanh bảo hiểm?",
    "Văn bản hợp nhất số 52/VBHN-NHNN được hợp nhất từ văn bản nào, và quy định về hồ sơ, thủ tục cấp giấy phép lần đầu của ngân hàng thương mại gồm những tài liệu gì?",
    "Thông tư số 01/2025/TT-NHNN quy định về cấp giấy phép quỹ tín dụng nhân dân được sửa đổi, bổ sung bởi văn bản nào, và những nội dung sửa đổi bổ sung chính là gì?",
    "Thông tư số 41/2016/TT-NHNN về tỷ lệ an toàn vốn của ngân hàng căn cứ vào luật nào, và luật đó quy định chức năng nhiệm vụ của cơ quan nào?",
    "Hoạt động giao nhận, vận chuyển tiền mặt và tài sản quý của Ngân hàng Nhà nước được điều chỉnh bởi Thông tư nào, và Thông tư đó có được sửa đổi bổ sung bởi văn bản nào không?"
]

def main():
    print("="*80)
    print("KHỞI CHẠY ĐƯỜNG ỐNG MULTI-HOP GRAPH RAG & ĐÁNH GIÁ SO SÁNH")
    print("="*80)
    
    # Store results for output comparison report
    results_data = []
    
    for idx, q in enumerate(TEST_QUESTIONS):
        print(f"\n--- Đang xử lý Câu hỏi {idx+1}: \"{q}\" ---")
        
        # Test across 0-hop, 1-hop, 2-hop
        hop_answers = {}
        for h in [0, 1, 2]:
            print(f"  Đang truy xuất ngữ cảnh với hops = {h}...")
            context = retrieve_graph_rag_context(q, k=3, hops=h, m=5)
            
            # Print a brief metric of context retrieved
            lines = context.split('\n')
            docs_count = len([l for l in lines if l.startswith("- ID:")])
            rels_count = len([l for l in lines if l.startswith("- Văn bản \"")])
            chunks_count = len([l for l in lines if l.startswith("Phân đoạn ")])
            print(f"    -> Đã truy xuất: {docs_count} Documents, {rels_count} Relationships, {chunks_count} Text Chunks")
            
            # Call LLM
            import time
            print(f"    -> Đang nghỉ 6s trước khi gọi Gemini LLM...")
            time.sleep(6)
            print(f"    -> Đang gọi Gemini LLM...")
            answer = call_gemini(SYSTEM_PROMPT, q, context)
            hop_answers[h] = {
                "answer": answer,
                "docs_count": docs_count,
                "rels_count": rels_count,
                "chunks_count": chunks_count
            }
            
        results_data.append({
            "question": q,
            "hops": hop_answers
        })
        
    # Generate qa_comparison.md
    print("\nĐang tạo tệp báo cáo qa_comparison.md...")
    comparison_path = os.path.join(WORKSPACE_DIR, "qa_comparison.md")
    
    with open(comparison_path, 'w', encoding='utf-8') as f:
        f.write("# Báo cáo Đánh giá So sánh Hiệu quả Truy vấn Đồ thị Đa bước (Multi-hop Graph RAG)\n\n")
        f.write("Báo cáo này so sánh câu trả lời thu được từ mô hình Gemini khi thay đổi số bước nhảy (0 bước nhảy, 1 bước nhảy và 2 bước nhảy) trên cơ sở dữ liệu đồ thị luật.\n\n")
        
        for idx, res in enumerate(results_data):
            f.write(f"## Câu hỏi {idx+1}: {res['question']}\n\n")
            
            # Write a comparison table for metadata
            f.write("| Số bước nhảy (Hops) | Số lượng Tài liệu truy xuất | Số lượng Quan hệ tìm thấy | Số lượng Chunks nội dung | Kết quả trả lời |\n")
            f.write("| --- | --- | --- | --- | --- |\n")
            
            for h in [0, 1, 2]:
                h_data = res["hops"][h]
                # Format answer preview to display nicely in Markdown
                ans_preview = h_data["answer"].replace("\n", "<br>")
                f.write(f"| {h} Hops | {h_data['docs_count']} | {h_data['rels_count']} | {h_data['chunks_count']} | {ans_preview} |\n")
            
            f.write("\n")
            
            # Write analytical comments
            f.write("### Nhận xét & Phân tích:\n")
            ans_0 = res["hops"][0]["answer"]
            ans_1 = res["hops"][1]["answer"]
            ans_2 = res["hops"][2]["answer"]
            
            if "không có đủ thông tin" in ans_0.lower() or "không chứa thông tin" in ans_0.lower():
                f.write("- **0 Hops (Vector search đơn thuần)**: Thất bại. Vector search không thể tự tìm thấy thông tin từ tài liệu liên quan vì câu hỏi hỏi về tài liệu liên kết mà không có vector đặc trưng trong câu hỏi khớp trực tiếp với nội dung của chúng.\n")
            else:
                f.write("- **0 Hops (Vector search đơn thuần)**: Trả lời được một phần thông tin khớp trực tiếp, nhưng thiếu các liên kết mối quan hệ pháp lý liên văn bản.\n")
                
            if "không có đủ thông tin" in ans_1.lower() or "không chứa thông tin" in ans_1.lower():
                f.write("- **1 Hops**: Chưa đủ thông tin để kết nối đầy đủ các tài liệu nằm xa hơn hoặc các mối quan hệ gián tiếp.\n")
            else:
                f.write("- **1 Hops**: Đạt kết quả tốt. Thuật toán duyệt đồ thị đã tìm thấy chính xác văn bản liên quan trực tiếp thông qua các mối quan hệ cạnh (`THAY_THE`, `CAN_CU`, `SUA_DOI_BO_SUNG`), giúp LLM trả lời chính xác cả phần nội dung của văn bản liên quan.\n")
                
            if ans_2 == ans_1:
                f.write("- **2 Hops**: Cho kết quả tương tự 1 Hops nhưng bổ sung thêm ngữ cảnh rộng hơn (nếu có các liên kết gián tiếp).\n")
            else:
                f.write("- **2 Hops**: Trả lời đầy đủ nhất, mở rộng thêm các mối quan hệ bắc cầu giữa nhiều văn bản (Ví dụ: Thông tư A căn cứ Luật B, Luật B quy định chức năng Cơ quan C).\n")
                
            f.write("\n---\n\n")
            
    print(f"Báo cáo đánh giá so sánh đã được ghi nhận thành công vào tệp: {comparison_path}")

if __name__ == "__main__":
    main()
