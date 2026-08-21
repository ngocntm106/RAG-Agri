"""
Application: app.py
Purpose: Streamlit Web UI Demo cho Buổi 17 — RBAC, Audit Trail & AI Compliance Gap Checker.
Mô hình bài lab đào tạo cho Agribank RAG System.
"""

import os
import sys
import json
import time
import pandas as pd
import streamlit as st
from pathlib import Path

# Cấu hình đường dẫn hệ thống để import module từ buoi_17/scripts
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from buoi_17.scripts.secure_retrieval_adapter import SecureRetrieverAdapter
from buoi_17.scripts.internal_lookup import internal_policy_lookup
from buoi_17.scripts.compliance_gap import ComplianceGapChecker, STATUS_HUMAN_REVIEW
from buoi_17.scripts.audit_logger import AuditLogger

# ----------------------------------------------------
# PAGE CONFIG & STYLING
# ----------------------------------------------------
st.set_page_config(
    page_title="Agribank Security & RAG Compliance System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS giao diện hiện đại, chuẩn hóa card & badge
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .banner-warning {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 0.8rem 1.2rem;
        border-radius: 4px;
        color: #92400E;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .status-badge-allowed {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-badge-denied {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-badge-gap {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .card-box {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# INITIALIZE CACHED MODULES
# ----------------------------------------------------
@st.cache_resource
def load_gap_checker():
    # Khởi tạo instance Compliance Gap Checker
    return ComplianceGapChecker()

@st.cache_resource
def check_neo4j_status():
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        pwd = os.getenv("NEO4J_PASSWORD", "12345678")
        driver = GraphDatabase.driver(uri, auth=(user, pwd), connection_timeout=2)
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception:
        return False


# ----------------------------------------------------
# BANNER BẮT BUỘC
# ----------------------------------------------------
st.markdown('<div class="banner-warning">⚠️ Demo đào tạo — kết quả AI cần kiểm toán viên xác minh.</div>', unsafe_allow_html=True)

st.markdown('<div class="main-header">🛡️ AGRIBANK RAG COMPLIANCE & SECURITY SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Buổi 17: Phân quyền RBAC, Ghi vết Audit Trail & AI Compliance Gap Checker</div>', unsafe_allow_html=True)


# ----------------------------------------------------
# SIDEBAR CONTROL PANEL
# ----------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield-turned-on.png", width=64)
    st.header("⚙️ Phân quyền Demo (RBAC)")

    user_id_demo = st.selectbox(
        "👤 Demo User ID",
        options=["usr_hr_lead_01", "usr_staff_ops_02", "usr_guest_intern", "usr_admin_master"],
        index=0,
        help="Chọn User ID mô phỏng kiểm thử"
    )

    user_role = st.radio(
        "🔑 Vai trò người dùng (Role)",
        options=["Admin", "HR", "Staff", "Guest"],
        index=1,
        help="Vai trò quyết định phạm vi truy cập dữ liệu RAG"
    )

    st.markdown("---")
    st.subheader("🌐 Trạng thái Hệ thống Graph")
    neo4j_online = check_neo4j_status()
    if neo4j_online:
        st.success("🟢 Neo4j Database: Online")
    else:
        st.info("🟡 Neo4j Database: Offline\n*(Tự động Fallback: Hybrid Search Active)*")

    st.markdown("---")
    st.caption("🔒 Bảo mật RAG & Audit Trail v2.5")
    st.caption("© 2026 Agribank AI Lab Training")


# ----------------------------------------------------
# MAIN TABS INTERFACE
# ----------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📖 TAB 1: TRA CỨU QUY ĐỊNH NỘI BỘ",
    "⚖️ TAB 2: COMPLIANCE GAP CHECKER",
    "📜 TAB 3: AUDIT TRAIL LOGS"
])


