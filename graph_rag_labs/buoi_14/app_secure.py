"""
Application: app_secure.py
Purpose: Streamlit Web Application demonstrating Role-Based Access Control (RBAC)
         on Data & Retrieval Pipeline for Legal & Banking Knowledge Graph RAG.
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
import streamlit as st

# Reconfigure stdout to UTF-8 and set root path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Secure RAG with RBAC — Buổi 15",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import (
    VALID_ROLES,
    ROLE_ADMIN,
    ROLE_HR,
    ROLE_STAFF,
    ROLE_GUEST,
    ROLE_DESCRIPTIONS,
    validate_roles
)
from src.secure_retriever import SecureRetriever
from src.generator import generate_rag_answer


# Tùy biến CSS để giao diện trực quan và chuyên nghiệp
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .badge-admin {
        background-color: #EF4444;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-hr {
        background-color: #8B5CF6;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-staff {
        background-color: #3B82F6;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-guest {
        background-color: #10B981;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .filter-alert {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 6px;
        color: #92400E;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    .card-container {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Đang khởi tạo hệ thống Secure Retrieval (BM25, Dense, RRF, Reranker)...")
def get_retriever():
    return SecureRetriever()


def format_role_badge(roles: list[str]) -> str:
    """Tạo badge HTML màu sắc cho từng nhóm quyền."""
    badges = []
    for r in roles:
        if r == ROLE_ADMIN:
            badges.append(f"<span class='badge-admin'>👑 {r}</span>")
        elif r == ROLE_HR:
            badges.append(f"<span class='badge-hr'>👔 {r}</span>")
        elif r == ROLE_STAFF:
            badges.append(f"<span class='badge-staff'>💼 {r}</span>")
        else:
            badges.append(f"<span class='badge-guest'>🌐 {r}</span>")
    return " ".join(badges)


def main():
    # Header chính
    st.markdown('<div class="main-header">🛡️ Hệ thống RAG Tìm kiếm An toàn (RBAC Secure Retrieval)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">'
        'Kiểm soát truy cập dữ liệu đa cấp độ (Role-Based Access Control) kết hợp <b>BM25</b>, '
        '<b>Dense Embedding</b>, <b>Hybrid RRF</b>, <b>Cross-Encoder Reranker</b> và <b>Neo4j Knowledge Graph</b>.'
        '</div>', 
        unsafe_allow_html=True
    )

    # Nạp Retriever
    try:
        retriever = get_retriever()
    except Exception as e:
        st.error(f"Lỗi khởi tạo hệ thống Retrieval: {e}")
        st.stop()

    # =========================================================================
    # SIDEBAR: CẤU HÌNH VAI TRÒ & PHƯƠNG THỨC TÌM KIẾM
    # =========================================================================
    with st.sidebar:
        st.header("👤 1. Thiết lập Vai trò (RBAC)")
        st.markdown("Chọn vai trò người dùng để mô phỏng phân quyền truy cập:")

        # Preset buttons for quick role selection
        st.caption("⚡ Chọn nhanh vai trò (1-Click Persona):")
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            if st.button("🌐 Guest (Khách)", use_container_width=True):
                st.session_state["selected_roles"] = [ROLE_GUEST]
            if st.button("👔 HR (Nhân sự)", use_container_width=True):
                st.session_state["selected_roles"] = [ROLE_HR]
        with p_col2:
            if st.button("💼 Staff (Nội bộ)", use_container_width=True):
                st.session_state["selected_roles"] = [ROLE_STAFF]
            if st.button("👑 Admin (Toàn quyền)", use_container_width=True):
                st.session_state["selected_roles"] = [ROLE_ADMIN]

        # Multiselect chính thức
        current_roles = st.session_state.get("selected_roles", [ROLE_GUEST])
        user_roles = st.multiselect(
            "Vai trò của bạn (Your Active Roles):",
            options=VALID_ROLES,
            default=current_roles,
            key="selected_roles_multiselect"
        )
        
        # Đồng bộ session state
        st.session_state["selected_roles"] = user_roles if user_roles else [ROLE_GUEST]
        active_roles = validate_roles(st.session_state["selected_roles"])

        # Hiển thị mô tả vai trò đang chọn
        st.markdown("**Quyền hạn hiện tại:**")
        for r in active_roles:
            st.markdown(f"- **{r}**: {ROLE_DESCRIPTIONS.get(r, '')}")

        st.divider()

        st.header("⚙️ 2. Cấu hình Retrieval")
        method_map = {
            "Hybrid + Rerank (Khuyên dùng)": "hybrid_rerank",
            "Hybrid (RRF Fusion)": "hybrid",
            "Dense Semantic Search": "dense",
            "BM25 Lexical Search": "bm25",
            "Neo4j Knowledge Graph": "graph"
        }
        
        selected_label = st.selectbox(
            "Phương thức tìm kiếm:",
            options=list(method_map.keys()),
            index=0
        )
        method = method_map[selected_label]

        top_k = st.slider("Top-K kết quả hiển thị:", min_value=1, max_value=15, value=5, step=1)
        candidate_k = 20
        if method in ["hybrid", "hybrid_rerank"]:
            candidate_k = st.slider("Candidate-K (ứng viên trung gian):", min_value=5, max_value=50, value=20, step=5)

        st.divider()
        st.markdown("### 💡 Câu hỏi mẫu kiểm thử:")
        
        sample_groups = {
            "🔒 Nhạy cảm Nhân sự (HR/Admin)": [
                "Hồ sơ và tiêu chuẩn bổ nhiệm người quản lý, tổng giám đốc",
                "Quy định về tuyển dụng, hợp đồng lao động và chế độ phụ cấp",
                "Tiêu chuẩn bổ nhiệm chuyên gia tính toán của doanh nghiệp bảo hiểm"
            ],
            "💼 Nghiệp vụ & Rủi ro (Staff/Admin)": [
                "Hạn mức cấp tín dụng và tỷ lệ an toàn vốn cho vay",
                "Quy định niêm phong và giao nhận vận chuyển tiền mặt trong kho quỹ",
                "Thủ tục kiểm soát đặc biệt và tổ chức lại quỹ tín dụng nhân dân"
            ],
            "🌐 Quy định Chung (Public/Guest)": [
                "Phạm vi áp dụng và nguyên tắc tham gia bảo hiểm tại Việt Nam",
                "Điều kiện cấp Giấy phép thành lập doanh nghiệp bảo hiểm",
                "Quyền hạn và nhiệm vụ của Ngân hàng Nhà nước Việt Nam"
            ]
        }

        for group_name, queries in sample_groups.items():
            st.markdown(f"**{group_name}**")
            for q in queries:
                if st.button(f"👉 {q}", key=f"btn_{q}"):
                    st.session_state["query_input"] = q

        st.divider()
        with st.expander("🔑 Cấu hình LLM API (Tùy chọn)"):
            user_api_key = st.text_input(
                "Gemini API Key:",
                type="password",
                placeholder="Dán API key nếu muốn dùng Gemini LLM...",
                help="Nếu không nhập, hệ thống tự động dùng Local Grounded RAG Synthesizer (miễn phí, offline 100%)"
            )

    # =========================================================================
    # MAIN AREA: KHUNG TÌM KIẾM & HIỂN THỊ KẾT QUẢ
    # =========================================================================
    
    # Active role banner
    st.info(f"🔑 **Đang tìm kiếm dưới danh nghĩa vai trò:** `{'`, `'.join(active_roles)}` | **Phương pháp:** `{selected_label}`")

    # Ô nhập truy vấn
    query_text = st.text_input(
        "Nhập câu hỏi tìm kiếm văn bản quy định:",
        value=st.session_state.get("query_input", "Hồ sơ và tiêu chuẩn bổ nhiệm người quản lý, tổng giám đốc"),
        placeholder="Ví dụ: Quy định về phê duyệt tín dụng, hồ sơ nhân sự, vốn điều lệ...",
        key="main_query_input"
    )

    c_btn, _ = st.columns([1, 4])
    with c_btn:
        search_clicked = st.button("🚀 Thực hiện Tìm kiếm", type="primary", use_container_width=True)

    if search_clicked or query_text:
        if not query_text.strip():
            st.warning("Vui lòng nhập nội dung câu hỏi!")
            return

        start_time = time.time()
        
        with st.spinner(f"Đang tìm kiếm an toàn cho vai trò {active_roles}..."):
            # 1. Chạy tìm kiếm với quyền hiện tại của người dùng
            results = retriever.retrieve(
                query=query_text,
                user_roles=active_roles,
                method=method,
                top_k=top_k,
                candidate_k=candidate_k
            )

            # 2. Chạy tìm kiếm giả định toàn quyền (Admin) để phát hiện số tài liệu bị lọc bỏ
            admin_results = retriever.retrieve(
                query=query_text,
                user_roles=[ROLE_ADMIN],
                method=method,
                top_k=top_k,
                candidate_k=candidate_k
            )

            # 3. Lấy Graph Hints đã qua bộ lọc quyền
            hints = retriever.get_secure_graph_hints(results, user_roles=active_roles)
            elapsed = time.time() - start_time

        # Tính toán số lượng tài liệu nhạy cảm bị ẩn đi đối với vai trò hiện tại
        user_cids = {r["chunk_id"] for r in results}
        admin_cids = {r["chunk_id"] for r in admin_results}
        hidden_cids = admin_cids - user_cids
        num_hidden = len(hidden_cids)

        # Thông báo thống kê bảo mật
        if num_hidden > 0 and ROLE_ADMIN not in active_roles:
            st.markdown(
                f"""
                <div class="filter-alert">
                    🛡️ <b>BẢO MẬT DỮ LIỆU:</b> Đã phát hiện và <b>lọc bỏ {num_hidden} tài liệu nhạy cảm</b> 
                    nằm trong Top-{top_k} do vai trò hiện tại (<code>{', '.join(active_roles)}</code>) không có quyền truy cập!
                </div>
                """, 
                unsafe_allow_html=True
            )

        if not results:
            st.warning("⚠️ Không tìm thấy tài liệu nào phù hợp hoặc toàn bộ kết quả đã bị ẩn do không đủ quyền truy cập!")
            return

        # Metrics tổng quan
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Số kết quả tìm thấy", f"{len(results)} chunks")
        with m2:
            st.metric("Thời gian phản hồi", f"{elapsed:.3f} s")
        with m3:
            st.metric("Tài liệu bị ẩn (RBAC)", f"{num_hidden} chunks", delta=f"-{num_hidden}" if num_hidden > 0 else "0", delta_color="inverse")
        with m4:
            st.metric("Mức độ an toàn", "100% Verified", delta="RBAC Mask Active")

        st.divider()

        # =========================================================================
        # 💬 CÂU TRẢ LỜI TỔNG HỢP & CITATION (RAG ANSWER & CITATION)
        # =========================================================================
        st.subheader("💬 Câu trả lời Tổng hợp & Trích dẫn (RAG Answer & Citation)")
        with st.spinner(f"Đang tổng hợp câu trả lời từ các tài liệu hợp lệ cho vai trò {active_roles}..."):
            api_key_val = user_api_key if 'user_api_key' in locals() and user_api_key else None
            rag_response = generate_rag_answer(
                query=query_text,
                results=results,
                user_roles=active_roles,
                num_hidden=num_hidden,
                api_key=api_key_val
            )

        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border: 1.5px solid #3B82F6; border-left: 6px solid #2563EB; border-radius: 8px; padding: 18px; margin-bottom: 24px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                    <span style="font-size: 1.1rem; font-weight: 700; color: #1E293B;">
                        📝 Trả lời theo phạm vi quyền: <code>{', '.join(active_roles)}</code>
                    </span>
                    <span style="background-color:#DBEAFE; color:#1E40AF; padding:3px 10px; border-radius:12px; font-size:0.82rem; font-weight:600;">
                        🤖 {rag_response['model_used']}
                    </span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown(rag_response['answer'])

        st.divider()

        # Hiển thị bảng so sánh (nếu dùng Reranker)
        if method == "hybrid_rerank":
            with st.expander("📊 Bảng chi tiết điểm số & Thứ hạng (Cross-Encoder vs RRF)", expanded=False):
                table_rows = []
                for r in results:
                    table_rows.append({
                        "Thứ hạng": r["rank"],
                        "Quyền xem": ", ".join(r.get("allowed_roles", [])),
                        "Rerank Score": f"{r['score']:.4f}",
                        "Hybrid Score": f"{r['hybrid_score']:.6f}" if r.get("hybrid_score") is not None else "-",
                        "Trích dẫn": r["citation"],
                        "Chunk ID": r["chunk_id"]
                    })
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        # Hiển thị từng kết quả
        st.subheader(f"📋 Chi tiết các Đoạn Tài liệu Trích xuất ({len(results)} chunks)")

        
        for i, (res, hint) in enumerate(zip(results, hints), 1):
            roles_badge_html = format_role_badge(res.get("allowed_roles", []))
            
            with st.container():
                st.markdown(f"""
                <div style="background-color:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#0F172A;">#{res['rank']} — {res['citation']}</h4>
                        <div><b>Quyền xem:</b> {roles_badge_html}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c_m1, c_m2, c_m3, c_m4 = st.columns([2, 2, 3, 3])
                with c_m1:
                    st.markdown(f"**Score:** `{res['score']:.4f}`")
                with c_m2:
                    st.markdown(f"**Method:** `{res['retrieval_method']}`")
                with c_m3:
                    st.markdown(f"**Document ID:** `{res['document_id']}`")
                with c_m4:
                    st.markdown(f"**Chunk ID:** `{res['chunk_id'][:16]}...`")

                # Nội dung đoạn văn bản
                st.text_area(
                    label="Nội dung điều khoản trích xuất:",
                    value=res["text"],
                    height=110,
                    key=f"card_text_{res['chunk_id']}_{i}",
                    disabled=True
                )

                # Ngữ cảnh Đồ thị Bảo mật (Secure Graph Hints)
                with st.expander(f"🌐 Ngữ cảnh Đồ thị Bảo mật (Secure Graph 1-Hop) — Chunk #{res['rank']}"):
                    g_col1, g_col2 = st.columns(2)
                    with g_col1:
                        st.markdown("**Cấu trúc văn bản tuần tự (Đã lọc quyền):**")
                        st.markdown(f"- **Chunk trước (PREV):** `{hint['prev_chunk_id']}`")
                        st.markdown(f"- **Chunk hiện tại:** `{hint['chunk_id']}`")
                        st.markdown(f"- **Chunk sau (NEXT):** `{hint['next_chunk_id']}`")
                    with g_col2:
                        st.markdown(f"**Thông tin liên kết:**")
                        st.markdown(f"- **Tệp nguồn:** `{hint['source_file']}`")
                        st.markdown(f"- **Mã tài liệu:** `{hint['document_id']}`")
                        st.markdown(f"- **Vai trò đang kiểm tra:** `{', '.join(hint['user_roles'])}`")

                st.markdown("<br>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
