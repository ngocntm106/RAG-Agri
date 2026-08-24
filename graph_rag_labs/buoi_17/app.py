"""
Application: app.py
Purpose: Streamlit Web UI Demo cho Buổi 18 — AI Compliance Checker (UC3) & AI Audit Checklist Generator (UC4).
Tích hợp RBAC, Audit Trail & Citations cho Ngân hàng Agribank.
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

from buoi_17.scripts.compliance_checker import ComplianceChecker
from buoi_17.scripts.audit_checklist_gen import AuditChecklistGenerator
from buoi_17.scripts.audit_logger import AuditLogger

# ----------------------------------------------------
# PAGE CONFIG & STYLING
# ----------------------------------------------------
st.set_page_config(
    page_title="Agribank AI Compliance & Audit Assist System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        margin-bottom: 1.2rem;
    }
    .banner-warning {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        color: #92400E;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .status-badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .status-badge-medium {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .status-badge-low {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .card-box {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .citation-box {
        background-color: #F3F4F6;
        border-left: 4px solid #3B82F6;
        padding: 0.6rem 1rem;
        border-radius: 4px;
        font-size: 0.9rem;
        font-family: monospace;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# INITIALIZE ENGINES
# ----------------------------------------------------
@st.cache_resource
def get_engines():
    checker = ComplianceChecker()
    checklist_gen = AuditChecklistGenerator()
    logger = AuditLogger()
    return checker, checklist_gen, logger


checker_engine, checklist_engine, audit_logger = get_engines()

# ----------------------------------------------------
# HEADER & SIDEBAR
# ----------------------------------------------------
st.markdown('<div class="main-header">🛡️ AGRIBANK AI COMPLIANCE & AUDIT SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Hệ thống AI So sánh chéo Quy định Tuân thủ (UC3) & Sinh Checklist Kiểm toán (UC4)</div>', unsafe_allow_html=True)

st.markdown("""
<div class="banner-warning">
    ⚠️ <b>DEMO SẢN PHẨM AI KIỂM TOÁN:</b> Kết quả phát hiện mâu thuẫn và checklist do AI gợi ý chỉ đóng vai trò trợ lý hỗ trợ. Kiểm toán viên bắt buộc rà soát thực tế và đối chiếu văn bản gốc trước khi ban hành kết luận chính thức (Guardrail: <code>NEEDS_HUMAN_REVIEW</code>).
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Agribank_logo.svg/1200px-Agribank_logo.svg.png", width=180)
    st.title("⚙️ Cấu hình Hệ thống")
    
    user_id = st.text_input("User ID Demo", value="usr_auditor_01")
    user_role = st.selectbox(
        "Vai trò Người dùng (RBAC Role)",
        options=["Admin", "Risk_Manager", "KiemToanVien", "Staff"],
        index=0
    )
    
    st.markdown("---")
    st.subheader("🌐 Trạng thái Kết nối Dữ liệu")
    st.markdown("✅ **Internal Policies:** 10 Văn bản (24 Chunks)")
    st.markdown("✅ **Combined Secure CSV:** 811 Chunks tổng cộng")
    st.markdown("🤖 **LLM Engine:** `gemini-3.6-flash` (Active)")
    st.markdown(f"👤 **Current Scope:** `{user_role}`")
    
    st.markdown("---")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    with col_sb2:
        if st.button("🧹 Clean Logs", use_container_width=True):
            log_p = CURRENT_DIR / "outputs" / "audit_log.jsonl"
            if log_p.exists():
                with open(log_p, "w", encoding="utf-8") as f:
                    f.write("")
                st.success("Đã xóa audit log!")
                time.sleep(0.5)
                st.rerun()

# ----------------------------------------------------
# MAIN TABS
# ----------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🔍 UC3 — AI Compliance Checker",
    "📋 UC4 — AI Audit Checklist Gen",
    "📜 Audit Log & System Trail"
])

