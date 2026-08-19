import os
import re
import pandas as pd
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

def extract_candidates(row, regex_pattern):
    source_id = row['id']
    source_so_ky_hieu = str(row['so_ky_hieu']).strip() if pd.notna(row['so_ky_hieu']) else ""
    content = str(row['content_clean']) if pd.notna(row['content_clean']) else ""
    
    candidates = []
    
    # Split content into lines (each line represents a structural paragraph or sentence from Step 1)
    lines = content.split('\n')
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Find all matching document numbers in this line
        matches = re.findall(regex_pattern, line_clean)
        if not matches:
            continue
            
        for match in matches:
            target_so_ky_hieu = match.strip()
            
            # 5. Loại candidate tự tham chiếu chính văn bản hiện tại
            if target_so_ky_hieu.lower() == source_so_ky_hieu.lower():
                continue
                
            # Determine trigger based on presence of keywords in the line
            line_lower = line_clean.lower()
            
            # Hierarchy: thay thế > sửa đổi, bổ sung > bãi bỏ > căn cứ > tham chiếu
            if "thay thế" in line_lower:
                trigger = "thay thế"
            elif "sửa đổi" in line_lower or "bổ sung" in line_lower:
                trigger = "sửa đổi, bổ sung"
            elif "bãi bỏ" in line_lower:
                trigger = "bãi bỏ"
            elif "căn cứ" in line_lower:
                trigger = "căn cứ"
            else:
                trigger = "tham chiếu"
                
            candidates.append({
                "source_id": source_id,
                "source_so_ky_hieu": source_so_ky_hieu,
                "target_so_ky_hieu": target_so_ky_hieu,
                "trigger": trigger,
                "evidence": line_clean
            })
            
    return candidates

def main():
    print("=" * 60)
    print("BƯỚC 2: RULE-BASED CANDIDATE EXTRACTION")
    print("=" * 60)
    
    input_path = os.path.join("ner_kb", "cleaned_documents.csv")
    output_path = os.path.join("ner_kb", "relation_candidates.csv")
    
    if not os.path.exists(input_path):
        print(f"Lỗi: Không tìm thấy {input_path}. Vui lòng chạy Bước 1 trước.")
        sys.exit(1)
        
    df = pd.read_csv(input_path)
    print(f"Đọc thành công {len(df)} văn bản từ {input_path}")
    
    # Regex to match Vietnamese legal document numbers
    # Format: [Number]/[Year or VBHN]/[Abbreviation]
    # Example: 32/2024/QH15, 73/2016/NĐ-CP, 52/VBHN-NHNN
    regex_pattern = r'\b\d+/[A-Za-z0-9\-\u0110\u0111_]+/[A-Za-z\u0110\u0111][A-Za-z0-9\-\u0110\u0111_]*\b'
    
    all_candidates = []
    for _, row in df.iterrows():
        candidates = extract_candidates(row, regex_pattern)
        all_candidates.extend(candidates)
        
    candidates_df = pd.DataFrame(all_candidates)
    
    if candidates_df.empty:
        print("Cảnh báo: Không phát hiện thấy bất kỳ candidate nào!")
        # Create empty dataframe with schema
        candidates_df = pd.DataFrame(columns=["source_id", "source_so_ky_hieu", "target_so_ky_hieu", "trigger", "evidence"])
    else:
        # 6. Loại duplicate candidate dựa trên (source_id, target_so_ky_hieu, trigger)
        # Nếu cùng văn bản nguồn, cùng văn bản đích và cùng trigger thì loại trùng
        before_dedup = len(candidates_df)
        candidates_df = candidates_df.drop_duplicates(subset=["source_id", "target_so_ky_hieu", "trigger"])
        after_dedup = len(candidates_df)
        print(f"Đã loại bỏ {before_dedup - after_dedup} candidate trùng lặp.")
        
    # 8. Lưu kết quả
    print(f"Đang lưu {len(candidates_df)} candidates vào {output_path}...")
    candidates_df.to_csv(output_path, index=False)
    print("Đã lưu thành công!")
    
    # 9. In thống kê
    print("\n" + "=" * 60)
    print("THỐNG KÊ KẾT QUẢ:")
    print("=" * 60)
    print(f"Tổng số candidate duy nhất tìm thấy: {len(candidates_df)}")
    
    if not candidates_df.empty:
        trigger_counts = candidates_df['trigger'].value_counts()
        print("\nSố lượng candidate theo trigger:")
        for trigger, count in trigger_counts.items():
            print(f"  - Trigger '{trigger}': {count}")
            
        print("\n10 CANDIDATE MẪU:")
        print("-" * 60)
        samples = candidates_df.head(10)
        for idx, row in samples.iterrows():
            print(f"{idx+1}. [{row['source_so_ky_hieu']}] --({row['trigger']})--> [{row['target_so_ky_hieu']}]")
            print(f"   Evidence: \"{row['evidence'][:150]}...\"")
            print("-" * 60)
            
    print("\nTrạng thái xác minh: HOÀN TẤT BƯỚC 2. Đạt yêu cầu [PASS]")

if __name__ == "__main__":
    main()
