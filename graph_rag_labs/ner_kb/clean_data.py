import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

def clean_html(html_str):
    if not isinstance(html_str, str):
        return ""
    soup = BeautifulSoup(html_str, "html.parser")
    # Get text with newline separator so block elements stay on separate lines
    text = soup.get_text(separator="\n")
    
    # Process line by line to normalize whitespace
    lines = []
    for line in text.splitlines():
        # Replace multiple spaces/tabs with a single space
        cleaned_line = re.sub(r'[ \t\r\f\v]+', ' ', line).strip()
        if cleaned_line:
            lines.append(cleaned_line)
            
    return "\n".join(lines)

def main():
    print("=" * 60)
    print("BƯỚC 1: KIỂM TRA DỮ LIỆU VÀ LÀM SẠCH HTML")
    print("=" * 60)
    
    metadata_path = os.path.join("ner_kb", "metadata.csv")
    content_path = os.path.join("ner_kb", "content.csv")
    output_path = os.path.join("ner_kb", "cleaned_documents.csv")
    
    # 1. Đọc dữ liệu bằng pandas
    print("Đang đọc dữ liệu đầu vào...")
    meta_df = pd.read_csv(metadata_path)
    content_df = pd.read_csv(content_path)
    
    # 2. Kiểm tra số dòng, số cột
    print(f"Metadata file: {meta_df.shape[0]} dòng, {meta_df.shape[1]} cột")
    print(f"Content file: {content_df.shape[0]} dòng, {content_df.shape[1]} cột")
    
    # 3. Kiểm tra duplicate id
    meta_dupes = meta_df['id'].duplicated().sum()
    content_dupes = content_df['id'].duplicated().sum()
    print(f"Số duplicate ID trong metadata: {meta_dupes}")
    print(f"Số duplicate ID trong content: {content_dupes}")
    
    # 4. Kiểm tra ID mismatch
    meta_ids = set(meta_df['id'])
    content_ids = set(content_df['id'])
    
    only_in_meta = meta_ids - content_ids
    only_in_content = content_ids - meta_ids
    
    print(f"Số ID chỉ có trong metadata (mismatch): {len(only_in_meta)}")
    if only_in_meta:
        print(f"  Các ID mismatch trong metadata: {only_in_meta}")
        
    print(f"Số ID chỉ có trong content (mismatch): {len(only_in_content)}")
    if only_in_content:
        print(f"  Các ID mismatch trong content: {only_in_content}")
        
    # 5. Merge theo id
    print("Đang thực hiện merge dữ liệu theo 'id'...")
    # Sử dụng inner join để đảm bảo các văn bản có đủ cả metadata và content
    merged_df = pd.merge(meta_df, content_df, on='id', how='inner')
    print(f"Số lượng văn bản sau khi merge (inner join): {len(merged_df)}")
    
    # 6. Thống kê missing values cho các cột trong metadata
    print("\nThống kê missing values trong các cột metadata:")
    missing_stats = merged_df.drop(columns=['content_html']).isnull().sum()
    for col, count in missing_stats.items():
        if count > 0:
            print(f"  - Cột '{col}': {count} giá trị thiếu (NaN)")
            
    # 7. Phát hiện các giá trị chưa chuẩn như rỗng hoặc "Chưa phân loại"
    print("\nKiểm tra các giá trị chưa chuẩn trong metadata:")
    for col in merged_df.columns:
        if col == 'content_html':
            continue
        
        # Tìm các chuỗi rỗng sau khi strip hoặc "Chưa phân loại"
        empty_str_count = 0
        chua_phan_loai_count = 0
        
        for val in merged_df[col]:
            if isinstance(val, str):
                stripped = val.strip()
                if stripped == "":
                    empty_str_count += 1
                if stripped.lower() == "chưa phân loại":
                    chua_phan_loai_count += 1
                    
        if empty_str_count > 0 or chua_phan_loai_count > 0:
            print(f"  - Cột '{col}':")
            if empty_str_count > 0:
                print(f"    * Số chuỗi rỗng: {empty_str_count}")
            if chua_phan_loai_count > 0:
                print(f"    * Số giá trị 'Chưa phân loại': {chua_phan_loai_count}")

    # 8. Làm sạch content_html bằng BeautifulSoup
    print("\nĐang tiến hành làm sạch content_html...")
    merged_df['content_clean'] = merged_df['content_html'].apply(clean_html)
    
    # 9. Kiểm tra xem nội dung đã sạch chưa và cột content_clean không rỗng bất thường
    empty_clean_count = (merged_df['content_clean'] == "").sum()
    print(f"Số lượng content_clean bị rỗng sau khi làm sạch: {empty_clean_count}")
    
    # 10. Lưu kết quả
    print(f"Đang lưu kết quả ra file {output_path}...")
    merged_df.to_csv(output_path, index=False)
    print("Đã lưu thành công!")
    
    # 11. In mẫu so sánh 2 văn bản đầu tiên
    print("\n" + "=" * 60)
    print("MẪU SO SÁNH NỘI DUNG HTML VÀ SAU KHI LÀM SẠCH (2 VĂN BẢN ĐẦU TIÊN):")
    print("=" * 60)
    
    samples = merged_df.head(2)
    for idx, row in samples.iterrows():
        print(f"\n--- Mẫu {idx+1} (ID: {row['id']}, Tiêu đề: {row['title']}) ---")
        
        # Lấy 300 ký tự đầu của HTML
        html_sample = str(row['content_html'])[:300].replace('\n', ' ')
        print(f"** [CONTENT_HTML - 300 ký tự đầu] **:\n{html_sample}...")
        
        # Lấy 300 ký tự đầu của Cleaned Text
        clean_sample = str(row['content_clean'])[:300].replace('\n', ' [NEWLINE] ')
        print(f"\n** [CONTENT_CLEAN - 300 ký tự đầu] **:\n{clean_sample}...")
        print("-" * 60)

    # In báo cáo kết quả cuối cùng theo định dạng yêu cầu để kiểm tra
    print("\n" + "=" * 60)
    print("KẾT QUẢ XÁC MINH BƯỚC 1:")
    print("=" * 60)
    print(f"Số lượng tài liệu gốc: {len(meta_df)}")
    print(f"Số lượng tài liệu sau khi làm sạch: {len(merged_df)}")
    print(f"File {output_path} tồn tại: {'ĐẠT' if os.path.exists(output_path) else 'KHÔNG ĐẠT'}")
    print("Trạng thái: HOÀN TẤT BƯỚC 1.")

if __name__ == "__main__":
    main()
