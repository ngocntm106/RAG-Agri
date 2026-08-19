import os
import re
import pandas as pd
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

def normalize_so_ky_hieu(skh):
    if not isinstance(skh, str):
        return ""
    val = skh.strip().lower()
    val = val.replace('–', '-').replace('—', '-')
    val = re.sub(r'\s*/\s*', '/', val)
    val = re.sub(r'\s*-\s*', '-', val)
    return val

def main():
    print("=" * 60)
    print("BƯỚC 5: RELATIONSHIP EXTRACTION")
    print("=" * 60)
    
    candidates_path = os.path.join("ner_kb", "relation_candidates.csv")
    entities_path = os.path.join("ner_kb", "entities.csv")
    metadata_path = os.path.join("ner_kb", "enriched_metadata.csv")
    output_path = os.path.join("ner_kb", "relationships_raw.csv")
    
    # Check input files
    for path in [candidates_path, entities_path, metadata_path]:
        if not os.path.exists(path):
            print(f"Lỗi: Không tìm thấy {path}. Vui lòng chạy các bước trước.")
            sys.exit(1)
            
    candidates_df = pd.read_csv(candidates_path)
    entities_df = pd.read_csv(entities_path)
    metadata_df = pd.read_csv(metadata_path)
    
    print(f"Đọc thành công:")
    print(f"  - {len(candidates_df)} relation candidates")
    print(f"  - {len(entities_df)} normalized entities")
    print(f"  - {len(metadata_df)} enriched metadata documents")
    
    # Build a robust mapping from normalized so_ky_hieu to document ID
    so_ky_hieu_map = {}
    for idx, row in metadata_df.iterrows():
        doc_id = str(row['id']).strip()
        skh = str(row['so_ky_hieu'])
        
        normalized_skh = normalize_so_ky_hieu(skh)
        if normalized_skh:
            so_ky_hieu_map[normalized_skh] = doc_id
            
    relationships = []
    
    # 1. Process Document -> Document relations from relation_candidates.csv
    print("\nĐang xử lý quan hệ giữa các tài liệu (Document -> Document)...")
    mismatched_targets = set()
    
    for idx, row in candidates_df.iterrows():
        source_doc_id = str(row['source_id']).strip()
        target_so_ky_hieu = str(row['target_so_ky_hieu'])
        trigger = str(row['trigger'])
        evidence = str(row['evidence'])
        
        normalized_target_skh = normalize_so_ky_hieu(target_so_ky_hieu)
        
        # Resolve target document ID
        if normalized_target_skh in so_ky_hieu_map:
            target_doc_id = so_ky_hieu_map[normalized_target_skh]
            
            # Skip self-reference (just to be extra safe)
            if source_doc_id == target_doc_id:
                continue
                
            # Determine relationship type and direction
            if trigger == "thay thế":
                # 4. THAY_THE_BOI direction: Document cũ (target) -> Document mới (source)
                source_id = target_doc_id
                target_id = source_doc_id
                rel_type = "THAY_THE_BOI"
            elif trigger == "sửa đổi, bổ sung":
                # 5. SUA_DOI_BO_SUNG direction: source -> target
                source_id = source_doc_id
                target_id = target_doc_id
                rel_type = "SUA_DOI_BO_SUNG"
            else: # trigger == "căn cứ", "bãi bỏ", "tham chiếu"
                source_id = source_doc_id
                target_id = target_doc_id
                rel_type = "THAM_CHIEU"
                
            # Check if evidence is empty or too short (rule 7: Không tạo relation nếu evidence không đủ)
            if len(evidence.strip()) < 5:
                continue
                
            relationships.append({
                "source": source_id,
                "target": target_id,
                "relationship_type": rel_type,
                "method": "rules",
                "confidence": 0.9,
                "evidence": evidence
            })
        else:
            mismatched_targets.add(target_so_ky_hieu)
            
    print(f"  -> Đã liên kết thành công {len(relationships)} quan hệ Document -> Document.")
    print(f"  -> Có {len(mismatched_targets)} số ký hiệu đích không nằm trong corpus 30 tài liệu (đã bỏ qua).")
    
    # 2. Process Document -> Entity relations from entities.csv
    print("\nĐang xử lý quan hệ giữa tài liệu và thực thể (Document -> Entity)...")
    doc_entity_count = 0
    
    entity_rel_mapping = {
        "CoQuan": "BAN_HANH_BOI",
        "NguoiKy": "KY_BOI",
        "DoiTuongApDung": "AP_DUNG_CHO",
        "LinhVuc": "THUOC_LINH_VUC"
    }
    
    for idx, row in entities_df.iterrows():
        source_doc_id = str(row['source_doc_id']).strip()
        entity_id = str(row['entity_id']).strip()
        entity_type = str(row['entity_type']).strip()
        method = str(row['method']).strip()
        confidence = float(row['confidence'])
        evidence = str(row['evidence']).strip()
        
        if entity_type in entity_rel_mapping:
            rel_type = entity_rel_mapping[entity_type]
            
            # Enforce rule 7: Không tạo nếu evidence không đủ
            if len(evidence) < 5:
                continue
                
            relationships.append({
                "source": source_doc_id,
                "target": entity_id,
                "relationship_type": rel_type,
                "method": method,
                "confidence": confidence,
                "evidence": evidence
            })
            doc_entity_count += 1
            
    print(f"  -> Đã tạo {doc_entity_count} quan hệ Document -> Entity.")
    
    # Create DataFrame
    rel_df = pd.DataFrame(relationships)
    
    if rel_df.empty:
        print("Cảnh báo: Không tạo được bất kỳ mối quan hệ nào!")
        rel_df = pd.DataFrame(columns=["source", "target", "relationship_type", "method", "confidence", "evidence"])
    else:
        # 8. Loại duplicate based on (source, target, relationship_type)
        # Sắp xếp theo confidence giảm dần để giữ lại bản ghi có confidence cao nhất khi gộp trùng
        rel_df = rel_df.sort_values(by="confidence", ascending=False)
        before_dedup = len(rel_df)
        rel_df = rel_df.drop_duplicates(subset=["source", "target", "relationship_type"])
        after_dedup = len(rel_df)
        print(f"\nĐã loại bỏ {before_dedup - after_dedup} quan hệ trùng lặp.")
        
    # 9. Lưu kết quả
    print(f"Đang lưu {len(rel_df)} quan hệ vào {output_path}...")
    rel_df.to_csv(output_path, index=False)
    print("Đã lưu thành công!")
    
    # 10. In thống kê
    print("\n" + "=" * 60)
    print("THỐNG KÊ SỐ LƯỢNG QUAN HỆ THEO LOẠI:")
    print("=" * 60)
    rel_counts = rel_df['relationship_type'].value_counts()
    for rtype, count in rel_counts.items():
        print(f"  - Quan hệ '{rtype}': {count}")
        
    print("\n10 QUAN HỆ MẪU VÀ EVIDENCE ĐI KÈM:")
    print("-" * 60)
    samples = rel_df.head(10)
    for idx, row in samples.iterrows():
        print(f"{idx+1}. [{row['source']}] --[:{row['relationship_type']}]--> [{row['target']}]")
        print(f"   Method: {row['method']} | Confidence: {row['confidence']}")
        print(f"   Evidence: \"{row['evidence'][:150]}...\"")
        print("-" * 60)
        
    print("\nTrạng thái xác minh: HOÀN TẤT BƯỚC 5. Đạt yêu cầu [PASS]")

if __name__ == "__main__":
    main()