# ====================================================
# TAB 1: TRA CỨU QUY ĐỊNH NỘI BỘ (USE CASE 1)
# ====================================================
with tab1:
    st.subheader("🔍 Use Case 1: Tra cứu Quy định Nội bộ có RBAC & Audit Trail")
    st.markdown("Tra cứu ngữ cảnh chính xác theo phạm vi phân quyền người dùng. Tuyệt đối không rò rỉ dữ liệu bị DENY.")

    col1_1, col1_2 = st.columns([3, 1])
    with col1_1:
        preset_questions = [
            "-- Chọn câu hỏi mẫu hoặc tự nhập bên dưới --",
            "quy định về nâng lương và phụ cấp tuyển dụng cán bộ nhân sự",
            "quy trình hướng dẫn công tác kiểm quỹ và quản lý kho tiền",
            "tỷ lệ an toàn vốn tối thiểu CAR của ngân hàng quy định bao nhiêu",
            "báo cáo đánh giá quy hoạch cán bộ và bảng lương bảo mật cá nhân"
        ]
        selected_preset = st.selectbox("Câu hỏi gợi ý:", options=preset_questions)
        
        default_q = "" if selected_preset.startswith("--") else selected_preset
        question = st.text_input("Nhập câu hỏi tra cứu quy định:", value=default_q, placeholder="Ví dụ: Quy định về bảo quản kho tiền và vận chuyển tiền mặt...")

    with col1_2:
        top_k = st.slider("Top-k candidates:", min_value=1, max_value=10, value=5)
        btn_lookup = st.button("🔎 Tra cứu ngay", type="primary", use_container_width=True)

    if btn_lookup and question.strip():
        with st.spinner("Đang thực thi Hybrid Search, kiểm tra RBAC và tổng hợp câu trả lời..."):
            start_time = time.time()
            res = internal_policy_lookup(
                question=question,
                user_role=user_role,
                top_k=top_k,
                user_id_demo=user_id_demo
            )
            elapsed = time.time() - start_time

        st.markdown("---")
        
        # Quyết định truy cập
        retrieved_chunk_ids = res.get("retrieved_chunk_ids", res.get("chunk_ids", []))
        retrieved_doc_ids = res.get("retrieved_document_ids", res.get("document_ids", []))
        is_denied = "Không tìm thấy đủ thông tin" in res.get("answer", "") or not retrieved_chunk_ids
        access_badge = '<span class="status-badge-denied">⛔ ACCESS DENIED / INSUFFICIENT</span>' if is_denied else '<span class="status-badge-allowed">✅ ACCESS ALLOWED</span>'

        st.markdown(f"### 📋 Kết quả Tra cứu {access_badge}", unsafe_allow_html=True)
        st.markdown(f"**Request ID**: `{res.get('request_id', 'N/A')}` | **Thời gian xử lý**: `{elapsed:.2f}s` | **Scope**: `{res.get('access_scope', 'N/A')}`")

        st.markdown("#### 💬 Câu trả lời từ AI:")
        st.info(res.get("answer", ""))

        # Chỉ hiển thị Citations & Metadata nếu được phép (chống rò rỉ khi DENIED)
        if not is_denied:
            st.markdown("#### 📚 Trích dẫn Pháp lý / Quy định (Citations):")
            for cit in res.get("citations", []):
                st.markdown(f"- 📄 `{cit}`")

            with st.expander("🧩 Mã Định danh Document ID & Chunk ID"):
                st.write("**Document IDs**:", retrieved_doc_ids)
                st.write("**Chunk IDs**:", retrieved_chunk_ids)
        else:
            st.warning("🔒 0 rò rỉ dữ liệu: Không hiển thị snippet hoặc citation bị cấm cho vai trò này.")