# ====================================================
# TAB 1: UC3 — AI COMPLIANCE CHECKER
# ====================================================
with tab1:
    st.header("🔍 Use Case 3 — AI Compliance Checker")
    st.caption("So sánh chéo văn bản nội bộ Agribank & Thông tư NHNN, tự động phát hiện xung đột/chồng chéo kèm Điều/Khoản & Severity.")

    col_uc3_1, col_uc3_2 = st.columns([1, 1])

    with col_uc3_1:
        domain_uc3 = st.selectbox(
            "Chọn Miền nghiệp vụ (Domain) kiểm tra:",
            options=[
                "An toàn Kho quỹ & Vận chuyển",
                "CAR & Quản trị Rủi ro",
                "Tín dụng & Phán quyết Cho vay",
                "Bảo mật CNTT & AI",
                "Ngoại tệ & Phái sinh",
                "An toàn & Bảo hiểm Kho tiền",
                "Phân loại Nợ & Xử lý Nợ xấu"
            ],
            index=0
        )

    with col_uc3_2:
        doc_pair_option = st.selectbox(
            "Chọn Cặp Văn bản Đối chiếu:",
            options=[
                "Tự động quét các cặp VB theo Domain chọn",
                "100/QĐ-NHNO-AT vs 180/QĐ-NHNO-BH (Kho quỹ vs Bảo hiểm)",
                "250/QĐ-NHNO-QLRR vs Thông tư 41/2016/TT-NHNN (CAR)",
                "315/QC-NHNO-TD vs 390/QĐ-NHNO-XLN (Tín dụng vs Xử lý nợ)"
            ],
            index=0
        )

    if st.button("⚡ Phát hiện Xung đột & Mâu thuẫn Quy định", type="primary", use_container_width=True):
        with st.spinner("Đang truy xuất Điều/Khoản và phân tích mâu thuẫn bằng AI..."):
            if "100/QĐ-NHNO-AT" in doc_pair_option:
                doc_a, doc_b = "agr_at01", "agr_bh06"
            elif "250/QĐ-NHNO-QLRR" in doc_pair_option:
                doc_a, doc_b = "agr_car02", "117310"
            elif "315/QC-NHNO-TD" in doc_pair_option:
                doc_a, doc_b = "agr_td03", "agr_xln10"
            else:
                if "Kho" in domain_uc3:
                    doc_a, doc_b = "agr_at01", "agr_bh06"
                elif "CAR" in domain_uc3:
                    doc_a, doc_b = "agr_car02", "117310"
                elif "Tín dụng" in domain_uc3:
                    doc_a, doc_b = "agr_td03", "agr_xln10"
                else:
                    doc_a, doc_b = "agr_at01", "agr_bh06"

            conflicts = checker_engine.check_conflict_between_docs(
                doc_a_id=doc_a,
                doc_b_id=doc_b,
                domain=domain_uc3,
                user_role=user_role,
                user_id_demo=user_id
            )
            st.session_state["latest_conflicts"] = conflicts

    # Display Conflicts
    conflicts_data = st.session_state.get("latest_conflicts", None)
    if conflicts_data is not None:
        st.markdown("---")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Tổng mâu thuẫn phát hiện", len(conflicts_data))
        col_m2.metric("Số xung đột HIGH Severity", sum(1 for c in conflicts_data if c.get("severity") == "HIGH"))
        col_m3.metric("Human Review Guardrail", "100% Active")

        if not conflicts_data:
            st.success("✅ Không phát hiện mâu thuẫn rõ ràng giữa 2 văn bản này!")
        else:
            for idx, cfl in enumerate(conflicts_data, 1):
                sev = cfl.get("severity", "MEDIUM")
                if sev == "HIGH":
                    badge_html = '<span class="status-badge-high">🔴 HIGH SEVERITY</span>'
                elif sev == "MEDIUM":
                    badge_html = '<span class="status-badge-medium">🟡 MEDIUM SEVERITY</span>'
                else:
                    badge_html = '<span class="status-badge-low">🟢 LOW SEVERITY</span>'
                
                with st.expander(f"📍 [{cfl.get('conflict_id')}] Xung đột {idx}: {cfl.get('conflict_type')} — {cfl.get('domain')}", expanded=True):
                    st.markdown(f"**Mức độ Rủi ro:** {badge_html} &nbsp;|&nbsp; **Guardrail Flag:** `NEEDS_HUMAN_REVIEW`", unsafe_allow_html=True)
                    st.markdown(f"**Phân tích Chi tiết từ AI:** {cfl.get('description')}")
                    
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        st.markdown("**📜 Văn bản A (Quy định gốc A):**")
                        st.markdown(f"<div class='citation-box'>{cfl.get('doc_a_citation')}</div>", unsafe_allow_html=True)
                        st.caption(f"Nội dung: {cfl.get('doc_a_text')}")

                    with c_col2:
                        st.markdown("**📜 Văn bản B (Quy định gốc B):**")
                        st.markdown(f"<div class='citation-box'>{cfl.get('doc_b_citation')}</div>", unsafe_allow_html=True)
                        st.caption(f"Nội dung: {cfl.get('doc_b_text')}")

            # Export Section
            st.markdown("### 📥 Xuất Báo cáo Kết quả UC3")
            df_exp = pd.DataFrame(conflicts_data)
            csv_bytes = df_exp.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            
            exp_c1, exp_c2 = st.columns(2)
            with exp_c1:
                st.download_button(
                    label="💾 Tải xuống Danh sách Conflicts (CSV)",
                    data=csv_bytes,
                    file_name="compliance_conflicts.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with exp_c2:
                report_p = CURRENT_DIR / "outputs" / "compliance_conflict_report.md"
                md_text = report_p.read_text(encoding="utf-8") if report_p.exists() else "Báo cáo mâu thuẫn quy định UC3"
                st.download_button(
                    label="📄 Tải xuống Báo cáo Kiểm toán (Markdown)",
                    data=md_text.encode("utf-8"),
                    file_name="compliance_conflict_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )


# ====================================================
# TAB 2: UC4 — AI AUDIT CHECKLIST GENERATOR
# ====================================================
with tab2:
    st.header("📋 Use Case 4 — AI Audit Checklist Generator")
    st.caption("Nhập Phạm vi Kiểm toán (Domain & Unit scope), AI tự động lập bản nháp Checklist Kiểm toán kèm Citation & Mức Rủi ro.")

    c_uc4_1, c_uc4_2 = st.columns(2)
    with c_uc4_1:
        domain_uc4 = st.selectbox(
            "Chọn Miền Kiểm toán (Domain):",
            options=[
                "An toàn Kho quỹ",
                "Bảo mật CNTT & AI",
                "CAR & Quản trị Rủi ro",
                "Phán quyết Tín dụng",
                "Phân loại Nợ & Xử lý nợ",
                "Kinh doanh Ngoại tệ",
                "Tài chính Mua sắm",
                "Nhân sự & Đào tạo"
            ],
            index=0
        )

    with c_uc4_2:
        unit_uc4 = st.selectbox(
            "Chọn Đơn vị được Kiểm toán (Unit Scope):",
            options=[
                "Chi nhánh loại I & Phòng Giao dịch",
                "Khối CNTT & Trung tâm Dữ liệu",
                "Phòng Kế toán & Tài chính",
                "Phòng Quản lý Rủi ro",
                "Hội đồng Thẩm định Tín dụng",
                "Tổ Xử lý Nợ xấu Chi nhánh"
            ],
            index=0
        )

    if st.button("📋 Tạo Bản Nháp Checklist Kiểm Toán", type="primary", use_container_width=True):
        with st.spinner("Đang tổng hợp quy định và sinh bản nháp Checklist..."):
            items = checklist_engine.generate_checklist(
                domain=domain_uc4,
                unit=unit_uc4,
                user_role=user_role,
                user_id_demo=user_id
            )
            st.session_state["latest_checklist"] = items

    # Display Checklist
    chk_data = st.session_state.get("latest_checklist", None)
    if chk_data is not None:
        st.markdown("---")
        chk_m1, chk_m2, chk_m3 = st.columns(3)
        chk_m1.metric("Tổng đầu mục Checklist", len(chk_data))
        chk_m2.metric("Số mục Rủi ro HIGH", sum(1 for item in chk_data if item.get("risk_level") == "HIGH"))
        chk_m3.metric("Citation Gốc Attached", "100%")

        st.markdown("### 📋 Bảng Checklist Kiểm toán Chi tiết")
        
        for idx, item in enumerate(chk_data, 1):
            rlevel = item.get("risk_level", "MEDIUM")
            if rlevel == "HIGH":
                badge_html = '<span class="status-badge-high">🔴 HIGH RISK</span>'
            elif rlevel == "MEDIUM":
                badge_html = '<span class="status-badge-medium">🟡 MEDIUM RISK</span>'
            else:
                badge_html = '<span class="status-badge-low">🟢 LOW RISK</span>'

            with st.expander(f"📌 Mục {idx}: [{item.get('item_id')}] {item.get('audit_question')}", expanded=True):
                st.markdown(f"**Miền nghiệp vụ:** `{item.get('domain')}` &nbsp;|&nbsp; **Phạm vi áp dụng:** `{item.get('unit_scope')}`", unsafe_allow_html=True)
                st.markdown(f"**Mức độ Rủi ro:** {badge_html} &nbsp;|&nbsp; **Cờ Guardrail:** `NEEDS_HUMAN_REVIEW`", unsafe_allow_html=True)
                st.markdown(f"**Rủi ro tiềm ẩn:** {item.get('risk_description')}")
                st.markdown(f"**📖 Văn bản & Điều khoản Gốc (Citation):**")
                st.markdown(f"<div class='citation-box'>{item.get('source_citation')}</div>", unsafe_allow_html=True)

        # Export Buttons
        st.markdown("### 📥 Xuất Checklist Kiểm toán")
        df_chk = pd.DataFrame(chk_data)
        csv_chk_bytes = df_chk.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        json_chk_bytes = json.dumps(chk_data, indent=2, ensure_ascii=False).encode("utf-8")

        chk_exp1, chk_exp2 = st.columns(2)
        with chk_exp1:
            st.download_button(
                label="💾 Tải xuống Checklist (CSV)",
                data=csv_chk_bytes,
                file_name="audit_checklist_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with chk_exp2:
            st.download_button(
                label="📄 Tải xuống Checklist (JSON)",
                data=json_chk_bytes,
                file_name="audit_checklist_results.json",
                mime="application/json",
                use_container_width=True
            )


# ====================================================
# TAB 3: AUDIT LOG & SYSTEM TRAIL
# ====================================================
with tab3:
    st.header("📜 Audit Log & System Trail")
    st.caption("Ghi nhận toàn bộ nhật ký truy vết hệ thống RAG, RBAC filtering, thao tác Check Conflict và Gen Checklist.")

    log_path = CURRENT_DIR / "outputs" / "audit_log.jsonl"
    
    if not log_path.exists() or os.path.getsize(log_path) == 0:
        st.info("Chưa có nhật ký kiểm toán nào được ghi nhận.")
    else:
        logs = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line.strip()))
                    except Exception:
                        pass

        st.markdown(f"**Tổng số bản ghi Audit Trail:** `{len(logs)}` events | **File Log:** `{log_path.name}`")

        # Filters
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            roles_filter = st.selectbox("Lọc theo User Role:", options=["All"] + list(set(r for l in logs for r in (l.get("user_role") if isinstance(l.get("user_role"), list) else [l.get("user_role")]))))
        with f_col2:
            actions_filter = st.selectbox("Lọc theo Action:", options=["All"] + list(set(l.get("action", "N/A") for l in logs)))

        filtered_logs = logs
        if roles_filter != "All":
            filtered_logs = [l for l in filtered_logs if roles_filter in (l.get("user_role") if isinstance(l.get("user_role"), list) else [l.get("user_role")])]
        if actions_filter != "All":
            filtered_logs = [l for l in filtered_logs if l.get("action") == actions_filter]

        st.dataframe(
            pd.DataFrame(filtered_logs)[["timestamp", "request_id", "user_id_demo", "user_role", "action", "query", "status"]],
            use_container_width=True
        )

        with st.expander("🔍 Xem chi tiết Raw JSON Event Log mới nhất"):
            if logs:
                st.json(logs[-1])
