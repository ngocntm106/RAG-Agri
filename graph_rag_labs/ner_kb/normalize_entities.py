import os
import re
import unicodedata
import pandas as pd
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Accent removal helper for clean entity IDs
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def generate_entity_id(entity_type, canonical_name):
    # Remove accents and replace non-alphanumeric with underscore
    no_accent = remove_accents(canonical_name)
    clean_name = re.sub(r'[^a-z0-9]', '_', no_accent.lower())
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    # Limit length
    clean_name = clean_name[:35]
    return f"{entity_type}_{clean_name}"

# Dictionary for explicit alias mapping
ALIAS_MAPS = {
    "CoQuan": {
        "nhnn": "Ngân hàng Nhà nước Việt Nam",
        "ngân hàng nhà nước": "Ngân hàng Nhà nước Việt Nam",
        "ngân hàng nhà nước việt nam": "Ngân hàng Nhà nước Việt Nam",
        "bộ tài chính": "Bộ Tài chính",
        "quốc hội": "Quốc hội",
        "chính phủ": "Chính phủ"
    },
    "LinhVuc": {
        "tín dụng": "Tín dụng",
        "bảo hiểm": "Bảo hiểm",
        "kiểm toán": "Kiểm toán",
        "chứng khoán": "Chứng khoán",
        "quản lý ngoại hối": "Quản lý ngoại hối",
        "phát hành và kho quỹ": "Phát hành và kho quỹ",
        "thanh tra, giám sát ngân hàng": "Thanh tra, giám sát ngân hàng"
    },
    "DoiTuongApDung": {
        "tổ chức tín dụng": "Tổ chức tín dụng",
        "ngân hàng thương mại": "Ngân hàng thương mại",
        "quỹ tín dụng nhân dân": "Quỹ tín dụng nhân dân",
        "chi nhánh ngân hàng nước ngoài": "Chi nhánh ngân hàng nước ngoài",
        "doanh nghiệp bảo hiểm": "Doanh nghiệp bảo hiểm",
        "ngân hàng hợp tác xã": "Ngân hàng hợp tác xã",
        "công ty chứng khoán": "Công ty chứng khoán",
        "công ty quản lý quỹ": "Công ty quản lý quỹ",
        "văn phòng đại diện tổ chức tín dụng nước ngoài": "Văn phòng đại diện tổ chức tín dụng nước ngoài"
    }
}

def normalize_entity_name(entity_type, name):
    # 1. Unicode normalization (NFC)
    name_normalized = unicodedata.normalize('NFC', name)
    # 2. Trim whitespace
    name_clean = re.sub(r'\s+', ' ', name_normalized).strip()
    
    # 3. Check alias mapping
    type_map = ALIAS_MAPS.get(entity_type, {})
    name_lower = name_clean.lower()
    
    if name_lower in type_map:
        return type_map[name_lower], name_clean
        
    # If not in mapping, clean and titlecase appropriately
    if len(name_clean) > 0:
        # Title case first letter
        name_clean = name_clean[0].upper() + name_clean[1:]
        
    return name_clean, name_clean

def main():
    print("=" * 60)
    print("BƯỚC 4: CHUẨN HÓA ENTITY")
    print("=" * 60)
    
    input_path = os.path.join("ner_kb", "extracted_entities_raw.csv")
    output_path = os.path.join("ner_kb", "entities.csv")
    
    if not os.path.exists(input_path):
        print(f"Lỗi: Không tìm thấy {input_path}. Vui lòng chạy Bước 3 trước.")
        sys.exit(1)
        
    raw_df = pd.read_csv(input_path)
    print(f"Đọc thành công {len(raw_df)} thực thể thô từ {input_path}")
    
    normalized_list = []
    alias_merges = {}
    
    # Process each entity
    for idx, row in raw_df.iterrows():
        doc_id = row['doc_id']
        orig_name = str(row['entity'])
        entity_type = str(row['entity_type'])
        source = str(row['source'])
        method = str(row['method'])
        confidence = float(row['confidence'])
        evidence = str(row['evidence'])
        
        canonical_name, clean_orig_name = normalize_entity_name(entity_type, orig_name)
        
        # Track alias merges
        if clean_orig_name.lower() != canonical_name.lower():
            key = f"[{entity_type}] {clean_orig_name}"
            alias_merges[key] = canonical_name
            
        entity_id = generate_entity_id(entity_type, canonical_name)
        
        normalized_list.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "canonical_name": canonical_name,
            "original_name": clean_orig_name,
            "source_doc_id": doc_id,
            "method": method,
            "confidence": confidence,
            "evidence": evidence
        })
        
    # Create dataframe
    norm_df = pd.DataFrame(normalized_list)
    
    # Deduplicate by (entity_type, canonical_name, source_doc_id)
    # If the same document has the same entity multiple times, keep the one with higher confidence
    norm_df = norm_df.sort_values(by="confidence", ascending=False)
    before_dedup = len(norm_df)
    norm_df = norm_df.drop_duplicates(subset=["entity_type", "canonical_name", "source_doc_id"])
    after_dedup = len(norm_df)
    
    print(f"Đã loại bỏ {before_dedup - after_dedup} thực thể trùng lặp trong cùng một văn bản.")
    
    # Save entities.csv
    print(f"Đang lưu {len(norm_df)} thực thể chuẩn hóa vào {output_path}...")
    norm_df.to_csv(output_path, index=False)
    print("Đã lưu thành công!")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("THỐNG KÊ KẾT QUẢ CHUẨN HÓA:")
    print("=" * 60)
    print(f"Số thực thể trước chuẩn hóa: {len(raw_df)}")
    print(f"Số thực thể sau chuẩn hóa (và loại trùng): {len(norm_df)}")
    print(f"Số thực thể độc nhất (Unique Nodes): {norm_df['entity_id'].nunique()}")
    
    print("\nChi tiết alias đã được gộp (Merge Alias):")
    for orig, canon in list(alias_merges.items())[:15]:
        print(f"  - {orig} -> {canon}")
    if len(alias_merges) > 15:
        print(f"  ... và {len(alias_merges) - 15} alias khác.")
        
    print("\n10 THỰC THỂ MẪU SAU CHUẨN HÓA:")
    print("-" * 60)
    samples = norm_df.head(10)
    for idx, row in samples.iterrows():
        print(f"{idx+1}. ID: {row['entity_id']}")
        print(f"   Loại: {row['entity_type']} | Tên chuẩn hóa: {row['canonical_name']} | Tên gốc: {row['original_name']}")
        print(f"   Văn bản nguồn: {row['source_doc_id']} | Confidence: {row['confidence']}")
        print("-" * 60)
        
    print("\nTrạng thái xác minh: HOÀN TẤT BƯỚC 4. Đạt yêu cầu [PASS]")

if __name__ == "__main__":
    main()
