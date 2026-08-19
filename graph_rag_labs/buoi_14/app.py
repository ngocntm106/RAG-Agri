import os
import sys
import pandas as pd
import streamlit as st

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="RAG Hybrid Search — Buổi 14",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from src.unified_retriever import UnifiedRetriever

@st.cache_resource(show_spinner="Đang khởi tạo các mô hình Retrieval (BM25, Dense, Hybrid, Reranker)...")
def get_retriever():
    return UnifiedRetriever()

def main():
    st.title("🔍 RAG Hybrid Search — Buổi 14")
    st.markdown(
        "Hệ thống tìm kiếm thông tin pháp lý đa phương thức kết hợp **BM25 Lexical Search**, "
        "**Dense Semantic Embedding**, **Reciprocal Rank Fusion (RRF)**, "
        "**Cross-Encoder Neural Reranking** và **Graph Context Hints**."
    )
    st.divider()

    # Khởi tạo retriever
    try:
        retriever = get_retriever()
    except Exception as e:
        st.error(f"Lỗi khởi tạo hệ thống Retrieval: {e}")
        st.stop()

    # Sidebar điều khiển
    with st.sidebar:
        st.header("⚙️ Cấu hình Tìm kiếm")
        
        method_map = {
            "Hybrid + Rerank": "hybrid_rerank",
            "Hybrid": "hybrid",
            "BM25": "bm25",
            "Dense": "dense"
        }
        
        selected_method_label = st.selectbox(
            "Phương pháp Retrieval:",
            options=list(method_map.keys()),
            index=0,
            help="Chọn chiến lược tìm kiếm tài liệu"
        )
        method = method_map[selected_method_label]

        top_k = st.slider("Top-K kết quả:", min_value=1, max_value=20, value=5, step=1)
        
        candidate_k = 20
        if method in ["hybrid", "hybrid_rerank"]:
            candidate_k = st.slider(
                "Candidate-K (ứng viên trước RRF/Rerank):", 
                min_value=5, max_value=50, value=20, step=5
            )

        st.divider()
        st.markdown("### 💡 Câu hỏi mẫu:")
        sample_queries = [
            "Thông tư 01/2014/TT-NHNN Điều 4 quy định đóng gói niêm phong tiền mặt",
            "Ai có thẩm quyền phê duyệt việc mở chi nhánh ngân hàng nước ngoài?",
            "Điều kiện thành lập doanh nghiệp bảo hiểm theo Nghị định 73/2016/NĐ-CP",
            "Quy định về sáp nhập hợp tác xã theo Điều 95 Luật Hợp tác xã số 17/2023/QH15"
        ]
        for q in sample_queries:
            if st.button(q, key=f"btn_{q}"):
                st.session_state["query_input"] = q

        st.divider()
        st.caption("Buổi 14 — Graph RAG Labs")

    # Main search interface
    query_text = st.text_input(
        "Nhập câu hỏi tìm kiếm:",
        value=st.session_state.get("query_input", "Quy định về niêm phong và đóng gói tiền mặt"),
        placeholder="Ví dụ: Quy định về vốn điều lệ của doanh nghiệp bảo hiểm...",
        key="query_text_input"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        search_clicked = st.button("🚀 Tìm kiếm", type="primary", use_container_width=True)

    if search_clicked or query_text:
        if not query_text.strip():
            st.warning("Vui lòng nhập câu hỏi tìm kiếm!")
            return

        with st.spinner(f"Đang thực hiện tìm kiếm bằng phương pháp `{selected_method_label}`..."):
            # Nếu là Hybrid + Rerank, lấy cả candidate list trước khi rerank để so sánh Before/After
            before_candidates = []
            if method == "hybrid_rerank":
                before_candidates = retriever.hybrid.search(query_text, top_k=candidate_k, candidate_k=candidate_k)

            results = retriever.retrieve(
                question=query_text,
                method=method,
                top_k=top_k,
                candidate_k=candidate_k
            )

            # Lấy Graph Hints
            hints = retriever.get_graph_hints(results)

        if not results:
            st.info("Không tìm thấy kết quả phù hợp.")
            return

        # Hiển thị kết quả
        st.subheader(f"📋 Kết quả Tìm kiếm ({len(results)} kết quả)")

        # Nếu là Hybrid + Rerank, hiển thị bảng so sánh BEFORE vs AFTER RERANK
        if method == "hybrid_rerank" and before_candidates:
            with st.expander("📊 So sánh thứ hạng: BEFORE RERANK (Hybrid) vs AFTER RERANK (Cross-Encoder)", expanded=True):
                comp_data = []
                for r in results:
                    comp_data.append({
                        "Final Rank (Sau Rerank)": r["rank"],
                        "Orig Rank (Trước Rerank)": r.get("hybrid_rank", "-"),
                        "Rerank Score": f"{r['rerank_score']:.4f}" if r.get('rerank_score') is not None else "-",
                        "Hybrid RRF": f"{r['hybrid_score']:.6f}" if r.get('hybrid_score') is not None else "-",
                        "Citation": r["citation"],
                        "Chunk ID": r["chunk_id"]
                    })
                st.dataframe(pd.DataFrame(comp_data), use_container_width=True)

        # Hiển thị từng Card kết quả
        for i, (res, hint) in enumerate(zip(results, hints), 1):
            with st.container():
                st.markdown(f"#### #{res['rank']} — `{res['citation']}`")
                
                # Metadata tags
                col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 3, 3])
                with col_m1:
                    st.markdown(f"**Score:** `{res['score']:.4f}`")
                with col_m2:
                    st.markdown(f"**Method:** `{res['retrieval_method']}`")
                with col_m3:
                    st.markdown(f"**Document ID:** `{res['document_id']}`")
                with col_m4:
                    st.markdown(f"**Chunk ID:** `{res['chunk_id'][:18]}...`")

                # Text content
                st.text_area(
                    label="Nội dung trích xuất:",
                    value=res["text"],
                    height=100,
                    key=f"text_{res['chunk_id']}_{i}",
                    disabled=True
                )

                # Graph Hints section
                with st.expander("🌐 Graph Hints (Ngữ cảnh Đồ thị 1-Hop)"):
                    gh_c1, gh_c2 = st.columns(2)
                    with gh_c1:
                        st.markdown("**Cấu trúc văn bản tuần tự:**")
                        st.markdown(f"- **Chunk trước (PREV):** `{hint['prev_chunk_id']}`")
                        st.markdown(f"- **Chunk hiện tại:** `{hint['chunk_id']}`")
                        st.markdown(f"- **Chunk kế tiếp (NEXT):** `{hint['next_chunk_id']}`")
                    
                    with gh_c2:
                        st.markdown(f"**Quan hệ liên văn bản ({hint.get('graph_source', 'Graph')}):**")
                        if hint['document_relations']:
                            for rel in hint['document_relations']:
                                direction_sym = "➡️" if rel.get('direction') == 'OUTGOING' else "⬅️"
                                st.markdown(f"- {direction_sym} `:{rel['type']}` {rel['target']} *({rel['desc']})*")
                        else:
                            st.markdown("*(Không có quan hệ liên văn bản trực tiếp)*")

                st.divider()

if __name__ == "__main__":
    main()
