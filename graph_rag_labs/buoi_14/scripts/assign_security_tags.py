"""
Script: assign_security_tags.py
Purpose: Classify and assign Role-Based Access Control (RBAC) security tags (allowed_roles)
         to each normalized chunk in the corpus.

Output: buoi_14/data/processed/chunks_secure.csv
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd

# Ensure project root is in sys.path and stdout is UTF-8
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

from src.config import (
    ROLE_ADMIN,
    ROLE_HR,
    ROLE_STAFF,
    ROLE_GUEST,
    VALID_ROLES,
    CHUNKS_NORMALIZED_PATH,
    CHUNKS_SECURE_PATH
)

# ==============================================================================
# KEYWORD & HEURISTIC DICTIONARIES FOR CLASSIFICATION
# ==============================================================================

# Nhóm từ khóa nhân sự, tuyển dụng, lương thưởng, bổ nhiệm, kỷ luật
HR_KEYWORDS = [
    "nhân sự", "tiền lương", "lương thưởng", "tuyển dụng", "bổ nhiệm",
    "kỷ luật", "thôi việc", "nghỉ việc", "chế độ thai sản", "bảo hiểm xã hội",
    "đãi ngộ", "phụ cấp", "hợp đồng lao động", "tiêu chuẩn người quản lý",
    "chuyên gia tính toán", "bổ nhiệm lại", "miễn nhiệm", "cách chức",
    "chức danh quản lý", "chứng chỉ đại lý", "đào tạo nhân viên",
    "tiêu chuẩn tổng giám đốc", "chủ tịch hội đồng", "bằng cấp chuyên môn"
]

# Nhóm từ khóa tín dụng, rủi ro, hạn mức, phê duyệt duyệt vay, kho quỹ
RISK_STAFF_KEYWORDS = [
    "tín dụng", "rủi ro", "hạn mức", "phê duyệt", "duyệt vay", "khoản vay",
    "tỷ lệ an toàn vốn", "bảo lãnh", "thu nợ", "nợ xấu", "giải ngân",
    "tài sản bảo đảm", "thẩm định", "trích lập dự phòng", "vốn tự có",
    "ngoại tệ", "dự trữ ngoại hối", "vận chuyển tiền", "niêm phong",
    "kho quỹ", "tài sản quý", "giấy tờ có giá", "thanh khoản",
    "quỹ tín dụng", "tổ chức lại", "kiểm soát đặc biệt"
]

def classify_chunk(row: pd.Series) -> list[str]:
    """
    Phân loại quyền truy cập cho từng chunk dựa trên tiêu đề, điều khoản và nội dung.
    
    Quy tắc phân cấp:
    1. HR Sensitive (Lương thưởng, bổ nhiệm, nhân sự, kỷ luật):
       -> allowed_roles = ["Admin", "HR"]
    2. Staff Internal / Operations / Risk / Credit (Tín dụng, rủi ro, phê duyệt vay, kho quỹ):
       -> allowed_roles = ["Admin", "Staff"]
    3. General / Public (Quy định chung, định nghĩa, chính sách thị trường):
       -> allowed_roles = ["Admin", "HR", "Staff", "Guest"]
    """
    text_content = str(row.get("text", "")).lower()
    title_content = str(row.get("title", "")).lower()
    article_content = str(row.get("article", "")).lower()
    full_context = f"{title_content} {article_content} {text_content}"

    # 1. Kiểm tra nhóm nhân sự / HR
    for kw in HR_KEYWORDS:
        if kw in full_context:
            return [ROLE_ADMIN, ROLE_HR]

    # 2. Kiểm tra nhóm tín dụng / rủi ro / nghiệp vụ nội bộ Staff
    for kw in RISK_STAFF_KEYWORDS:
        if kw in full_context:
            return [ROLE_ADMIN, ROLE_STAFF]

    # 3. Quy định chung cho mọi đối tượng
    return [ROLE_ADMIN, ROLE_HR, ROLE_STAFF, ROLE_GUEST]


def assign_security_tags(input_path: Path, output_path: Path) -> pd.DataFrame:
    """
    Đọc chunks_normalized.csv, gán allowed_roles và ghi ra chunks_secure.csv.
    """
    print(f"[1/4] Đang đọc dữ liệu chuẩn hóa từ: {input_path}")
    if not input_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại {input_path}")

    df = pd.read_csv(input_path)
    total_chunks = len(df)
    print(f"      Tổng số chunks: {total_chunks:,}")

    print("[2/4] Đang thực hiện phân loại bảo mật theo vai trò (RBAC Security Tagging)...")
    # Gán danh sách vai trò
    df["allowed_roles_list"] = df.apply(classify_chunk, axis=1)
    
    # Lưu dưới dạng chuỗi JSON chuẩn trong file CSV
    df["allowed_roles"] = df["allowed_roles_list"].apply(lambda roles: json.dumps(roles, ensure_ascii=False))

    # Xóa cột tạm
    df = df.drop(columns=["allowed_roles_list"])

    print(f"[3/4] Đang lưu tập dữ liệu có gắn thẻ bảo mật ra: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"      Ghi thành công {len(df):,} dòng vào {output_path.name}")

    return df


def verify_security_tags(df: pd.DataFrame):
    """
    Kiểm tra tính toàn vẹn dữ liệu phân quyền và in báo cáo thống kê.
    """
    print("\n[4/4] === KIỂM TRA TOÀN VẸN VÀ THỐNG KÊ PHÂN BỔ QUYỀN (AUDIT) ===")
    
    # 1. Kiểm tra không có dòng nào bị rỗng/null
    null_roles = df["allowed_roles"].isna().sum()
    empty_roles = (df["allowed_roles"] == "").sum()
    invalid_format = 0
    
    group_counts = {}
    valid_roles_set = set(VALID_ROLES)

    for idx, raw_val in enumerate(df["allowed_roles"]):
        try:
            roles = json.loads(raw_val) if isinstance(raw_val, str) else raw_val
            if not isinstance(roles, list) or len(roles) == 0:
                invalid_format += 1
            # Kiểm tra xem các role có nằm trong VALID_ROLES không
            if not all(r in valid_roles_set for r in roles):
                invalid_format += 1
            
            group_key = "+".join(roles)
            group_counts[group_key] = group_counts.get(group_key, 0) + 1
        except Exception:
            invalid_format += 1

    print(f" - Tổng số dòng kiểm tra: {len(df):,}")
    print(f" - Số dòng bị NULL/NaN: {null_roles} (Yêu cầu: 0)")
    print(f" - Số dòng bị rỗng ('') : {empty_roles} (Yêu cầu: 0)")
    print(f" - Số dòng sai định dạng/vai trò: {invalid_format} (Yêu cầu: 0)")

    assert null_roles == 0 and empty_roles == 0 and invalid_format == 0, "LỖI: Dữ liệu phân quyền có dòng không hợp lệ!"

    # 2. Thống kê phân bổ
    print("\n--- THỐNG KÊ PHÂN BỔ THEO NHÓM VAI TRÒ ---")
    for group, count in sorted(group_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f" • Nhóm [{group:<32}]: {count:>5,} chunks ({percentage:>5.2f}%)")

    # 3. Hiển thị 3 mẫu đại diện cho 3 cấp độ bảo mật
    print("\n--- 3 MẪU DỮ LIỆU ĐẠI DIỆN CHO CÁC CẤP ĐỘ BẢO MẬT KHÁC NHAU ---")
    
    # Mẫu 1: HR Sensitive
    hr_samples = df[df["allowed_roles"].str.contains(ROLE_HR) & (~df["allowed_roles"].str.contains(ROLE_GUEST))]
    if not hr_samples.empty:
        sample_hr = hr_samples.iloc[0]
        print(f"\n[MẪU 1 - HR SENSITIVE: {sample_hr['allowed_roles']}]")
        print(f" Chunk ID : {sample_hr['chunk_id']}")
        print(f" Văn bản  : {sample_hr['source_file']} - {str(sample_hr['title'])[:60]}...")
        print(f" Điều     : {sample_hr.get('article', 'N/A')}")
        print(f" Nội dung : {str(sample_hr['text'])[:160]}...")

    # Mẫu 2: Staff / Operational Internal
    staff_samples = df[df["allowed_roles"].str.contains(ROLE_STAFF) & (~df["allowed_roles"].str.contains(ROLE_GUEST))]
    if not staff_samples.empty:
        sample_staff = staff_samples.iloc[0]
        print(f"\n[MẪU 2 - STAFF INTERNAL / RISK: {sample_staff['allowed_roles']}]")
        print(f" Chunk ID : {sample_staff['chunk_id']}")
        print(f" Văn bản  : {sample_staff['source_file']} - {str(sample_staff['title'])[:60]}...")
        print(f" Điều     : {sample_staff.get('article', 'N/A')}")
        print(f" Nội dung : {str(sample_staff['text'])[:160]}...")

    # Mẫu 3: Guest / Public Regulations
    guest_samples = df[df["allowed_roles"].str.contains(ROLE_GUEST)]
    if not guest_samples.empty:
        sample_guest = guest_samples.iloc[0]
        print(f"\n[MẪU 3 - GENERAL / PUBLIC: {sample_guest['allowed_roles']}]")
        print(f" Chunk ID : {sample_guest['chunk_id']}")
        print(f" Văn bản  : {sample_guest['source_file']} - {str(sample_guest['title'])[:60]}...")
        print(f" Điều     : {sample_guest.get('article', 'N/A')}")
        print(f" Nội dung : {str(sample_guest['text'])[:160]}...")

    print("\n[SUCCESS] Phân loại và gắn tag bảo mật RBAC hoàn tất thành công 100%!")


if __name__ == "__main__":
    df_secure = assign_security_tags(
        input_path=CHUNKS_NORMALIZED_PATH,
        output_path=CHUNKS_SECURE_PATH
    )
    verify_security_tags(df_secure)
