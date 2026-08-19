import os
import pandas as pd
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 60)
    print("BƯỚC 6: VALIDATE RELATIONSHIP")
    print("=" * 60)
    
    raw_rels_path = os.path.join("ner_kb", "relationships_raw.csv")
    cleaned_docs_path = os.path.join("ner_kb", "cleaned_documents.csv")
    entities_path = os.path.join("ner_kb", "entities.csv")
    
    output_rels_path = os.path.join("ner_kb", "relationships.csv")
    output_report_path = os.path.join("ner_kb", "validation_report.csv")
    
    # Check input files
    for path in [raw_rels_path, cleaned_docs_path, entities_path]:
        if not os.path.exists(path):
            print(f"Lỗi: Không tìm thấy {path}. Vui lòng chạy các bước trước.")
            sys.exit(1)
            
    raw_df = pd.read_csv(raw_rels_path)
    docs_df = pd.read_csv(cleaned_docs_path)
    entities_df = pd.read_csv(entities_path)
    
    print(f"Đọc thành công:")
    print(f"  - {len(raw_df)} raw relationships")
    print(f"  - {len(docs_df)} cleaned documents")
    print(f"  - {len(entities_df)} normalized entities")
    
    # Build validation sets (normalize as string and strip)
    valid_doc_ids = set(docs_df['id'].astype(str).str.strip().tolist())
    valid_entity_ids = set(entities_df['entity_id'].astype(str).str.strip().tolist())
    
    valid_rel_types = {
        "THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI", 
        "BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"
    }
    
    doc_doc_types = {"THAM_CHIEU", "SUA_DOI_BO_SUNG", "THAY_THE_BOI"}
    doc_ent_types = {"BAN_HANH_BOI", "KY_BOI", "AP_DUNG_CHO", "THUOC_LINH_VUC"}
    
    validated_records = []
    seen_relationships = set()
    
    pass_count = 0
    fail_count = 0
    fail_reasons_stats = {}
    
    # Sort by confidence to keep the highest confidence in duplicate checks
    raw_df = raw_df.sort_values(by="confidence", ascending=False)
    
    for idx, row in raw_df.iterrows():
        source = str(row['source']).strip()
        target = str(row['target']).strip()
        rel_type = str(row['relationship_type']).strip()
        method = str(row['method']).strip()
        confidence = float(row['confidence'])
        evidence = str(row['evidence']).strip() if pd.notna(row['evidence']) else ""
        
        status = "PASS"
        reason = "Valid relationship"
        
        # 3. Validate relationship_type
        if rel_type not in valid_rel_types:
            status = "FAIL"
            reason = f"Invalid relationship type: {rel_type}"
            
        # 1. Validate source
        elif source not in valid_doc_ids:
            status = "FAIL"
            reason = f"Source document ID '{source}' not found in documents corpus"
            
        # 4. Kiểm tra self-loop
        elif source == target:
            status = "FAIL"
            reason = f"Self-loop detected: source and target are both '{source}'"
            
        # 2. Validate target
        else:
            if rel_type in doc_doc_types:
                if target not in valid_doc_ids:
                    status = "FAIL"
                    reason = f"Target document ID '{target}' not found in documents corpus"
            elif rel_type in doc_ent_types:
                if target not in valid_entity_ids:
                    status = "FAIL"
                    reason = f"Target entity ID '{target}' not found in entities list"
                    
        # 6. Kiểm tra missing/insufficient evidence (tối thiểu 5 ký tự)
        if status == "PASS" and (not evidence or len(evidence) < 5):
            status = "FAIL"
            reason = "Missing or insufficient evidence"
            
        # 5. Kiểm tra duplicate
        if status == "PASS":
            rel_key = (source, target, rel_type)
            if rel_key in seen_relationships:
                status = "FAIL"
                reason = "Duplicate relationship"
            else:
                seen_relationships.add(rel_key)
                
        # Count statistics
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1
            fail_reasons_stats[reason] = fail_reasons_stats.get(reason, 0) + 1
            
        validated_records.append({
            "source": source,
            "target": target,
            "relationship_type": rel_type,
            "method": method,
            "confidence": confidence,
            "evidence": evidence,
            "status": status,
            "reason": reason
        })
        
    # Convert to DataFrame
    report_df = pd.DataFrame(validated_records)
    
    # 10. Lưu toàn bộ báo cáo (validation_report.csv)
    report_df.to_csv(output_report_path, index=False)
    print(f"Đã lưu toàn bộ báo cáo thẩm định vào {output_report_path}")
    
    # 9. Lọc các relation đạt (PASS) lưu vào (relationships.csv)
    pass_df = report_df[report_df['status'] == "PASS"].drop(columns=['status', 'reason'])
    pass_df.to_csv(output_rels_path, index=False)
    print(f"Đã lưu {len(pass_df)} quan hệ hợp lệ vào {output_rels_path}")
    
    # 11. In thống kê
    print("\n" + "=" * 60)
    print("THỐNG KÊ KẾT QUẢ THẨM ĐỊNH:")
    print("=" * 60)
    print(f"Tổng số quan hệ đầu vào (raw): {len(raw_df)}")
    print(f"Số lượng ĐẠT (PASS): {pass_count}")
    print(f"Số lượng BỊ LOẠI (FAIL): {fail_count}")
    
    if pass_count > 0:
        print("\nSố lượng quan hệ PASS theo loại:")
        type_counts = pass_df['relationship_type'].value_counts()
        for rtype, count in type_counts.items():
            print(f"  - {rtype}: {count}")
            
    if fail_count > 0:
        print("\nCác nguyên nhân thất bại (FAIL) phổ biến:")
        sorted_reasons = sorted(fail_reasons_stats.items(), key=lambda x: x[1], reverse=True)
        for reason, count in sorted_reasons:
            print(f"  - {reason}: {count}")
            
    print("\n10 QUAN HỆ ĐẠT (PASS) MẪU:")
    print("-" * 60)
    samples = pass_df.head(10)
    for idx, row in samples.iterrows():
        print(f"{idx+1}. [{row['source']}] --[:{row['relationship_type']}]--> [{row['target']}]")
        print(f"   Confidence: {row['confidence']} | Method: {row['method']}")
        print(f"   Evidence: \"{row['evidence'][:150]}...\"")
        print("-" * 60)
        
    print("\nTrạng thái xác minh: HOÀN TẤT BƯỚC 6. Đạt yêu cầu [PASS]")

if __name__ == "__main__":
    main()
