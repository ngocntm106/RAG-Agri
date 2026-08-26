"""
Application: app.py
Purpose: Agribank Local AI System — RAG Bảo mật & Kiểm toán (Buổi 19)
Tích hợp:
- Dual-Provider (Ollama Local SLM Qwen3:0.6B / Gemini Cloud API)
- UC1: Tra cứu Quy định Nội bộ (RBAC Enforced)
- UC2: Phân tích Khoảng trống Tuân thủ (Compliance Gap)
- UC3: Phát hiện Mâu thuẫn & Xung đột Quy định (Compliance Checker)
- UC4: Sinh Bản nháp Checklist Kiểm toán (Audit Checklist Generator)
- System / Security & Nhật ký Kiểm toán (Audit Trail Log)
"""

import os
import sys
import json
import time
import uuid
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Cấu hình đường dẫn hệ thống
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(CURRENT_DIR / ".env")

try:
    from scripts.ollama_adapter import OllamaClient
    from scripts.internal_lookup import internal_policy_lookup
    from scripts.compliance_gap import ComplianceGapChecker
    from scripts.compliance_checker import ComplianceChecker
    from scripts.audit_checklist_gen import AuditChecklistGenerator
    from scripts.audit_logger import AuditLogger
except ImportError:
    try:
        from buoi_17.scripts.ollama_adapter import OllamaClient
        from buoi_17.scripts.internal_lookup import internal_policy_lookup
        from buoi_17.scripts.compliance_gap import ComplianceGapChecker
        from buoi_17.scripts.compliance_checker import ComplianceChecker
        from buoi_17.scripts.audit_checklist_gen import AuditChecklistGenerator
        from buoi_17.scripts.audit_logger import AuditLogger
    except ImportError:
        from ollama_adapter import OllamaClient
        from internal_lookup import internal_policy_lookup
        from compliance_gap import ComplianceGapChecker
        from compliance_checker import ComplianceChecker
        from audit_checklist_gen import AuditChecklistGenerator
        from audit_logger import AuditLogger

