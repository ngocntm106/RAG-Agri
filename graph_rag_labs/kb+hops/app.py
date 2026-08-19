import streamlit as st
import os
import time
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from google.genai.errors import ClientError

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Graph RAG Pháp Luật Việt Nam",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Theme & Glassmorphism UI)
st.markdown("""
<style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main {
        background-color: #0f1115;
        color: #e2e8f0;
    }
    
    /* Header Banner styling */
    .title-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    .title-banner h1 {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .title-banner p {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 0;
    }
    
    /* Card design for Graph Documents */
    .doc-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .doc-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
        box-shadow: 0 6px 15px rgba(56, 189, 248, 0.15);
    }
    
    .doc-card-title {
        color: #38bdf8;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 6px;
    }
    
    .doc-card-meta {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    
    /* Badges for relationships */
    .rel-badge {
        display: inline-block;
        background: rgba(129, 140, 248, 0.15);
        color: #818cf8;
        border: 1px solid rgba(129, 140, 248, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .rel-badge:hover {
        background: rgba(129, 140, 248, 0.25);
        border-color: #818cf8;
    }
    
    /* Answer box */
    .answer-box {
        background: rgba(30, 41, 59, 0.2);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #f1f5f9;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Initialize Session State
if "neo4j_connected" not in st.session_state:
    st.session_state.neo4j_connected = False
if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = None

# Sidebar Configurations
st.sidebar.title("⚙️ Cấu hình Hệ thống")

# 1. Neo4j connection parameters
st.sidebar.subheader("🔌 Kết nối Cơ sở dữ liệu")
neo4j_host = st.sidebar.text_input("Neo4j Host", value="localhost")
neo4j_port = st.sidebar.text_input("Neo4j Port", value="7687")
neo4j_user = st.sidebar.text_input("Tài khoản", value="neo4j")
neo4j_password = st.sidebar.text_input("Mật khẩu", value="12345678", type="password")
neo4j_db = st.sidebar.text_input("Database Name", value="kb-hops")

# Connection URL
neo4j_uri = f"bolt://{neo4j_host}:{neo4j_port}"

# Test connection button
if st.sidebar.button("Kiểm tra kết nối Neo4j"):
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session(database=neo4j_db) as session:
            # Simple test query
            res = session.run("MATCH (d:Document) RETURN count(d) AS count")
            doc_count = res.single()["count"]
            st.session_state.neo4j_connected = True
            st.sidebar.success(f"Kết nối thành công! Đang có {doc_count} tài liệu.")
        driver.close()
    except Exception as e:
        st.session_state.neo4j_connected = False
        st.sidebar.error(f"Lỗi kết nối: {str(e)[:150]}")

# 2. RAG parameters
st.sidebar.subheader("🔍 Cấu hình RAG")
val_k = st.sidebar.slider("Số phân đoạn khớp gốc (k)", min_value=1, max_value=10, value=3)
val_hops = st.sidebar.slider("Số bước nhảy đồ thị (N hops)", min_value=0, max_value=3, value=1)
val_m = st.sidebar.slider("Tổng số phân đoạn tổng hợp (m)", min_value=2, max_value=15, value=5)

# 3. Gemini key configuration
st.sidebar.subheader("🤖 Cấu hình Gemini")
api_key_env = os.environ.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key", value=api_key_env, type="password")
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

# Load Embeddings Model (cached resource)
@st.cache_resource(show_spinner="Đang tải mô hình nhúng câu hỏi (MiniLM)...")
def load_embed_model():
    model_name = "thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5"
    return SentenceTransformer(model_name)

try:
    if st.session_state.embedding_model is None:
        st.session_state.embedding_model = load_embed_model()
except Exception as e:
    st.error(f"Không thể tải mô hình nhúng: {e}")

# Helper: embed query
def get_query_embedding(text):
    if st.session_state.embedding_model is not None:
        return st.session_state.embedding_model.encode(text).tolist()
    return None

# Helper: compute cosine similarity
def cosine_similarity(v1, v2):
    import numpy as np
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))

# Multi-hop retrieval logic returning structured details
def run_multihop_retrieval(query_text, k, hops, m):
    query_vector = get_query_embedding(query_text)
    if not query_vector:
        return None, [], [], []
        
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    direct_chunks = []
    direct_doc_ids = set()
    related_doc_ids = set()
    relationships_found = []
    doc_metadata = {}
    
    with driver.session(database=neo4j_db) as session:
        # Step 1: Query direct matches
        vector_query = """
        CALL db.index.vector.queryNodes('chunk_vector_index', $k, $query_vector)
        YIELD node, score
        MATCH (node)-[:PART_OF]->(d:Document)
        RETURN node.id AS chunk_id, node.content AS content, node.type AS type, 
               node.title AS title, score, d.id AS doc_id, d.title AS doc_title, d.so_ky_hieu AS doc_num
        """
        try:
            res = session.run(vector_query, k=k, query_vector=query_vector)
            for record in res:
                doc_id = record["doc_id"]
                direct_doc_ids.add(doc_id)
                
                # Keep document metadata
                doc_metadata[doc_id] = {
                    "id": doc_id,
                    "title": record["doc_title"],
                    "so_ky_hieu": record["doc_num"]
                }
                
                direct_chunks.append({
                    "id": record["chunk_id"],
                    "content": record["content"],
                    "type": record["type"],
                    "title": record["title"],
                    "score": float(record["score"]),
                    "doc_id": doc_id
                })
        except Exception as e:
            st.error(f"Lỗi truy vấn Vector Neo4j: {e}")
            driver.close()
            return None, [], [], []

        # If no documents matched
        if not direct_doc_ids:
            driver.close()
            return "Không tìm thấy tài liệu phù hợp trong cơ sở dữ liệu.", [], [], []

        # Step 2: Traverse graph if hops > 0
        if hops > 0:
            graph_query = f"""
            MATCH (d1:Document)
            WHERE d1.id IN $direct_doc_ids
            MATCH path = (d1)-[r:CAN_CU|THAY_THE|SUA_DOI_BO_SUNG|HOP_NHAT|VAN_BAN_BO_SUNG*1..{hops}]-(d2:Document)
            RETURN d1.id AS start_id, d1.so_ky_hieu AS start_num,
                   d2.id AS end_id, d2.so_ky_hieu AS end_num, d2.title AS end_title,
                   [rel in relationships(path) | type(rel)] AS rel_types
            """
            graph_res = session.run(graph_query, direct_doc_ids=list(direct_doc_ids))
            
            for record in graph_res:
                end_id = record["end_id"]
                if end_id not in direct_doc_ids:
                    related_doc_ids.add(end_id)
                    doc_metadata[end_id] = {
                        "id": end_id,
                        "title": record["end_title"],
                        "so_ky_hieu": record["end_num"]
                    }
                
                start_id = record["start_id"]
                start_num = record["start_num"]
                end_num = record["end_num"]
                for rel_type in record["rel_types"]:
                    edge_str = f'"{start_num}" --[{rel_type}]--> "{end_num}"'
                    if edge_str not in relationships_found:
                        relationships_found.append(edge_str)

        # Step 3: Fetch and rank chunks from the union of all connected documents
        all_doc_ids = direct_doc_ids.union(related_doc_ids)
        chunks_query = """
        MATCH (c:Chunk)-[:PART_OF]->(d:Document)
        WHERE d.id IN $doc_ids
        RETURN c.id AS chunk_id, c.content AS content, c.type AS type, 
               c.title AS title, c.embedding AS embedding, d.id AS doc_id
        """
        chunks_res = session.run(chunks_query, doc_ids=list(all_doc_ids))
        
        scored_chunks = []
        for record in chunks_res:
            emb = record["embedding"]
            if emb and len(emb) == 384:
                score = cosine_similarity(query_vector, emb)
                scored_chunks.append({
                    "id": record["chunk_id"],
                    "content": record["content"],
                    "type": record["type"],
                    "title": record["title"],
                    "score": float(score),
                    "doc_id": record["doc_id"]
                })
                
        # Sort and select top-m chunks
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_chunks = scored_chunks[:m]
        
        # Combine direct matches and top-m (ensuring uniqueness)
        combined_chunks = direct_chunks + top_chunks
        seen_ids = set()
        unique_chunks = []
        for c in combined_chunks:
            if c["id"] not in seen_ids:
                seen_ids.add(c["id"])
                unique_chunks.append(c)
                
    driver.close()
    
    # Construct structured context text
    context_lines = []
    context_lines.append("=== DANH SÁCH VĂN BẢN TRONG NGỮ CẢNH ===")
    for d_id, meta in doc_metadata.items():
        doc_type_label = "Gốc (Direct)" if d_id in direct_doc_ids else "Liên quan (Related)"
        context_lines.append(f"- ID: {d_id} | Số ký hiệu: {meta['so_ky_hieu']} | Tiêu đề: {meta['title']} ({doc_type_label})")
        
    if relationships_found:
        context_lines.append("\n=== QUAN HỆ ĐỒ THỊ GIỮA CÁC VĂN BẢN ===")
        for rel in relationships_found:
            context_lines.append(f"- {rel}")
            
    context_lines.append("\n=== NỘI DUNG CÁC PHÂN ĐOẠN VĂN BẢN CHI TIẾT ===")
    for idx, c in enumerate(unique_chunks):
        meta = doc_metadata.get(c["doc_id"], {"so_ky_hieu": "Không rõ"})
        context_lines.append(f"\nPhân đoạn {idx+1} [ID: {c['id']}] (Thuộc văn bản: {meta['so_ky_hieu']} | Phân loại: {c['type']}):")
        context_lines.append(f"Tiêu đề/Điều mục: {c['title'] or 'Không có'}")
        context_lines.append(c["content"])
        
    context_text = "\n".join(context_lines)
    
    # Return context_text, document list, relationship list, and unique chunks for UI rendering
    return context_text, list(doc_metadata.values()), relationships_found, unique_chunks

# Gemini API wrapper with retries
def ask_gemini(system_prompt, user_query, context_str):
    api_key_val = os.environ.get("GEMINI_API_KEY")
    if not api_key_val:
        return "Lỗi: Vui lòng nhập Gemini API Key ở thanh cấu hình bên trái."
        
    max_retries = 5
    backoff_delay = 3
    
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key_val)
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
                time.sleep(backoff_delay)
                backoff_delay *= 2
            else:
                return f"Lỗi gọi Gemini API sau {attempt+1} lần thử: {e}"
                
    return "Lỗi: Vượt quá số lần thử tối đa do lỗi hạn ngạch hoặc quyền truy cập."

# Legal QA prompt template
SYSTEM_PROMPT = """
Bạn là một chuyên gia trợ lý pháp luật cao cấp của Việt Nam, được thiết kế để trả lời các câu hỏi về luật pháp một cách cực kỳ chính xác dựa trên ngữ cảnh cấu trúc đồ thị được cung cấp.

HƯỚNG DẪN TRẢ LỜI:
1. TRỰC TIẾP & CHÍNH XÁC: Chỉ trả lời các câu hỏi dựa trên thông tin có sẵn trong Ngữ cảnh (Context). Trả lời mạch lạc, trích dẫn rõ ràng số ký hiệu văn bản, tên điều khoản.
2. KHÔNG SUY ĐOÁN: Nếu Ngữ cảnh không chứa đủ thông tin để trả lời câu hỏi, bạn phải nói rõ: "Ngữ cảnh được cung cấp không chứa thông tin về..." thay vì cố tự bịa ra thông tin. Việc bịa đặt hoặc tự suy diễn thông tin nằm ngoài ngữ cảnh là KHÔNG CHẤP NHẬN ĐƯỢC.
3. PHÂN TÍCH ĐA BƯỚC: Nếu ngữ cảnh hiển thị các mối quan hệ đồ thị giữa các văn bản (ví dụ: Thay thế, Sửa đổi bổ sung, Căn cứ pháp lý), hãy tích hợp thông tin này vào câu trả lời để giải thích rõ sự liên kết logic giữa các văn bản luật.
"""

# Main Interface Layout
st.markdown("""
<div class="title-banner">
    <h1>⚖️ Graph RAG Hỏi Đáp Pháp Luật Việt Nam</h1>
    <p>Hệ thống hỗ trợ tra cứu luật thông minh kết hợp Cơ sở dữ liệu đồ thị Neo4j, nhúng MSMARCO và mô hình Gemini 3.6 Flash</p>
</div>
""", unsafe_allow_html=True)

# Question Input Section
st.subheader("❓ Nhập câu hỏi pháp lý của bạn")
user_query_input = st.text_area(
    "Nhập câu hỏi (Ví dụ: Nghị định 46/2023/NĐ-CP thay thế cho nghị định nào, và nghị định bị thay thế đó có nội dung gì nổi bật?)",
    height=80,
    placeholder="Nhập câu hỏi tại đây..."
)

# Active retrieval run
if st.button("🚀 Gửi Câu hỏi & Phân tích Đồ thị"):
    if not user_query_input.strip():
        st.warning("Vui lòng nhập nội dung câu hỏi trước khi tìm kiếm.")
    elif not api_key:
        st.warning("Vui lòng cấu hình Gemini API Key ở menu bên trái.")
    else:
        with st.spinner("Hệ thống đang nhúng câu hỏi, truy vấn đồ thị Neo4j và phân tích đa bước..."):
            
            # Run multi-hop retrieval
            start_time = time.time()
            context_output, docs, relationships, chunks = run_multihop_retrieval(
                user_query_input, val_k, val_hops, val_m
            )
            retrieval_time = time.time() - start_time
            
            if context_output is None:
                st.error("Truy vấn thất bại. Vui lòng kiểm tra lại cấu hình kết nối Neo4j hoặc mô hình nhúng.")
            else:
                # Run LLM response generation
                llm_start = time.time()
                llm_response = ask_gemini(SYSTEM_PROMPT, user_query_input, context_output)
                llm_time = time.time() - llm_start
                
                # Render response in Tabs
                tab_ans, tab_graph, tab_chunks = st.tabs([
                    "💬 Câu trả lời (Gemini Answer)", 
                    "🕸️ Ngữ cảnh Đồ thị (Graph Subgraph)", 
                    "📄 Nội dung Phân đoạn (Context Chunks)"
                ])
                
                with tab_ans:
                    st.markdown(f"**⚡ Thời gian xử lý:** Truy xuất đồ thị: `{retrieval_time:.2f}s` | Gemini LLM: `{llm_time:.2f}s`")
                    st.markdown(f'<div class="answer-box">{llm_response}</div>', unsafe_allow_html=True)
                
                with tab_graph:
                    col_docs, col_rels = st.columns(2)
                    with col_docs:
                        st.markdown("### 📄 Các văn bản liên quan")
                        if not docs:
                            st.write("Không tìm thấy văn bản nào.")
                        else:
                            for d in docs:
                                st.markdown(f"""
                                <div class="doc-card">
                                    <div class="doc-card-title">{d['so_ky_hieu']}</div>
                                    <div class="doc-card-meta">{d['title']}</div>
                                    <div class="doc-card-meta" style="color: #38bdf8; font-weight:bold; margin-top:5px;">ID: {d['id']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                    with col_rels:
                        st.markdown("### 🔗 Các mối quan hệ duyệt đồ thị (Document Links)")
                        if not relationships:
                            st.info("Không có liên kết trực tiếp giữa các văn bản được tìm thấy (0 Hops).")
                        else:
                            for rel in relationships:
                                st.markdown(f'<span class="rel-badge">{rel}</span>', unsafe_allow_html=True)
                                
                with tab_chunks:
                    st.markdown("### 📄 Chi tiết các đoạn văn bản cấu trúc đã nạp vào Context")
                    if not chunks:
                        st.write("Không có phân đoạn nội dung nào.")
                    else:
                        for idx, c in enumerate(chunks):
                            with st.expander(f"Phân đoạn {idx+1}: {c['title'] or 'Không tiêu đề'} (Score: {c['score']:.4f})"):
                                st.markdown(f"**Văn bản thuộc về:** ID {c['doc_id']} | **Loại phân đoạn:** `{c['type']}`")
                                st.markdown("---")
                                st.write(c["content"])

# Footer metadata
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>Lab Graph RAG Pháp Luật | Neo4j Desktop | HuggingFace MiniLM Embeddings</p>", unsafe_allow_html=True)