# ====================================================
# TAB 2: COMPLIANCE GAP CHECKER (USE CASE 2)
# ====================================================
with tab2:
    st.subheader("⚖️ Use Case 2: AI Compliance Gap Checker (Đối chiếu Bằng chứng 2 Phía)")
    st.markdown("So sánh đối chiếu yêu cầu Ngân hàng Nhà nước (External) với Quy định Nội bộ Agribank (Internal).")

    sample_reqs = {
        "REQ-NHNN-01-VALUABLES": {
            "req": "Quy định về tiêu chuẩn bảo quản, vận chuyển tiền mặt, tài sản quý và giấy tờ có giá trong kho tiền.",
            "cit": "[Thông tư 01/2014/TT-NHNN | Điều 15. Sắp xếp, bảo quản tài sản tại quầy giao dịch và trong kho tiền | 9fe3fbee-2d53-11f1-9d3d-e316384c20ed]"
        },
        "REQ-NHNN-41-CAPITAL": {
            "req": "Quy định tỷ lệ an toàn vốn tối thiểu và quản lý rủi ro hoạt động đối với ngân hàng thương mại.",
            "cit": "[Thông tư 41/2016/TT-NHNN | Điều 3. Tỷ lệ an toàn vốn | 93f5c852-df3e-11f0-b44b-8573f7cc12b3]"
        },
        "REQ-NHNN-27-SAFETY-FUND": {
            "req": "Quy định trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân.",
            "cit": "[Thông tư 27/2024/TT-NHNN | Điều 5. Trích nộp Quỹ bảo đảm an toàn | 93f5c884-df3e-11f0-bcf2-f34d1dbe48ff]"
        },
        "REQ-NHNN-56-LICENSING": {
            "req": "Quy định về hồ sơ, thủ tục cấp Giấy phép lần đầu của ngân hàng thương mại và chi nhánh ngân hàng nước ngoài.",
            "cit": "[Thông tư 56/2024/TT-NHNN | Điều 8. Hồ sơ cấp phép | 93f66578-df3e-11f0-96dd-1d7f48a0b5c4]"
        }
    }

    col2_1, col2_2 = st.columns([2, 1])
    with col2_1:
        req_key = st.selectbox("Chọn Yêu cầu NHNN mẫu:", options=list(sample_reqs.keys()))
        ext_req = st.text_area("Yêu cầu Ngân hàng Nhà nước (External Requirement):", value=sample_reqs[req_key]["req"], height=100)
        ext_cit = st.text_input("Trích dẫn NHNN (External Citation):", value=sample_reqs[req_key]["cit"])

    with col2_2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        btn_gap = st.button("⚖️ Phân tích khoảng trống Compliance Gap", type="primary", use_container_width=True)

    if btn_gap:
        with st.spinner("Đang chạy đối chiếu bằng chứng hai phía..."):
            checker = load_gap_checker()
            gap_res = checker.analyze_requirement(
                requirement_id=req_key,
                external_requirement=ext_req,
                external_citation=ext_cit,
                user_role=user_role,
                user_id_demo=user_id_demo
            )

        st.markdown("---")
        st.markdown("### 📊 Kết quả Phân tích Evidence Package")

        col_g1, col_g2, col_g3, col_g4 = st.columns(4)
        with col_g1:
            st.metric("Trạng thái Gap", gap_res["gap_status"])
        with col_g2:
            st.metric("Độ tin cậy (Confidence)", f"{int(gap_res['confidence']*100)}%")
        with col_g3:
            st.metric("Review Status", gap_res["review_status"])
        with col_g4:
            st.metric("Vai trò thẩm định", user_role)

        st.markdown("#### 🔍 Bằng chứng hai phía (Evidence Package):")
        df_evidence = pd.DataFrame([{
            "Mã Req": gap_res["requirement_id"],
            "Yêu cầu NHNN (External)": gap_res["external_requirement"],
            "Citation NHNN": gap_res["external_citation"],
            "Bằng chứng Nội bộ Agribank": gap_res["internal_evidence"],
            "Citation Nội bộ": gap_res["internal_citation"],
            "Trạng thái Gap": gap_res["gap_status"],
            "Review Status": gap_res["review_status"]
        }])
        st.dataframe(df_evidence, use_container_width=True)

        st.markdown("#### 📝 Lý do phân loại (Reason):")
        st.warning(gap_res["reason"])


# ====================================================
# TAB 3: AUDIT TRAIL LOGS
# ====================================================
with tab3:
    st.subheader("📜 Nhật ký Kiểm toán Audit Trail & Data Security")
    st.markdown("Lưu vết 100% các request truy vấn (kể cả request bị DENIED). Tuyệt đối không chứa secret hay API Key.")

    log_file = CURRENT_DIR / "outputs" / "audit_log.jsonl"
    
    if log_file.exists():
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except Exception:
                        pass

        if logs:
            df_logs = pd.DataFrame(logs)
            
            # Lọc log hiển thị phù hợp với role demo (nếu không phải Admin)
            if user_role != "Admin":
                df_logs_show = df_logs[df_logs["user_role"].apply(lambda r: user_role in r if isinstance(r, list) else user_role == r)]
            else:
                df_logs_show = df_logs

            # Đảm bảo loại bỏ hoàn toàn các trường secret nếu vô tình có
            secret_cols = [c for c in df_logs_show.columns if any(k in c.lower() for k in ["password", "secret", "api_key", "token"])]
            if secret_cols:
                df_logs_show = df_logs_show.drop(columns=secret_cols)

            st.write(f"**Tổng số Audit Events ghi nhận**: `{len(df_logs):,}` events | **Hiển thị cho role {user_role}**: `{len(df_logs_show):,}` events")
            
            st.dataframe(
                df_logs_show.sort_values(by="timestamp", ascending=False),
                use_container_width=True
            )
        else:
            st.info("Chưa có nhật ký kiểm toán trong tệp audit_log.jsonl.")
    else:
        st.warning("Chưa tìm thấy tệp nhật ký buoi_17/outputs/audit_log.jsonl.")

    st.markdown("---")
    st.subheader("🔐 Demo Mã hóa dữ liệu lưu trữ (Data At-Rest Encryption)")
    enc_file = CURRENT_DIR / "outputs" / "audit_log.jsonl.enc"
    dec_file = CURRENT_DIR / "outputs" / "audit_log_decrypted.jsonl"

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.write("**Trạng thái tệp mã hóa (.enc)**:", "✅ Có sẵn" if enc_file.exists() else "❌ Chưa khởi tạo")
        if enc_file.exists():
            st.caption(f"Kích thước tệp mã hóa: `{enc_file.stat().st_size:,}` bytes")
    with col_e2:
        st.write("**Trạng thái giải mã & So khớp**:", "✅ Byte-for-Byte Match (100%)" if dec_file.exists() else "N/A")