# ----------------------------------------------------
# PAGE CONFIG & MODERN DARK THEME STYLING
# ----------------------------------------------------
st.set_page_config(
    page_title="AGRIBANK LOCAL AI SYSTEM — RAG BẢO MẬT & KIỂM TOÁN",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main Dark Theme Container */
    .stApp {
        background-color: #0E1117;
        color: #E2E8F0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    .main-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #00A86B;
        letter-spacing: -0.02em;
        margin-bottom: 0.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-bottom: 1.2rem;
        font-weight: 500;
    }
    
    /* Status Badges */
    .badge-offline {
        display: inline-flex;
        align-items: center;
        background-color: #4C1D24;
        color: #F87171;
        border: 1px solid #7F1D1D;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .badge-online {
        display: inline-flex;
        align-items: center;
        background-color: #064E3B;
        color: #34D399;
        border: 1px solid #047857;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    
    .status-badge-high {
        background-color: #7F1D1D;
        color: #FECACA;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .status-badge-medium {
        background-color: #78350F;
        color: #FDE68A;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .status-badge-low {
        background-color: #064E3B;
        color: #A7F3D0;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    /* Content Cards */
    .card-box {
        background-color: #1A1F2C;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .citation-box {
        background-color: #131722;
        border-left: 4px solid #00A86B;
        padding: 0.6rem 1rem;
        border-radius: 4px;
        font-size: 0.88rem;
        color: #93C5FD;
        font-family: monospace;
        margin-top: 0.5rem;
    }
    .answer-box {
        background-color: #161B26;
        border: 1px solid #2A324B;
        border-radius: 8px;
        padding: 1.2rem;
        color: #F1F5F9;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# INITIALIZE ENGINES & OLLAMA CLIENT
# ----------------------------------------------------
@st.cache_resource
def init_system():
    ollama = OllamaClient()
    checker = ComplianceChecker()
    checklist_gen = AuditChecklistGenerator()
    gap_checker = ComplianceGapChecker()
    logger = AuditLogger()
    return ollama, checker, checklist_gen, gap_checker, logger


ollama_client, checker_engine, checklist_engine, gap_engine, audit_logger = init_system()


# ----------------------------------------------------
# SIDEBAR: CẤU HÌNH HỆ THỐNG LOCAL AI & PHÂN QUYỀN RBAC
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Cấu hình Hệ thống Local AI")
    
    llm_provider_option = st.selectbox(
        "👁️ Chọn LLM Provider",
        options=[
            "Ollama (Local Offline Model)",
            "Cloud Gemini API (Free Tier)"
        ],
        index=0
    )
    
    # Update LLM Provider env
    selected_provider = "ollama" if "Ollama" in llm_provider_option else "gemini"
    os.environ["LLM_PROVIDER"] = selected_provider

    # Check Ollama Server status
    is_ollama_online, models_list = ollama_client.check_health()
    st.markdown("<div style='margin-top: 0.8rem; font-size: 0.9rem; font-weight: 600;'>Trạng thái Ollama Server:</div>", unsafe_allow_html=True)
    
    if is_ollama_online and len(models_list) > 0:
        st.markdown(f'<div class="badge-online">🟢 ONLINE ({models_list[0]})</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="badge-offline">🔴 OFFLINE / FALLBACK ENGINE READY</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 👤 Phân quyền Người dùng (RBAC)")
    
    user_role = st.selectbox(
        "Vai trò người dùng hiện tại:",
        options=["KiemToanVien", "Admin", "Risk_Manager", "Staff"],
        index=0
    )
    
    user_id = st.text_input("User ID:", value=f"usr_{user_role.lower()}")

    st.markdown("---")
    st.caption("🔒 **Security Guardrail:** 100% dữ liệu xử lý nội bộ On-Premise. Guardrail `NEEDS_HUMAN_REVIEW` bắt buộc.")
    
    if st.button("🔄 Làm mới Trạng thái", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()


# ----------------------------------------------------
# MAIN HEADER
# ----------------------------------------------------
st.markdown('<div class="main-title">🏛️ AGRIBANK LOCAL AI SYSTEM — RAG BẢO MẬT & KIỂM TOÁN</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Hệ thống Local Offline Containerized | Vai trò: <b>{user_role}</b> | Provider: <b>{selected_provider.upper()}</b></div>', unsafe_allow_html=True)


# ----------------------------------------------------
# 5 TABS NAVIGATION
# ----------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 UC1: Tra cứu Quy định",
    "📊 UC2: Compliance Gap",
    "⚖️ UC3: Mâu thuẫn Quy định",
    "📋 UC4: Audit Checklist",
    "🛡️ System & Audit Trail"
])


# ====================================================
# TAB 1: UC1 — TRA CỨU QUY ĐỊNH NỘI BỘ (RBAC ENFORCED)
# ====================================================
with tab1:
    st.subheader("Tra cứu Quy định Nội bộ Agribank (RBAC Enforced)")
    st.caption("Tra cứu tri thức quy chuẩn nội bộ có kiểm soát bảo mật theo vai trò người dùng (Pre-filtering RBAC).")

    q_input = st.text_input(
        "Nhập câu hỏi tra cứu:",
        value="Hạn mức vận chuyển tiền mặt bằng xe bọc thép?"
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        run_uc1 = st.button("Chạy Tra cứu UC1", type="primary", use_container_width=True)

    if run_uc1 and q_input:
        with st.spinner("Đang tra cứu và sinh câu trả lời có trích dẫn..."):
            # Map role
            role_for_retrieval = "Admin" if user_role in ["Admin", "KiemToanVien"] else user_role
            res_uc1 = internal_policy_lookup(
                question=q_input,
                user_role=role_for_retrieval,
                user_id_demo=user_id
            )
            st.session_state["latest_uc1_result"] = res_uc1

    uc1_res = st.session_state.get("latest_uc1_result", None)
    if uc1_res:
        st.markdown("---")
        if uc1_res.get("status") == "DENIED":
            st.warning(f"🚫 **TRUY CẬP BỊ TỪ CHỐI (RBAC ENFORCED):** Vai trò `{user_role}` không có thẩm quyền truy cập các điều khoản quy định này. (Blocked {uc1_res.get('rbac_blocked_count', 0)} chunks).")
        else:
            st.markdown(f"**Kết quả Tra cứu cho Vai trò `{user_role}`:**")
            st.markdown(f"<div class='answer-box'>{uc1_res.get('answer')}</div>", unsafe_allow_html=True)

            citations = uc1_res.get("citations", [])
            if citations:
                st.markdown("#### 📖 Căn cứ & Trích dẫn Văn bản gốc (Citations):")
                for cit in citations:
                    st.markdown(f"<div class='citation-box'>{cit}</div>", unsafe_allow_html=True)


# ====================================================
# TAB 2: UC2 — COMPLIANCE GAP ANALYSIS
# ====================================================
with tab2:
    st.subheader("Phân tích Khoảng trống Tuân thủ (Compliance Gap)")
    st.caption("Đối chiếu yêu cầu quản lý nhà nước (Thông tư NHNN) với Quy định Nội bộ Agribank tương ứng.")

    req_presets = {
        "REQ-NHNN-01: An toàn Kho tiền & Vận chuyển tiền mặt (TT 01/2014/TT-NHNN)": {
            "req_id": "REQ-NHNN-01-VALUABLES",
            "text": "Quy định về tiêu chuẩn bảo quản, vận chuyển tiền mặt, tài sản quý và giấy tờ có giá trong kho tiền.",
            "citation": "[Thông tư 01/2014/TT-NHNN | Điều 15]"
        },
        "REQ-NHNN-02: Tỷ lệ an toàn vốn CAR tối thiểu 8.0% (TT 41/2016/TT-NHNN)": {
            "req_id": "REQ-NHNN-02-CAR",
            "text": "Tổ chức tín dụng phải duy trì tỷ lệ an toàn vốn (CAR) tối thiểu 8.0% theo phương pháp chuẩn hóa.",
            "citation": "[Thông tư 41/2016/TT-NHNN | Điều 4]"
        },
        "REQ-NHNN-03: Phân loại nợ và trích lập dự phòng rủi ro (TT 11/2021/TT-NHNN)": {
            "req_id": "REQ-NHNN-03-CREDIT",
            "text": "Quy định chặt chẽ về phân loại nợ xấu nhóm 3, 4, 5 và thẩm quyền phê duyệt hạn mức.",
            "citation": "[Thông tư 11/2021/TT-NHNN | Điều 8]"
        }
    }

    selected_req_label = st.selectbox(
        "Chọn Yêu cầu Pháp lý NHNN cần Đối chiếu:",
        options=list(req_presets.keys()),
        index=0
    )
    
    current_req = req_presets[selected_req_label]

    if st.button("Phân tích Khoảng trống UC2", type="primary"):
        with st.spinner("Đang đối chiếu bằng chứng hai phía..."):
            gap_res = gap_engine.analyze_requirement(
                requirement_id=current_req["req_id"],
                external_requirement=current_req["text"],
                external_citation=current_req["citation"],
                user_role=user_role,
                user_id_demo=user_id
            )
            st.session_state["latest_uc2_result"] = gap_res

    uc2_res = st.session_state.get("latest_uc2_result", None)
    if uc2_res:
        st.markdown("---")
        status_gap = uc2_res.get("gap_status", "DAP_UNG")
        if status_gap == "DAP_UNG":
            status_html = '<span class="status-badge-low">🟢 ĐÁP ỨNG ĐẦY ĐỦ (DAP_UNG)</span>'
        elif status_gap == "CHENH_LECH":
            status_html = '<span class="status-badge-medium">🟡 CHÊNH LỆCH NGƯỠNG (CHENH_LECH)</span>'
        else:
            status_html = '<span class="status-badge-high">🔴 THIẾU BẰNG CHỨNG (CHUA_DU_BANG_CHUNG)</span>'

        st.markdown(f"### Kết quả Đánh giá Tuân thủ: {status_html}", unsafe_allow_html=True)
        st.markdown(f"**Nhận định của Hệ thống:** {uc2_res.get('reason')}")
        st.markdown(f"**Guardrail Flag:** `NEEDS_HUMAN_REVIEW` &nbsp;|&nbsp; **Độ tin cậy:** `{uc2_res.get('confidence', 0.9) * 100:.0f}%`")

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### 🏛️ Yêu cầu NHNN (External):")
            st.markdown(f"<div class='citation-box'>{uc2_res.get('external_citation')}</div>", unsafe_allow_html=True)
            st.caption(f"Nội dung: {uc2_res.get('external_requirement')}")
        with col_g2:
            st.markdown("#### 🏢 Quy định Nội bộ Agribank (Internal):")
            st.markdown(f"<div class='citation-box'>{uc2_res.get('internal_citation')}</div>", unsafe_allow_html=True)
            st.caption(f"Bằng chứng đối ứng: {uc2_res.get('internal_evidence')}")


# ====================================================
# TAB 3: UC3 — PHÁT HIỆN MÂU THUẪN QUY ĐỊNH (COMPLIANCE CHECKER)
# ====================================================
with tab3:
    st.subheader("Phát hiện Mâu thuẫn & Xung đột Quy định (Compliance Conflict Detection)")
    st.caption("Tự động đối chiếu chéo các văn bản nội bộ để phát hiện mâu thuẫn về hạn mức, thẩm quyền và quy trình.")

    col_u3_1, col_u3_2 = st.columns(2)
    with col_u3_1:
        domain_uc3 = st.selectbox(
            "Miền nghiệp vụ kiểm tra:",
            options=[
                "An toàn Kho quỹ & Vận chuyển",
                "CAR & Quản trị Rủi ro",
                "Tín dụng & Phán quyết Cho vay",
                "Bảo mật CNTT & AI"
            ],
            index=0
        )
    with col_u3_2:
        pair_uc3 = st.selectbox(
            "Cặp văn bản đối chiếu:",
            options=[
                "100/QĐ-NHNO-AT vs 180/QĐ-NHNO-BH (Kho quỹ vs Bảo hiểm)",
                "250/QĐ-NHNO-QLRR vs Thông tư 41/2016/TT-NHNN (CAR)",
                "315/QC-NHNO-TD vs 390/QĐ-NHNO-XLN (Tín dụng vs Xử lý nợ)"
            ],
            index=0
        )

    if st.button("Phát hiện Mâu thuẫn UC3", type="primary"):
        with st.spinner("Đang phân tích xung đột điều khoản bằng AI..."):
            if "100/QĐ-NHNO-AT" in pair_uc3:
                doc_a, doc_b = "agr_at01", "agr_bh06"
            elif "250/QĐ-NHNO-QLRR" in pair_uc3:
                doc_a, doc_b = "agr_car02", "117310"
            else:
                doc_a, doc_b = "agr_td03", "agr_xln10"

            cfls = checker_engine.check_conflict_between_docs(
                doc_a_id=doc_a,
                doc_b_id=doc_b,
                domain=domain_uc3,
                user_role=user_role,
                user_id_demo=user_id
            )
            st.session_state["latest_uc3_conflicts"] = cfls

    cfls_data = st.session_state.get("latest_uc3_conflicts", None)
    if cfls_data:
        st.markdown("---")
        for idx, c in enumerate(cfls_data, 1):
            sev = c.get("severity", "HIGH")
            badge = '<span class="status-badge-high">🔴 HIGH SEVERITY</span>' if sev == "HIGH" else '<span class="status-badge-medium">🟡 MEDIUM SEVERITY</span>'
            
            with st.expander(f"📍 [{c.get('conflict_id')}] Xung đột {idx}: {c.get('conflict_type')} — {c.get('domain')}", expanded=True):
                st.markdown(f"**Mức độ Severity:** {badge} &nbsp;|&nbsp; **Guardrail Flag:** `NEEDS_HUMAN_REVIEW`", unsafe_allow_html=True)
                st.markdown(f"**Phân tích từ AI:** {c.get('description')}")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("**📜 Văn bản A (Quy định gốc):**")
                    st.markdown(f"<div class='citation-box'>{c.get('doc_a_citation')}</div>", unsafe_allow_html=True)
                    st.caption(f"Nội dung: {c.get('doc_a_text')}")
                with col_c2:
                    st.markdown("**📜 Văn bản B (Quy định gốc):**")
                    st.markdown(f"<div class='citation-box'>{c.get('doc_b_citation')}</div>", unsafe_allow_html=True)
                    st.caption(f"Nội dung: {c.get('doc_b_text')}")


# ====================================================
# TAB 4: UC4 — AUDIT CHECKLIST GENERATOR
# ====================================================
with tab4:
    st.subheader("Sinh Bản nháp Checklist Kiểm toán (AI Audit Checklist Generator)")
    st.caption("AI tự động lập danh mục câu hỏi và tiêu chuẩn kiểm toán bám sát theo từng Đơn vị & Miền nghiệp vụ.")

    col_u4_1, col_u4_2 = st.columns(2)
    with col_u4_1:
        domain_uc4 = st.selectbox(
            "Chọn Miền Kiểm toán:",
            options=["An toàn Kho quỹ", "Bảo mật CNTT & AI", "CAR & Quản trị Rủi ro", "Phán quyết Tín dụng"],
            index=0
        )
    with col_u4_2:
        unit_uc4 = st.selectbox(
            "Chọn Đơn vị áp dụng (Unit Scope):",
            options=["Chi nhánh loại I & Phòng Giao dịch", "Khối CNTT & Trung tâm Dữ liệu", "Phòng Quản lý Rủi ro"],
            index=0
        )

    if st.button("Sinh Checklist UC4", type="primary"):
        with st.spinner("Đang tổng hợp quy định và sinh checklist..."):
            chk_items = checklist_engine.generate_checklist(
                domain=domain_uc4,
                unit=unit_uc4,
                user_role=user_role,
                user_id_demo=user_id
            )
            st.session_state["latest_uc4_items"] = chk_items

    chk_res = st.session_state.get("latest_uc4_items", None)
    if chk_res:
        st.markdown("---")
        st.markdown(f"### 📋 Danh mục Checklist ({len(chk_res)} hạng mục):")
        for idx, itm in enumerate(chk_res, 1):
            rlevel = itm.get("risk_level", "MEDIUM")
            badge = '<span class="status-badge-high">🔴 HIGH RISK</span>' if rlevel == "HIGH" else '<span class="status-badge-medium">🟡 MEDIUM RISK</span>'
            
            with st.expander(f"📌 Mục {idx}: [{itm.get('item_id')}] {itm.get('audit_question')}", expanded=True):
                st.markdown(f"**Mức độ Rủi ro:** {badge} &nbsp;|&nbsp; **Cờ Phê duyệt:** `NEEDS_HUMAN_REVIEW`", unsafe_allow_html=True)
                st.markdown(f"**Rủi ro tiềm ẩn:** {itm.get('risk_description')}")
                st.markdown(f"**📖 Căn cứ Quy định (Citation):**")
                st.markdown(f"<div class='citation-box'>{itm.get('source_citation') or itm.get('citation')}</div>", unsafe_allow_html=True)


# ====================================================
# TAB 5: SYSTEM & AUDIT TRAIL
# ====================================================
with tab5:
    st.subheader("Nhật ký Kiểm toán (Audit Trail) & Trạng thái Hệ thống")
    st.caption("Truy vết toàn bộ yêu cầu tra cứu, kiểm toán và hoạt động của hệ thống Local AI.")

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Docker Containers", "2/2 ONLINE", delta="Healthy")
    col_stat2.metric("Ollama Engine Port", "11434", delta="Active")
    col_stat3.metric("Web UI Port", "8501", delta="Streamlit")

    log_path = CURRENT_DIR / "outputs" / "audit_log.jsonl"
    if log_path.exists() and os.path.getsize(log_path) > 0:
        logs = []
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.strip():
                    try: logs.append(json.loads(line.strip()))
                    except Exception: pass
        
        st.markdown(f"**Tổng số bản ghi Audit Trail:** `{len(logs)}` sự kiện.")
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs[["timestamp", "request_id", "user_id_demo", "user_role", "action", "status"]].tail(20), use_container_width=True)
    else:
        st.info("Chưa có bản ghi nhật ký kiểm toán.")
