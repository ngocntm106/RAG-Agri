import os
import sys
import pandas as pd

# Reconfigure output to utf-8 for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

def detect_encoding(file_path):
    try:
        import charset_normalizer
        with open(file_path, 'rb') as f:
            data = f.read(1024 * 1024)  # read 1MB for encoding detection
            result = charset_normalizer.detect(data)
            return result['encoding']
    except ImportError:
        # Fallback if charset-normalizer is not installed
        for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    f.read(1024)
                return enc
            except UnicodeDecodeError:
                continue
        return 'unknown'

def check_file_structure():
    print("=== PROJECT STRUCTURE ===")
    files_found = []
    dangerous_keywords = ["os.remove", "shutil.rmtree", "open(", '"w"', "'w'", "DELETE", "DROP", "DETACH DELETE"]
    dangerous_matches = []
    
    for root, dirs, files in os.walk('.'):
        # Exclude virtual environment
        if '.venv' in root.split(os.sep) or '.git' in root.split(os.sep):
            continue
            
        for file in files:
            path = os.path.join(root, file)
            ext = os.path.splitext(file)[1]
            if ext in ['.py', '.md', '.csv', '.json', '.txt', '.env'] or file == 'requirements.txt' or file.startswith('.env'):
                files_found.append(path)
                # Check for dangerous patterns
                if ext in ['.py', '.sh', '.ipynb'] and file != 'inspect_project.py':
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            for i, line in enumerate(f, 1):
                                for kw in dangerous_keywords:
                                    if kw in line:
                                        dangerous_matches.append((path, i, kw, line.strip()))
                    except Exception as e:
                        pass
                        
    print(f"Found files: {files_found}")
    return files_found, dangerous_matches

def analyze_csv(file_name, file_path):
    print(f"\n=== ANALYZING: {file_name} ===")
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return None
        
    encoding = detect_encoding(file_path)
    print(f"Detected encoding: {encoding}")
    
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        print(f"Error reading CSV with detected encoding: {e}")
        # Try utf-8-sig or latin-1
        for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                encoding = enc
                print(f"Read successful with: {enc}")
                break
            except Exception:
                pass
        else:
            raise e

    num_rows = len(df)
    columns = list(df.columns)
    null_counts = df.isnull().sum().to_dict()
    duplicate_count = df.duplicated().sum()
    
    print(f"Number of rows: {num_rows}")
    print(f"Columns: {columns}")
    print(f"Null counts: {null_counts}")
    print(f"Duplicate rows: {duplicate_count}")
    
    samples = df.head(3).copy()
    if 'content_html' in samples.columns:
        samples['content_html'] = samples['content_html'].apply(lambda x: str(x)[:300] + "..." if len(str(x)) > 300 else str(x))
        
    return {
        "file_name": file_name,
        "file_path": file_path,
        "num_rows": num_rows,
        "columns": columns,
        "encoding": encoding,
        "null_counts": null_counts,
        "duplicate_count": duplicate_count,
        "head_samples": samples.to_dict(orient='records')
    }

def main():
    print(f"Python interpreter: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Pandas version: {pd.__version__}")
    
    files_found, dangerous_matches = check_file_structure()
    
    # Path to source CSV files
    # The current directory is buoi_14, so source data is in ../kb+hops/
    kb_path = os.path.join("..", "kb+hops")
    
    csv_files = {
        "metadata.csv": os.path.join(kb_path, "metadata.csv"),
        "content.csv": os.path.join(kb_path, "content.csv"),
        "relationships.csv": os.path.join(kb_path, "relationships.csv")
    }
    
    results = {}
    for name, path in csv_files.items():
        results[name] = analyze_csv(name, path)
        
    # Write report
    report_dir = "outputs"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "inspection_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO KIỂM TRA PROJECT VÀ DỮ LIỆU (INSPECTION REPORT)\n\n")
        
        f.write("## 1. Môi trường hệ thống\n")
        f.write(f"- **Working Root**: {os.path.abspath('.')}\n")
        f.write(f"- **Python Interpreter**: `{sys.executable}`\n")
        f.write(f"- **Python Version**: `{sys.version}`\n")
        f.write(f"- **Pandas Version**: `{pd.__version__}`\n\n")
        
        f.write("## 2. Cấu trúc thư mục hiện tại (buoi_14/)\n")
        f.write("Các file đã quét được:\n")
        for file in files_found:
            f.write(f"- `{file}`\n")
        f.write("\n")
        
        f.write("## 3. Phân tích Dữ liệu Nguồn (kb+hops/)\n")
        for name, res in results.items():
            if res is None:
                f.write(f"### {name}: KHÔNG TÌM THẤY FILE\n\n")
                continue
            f.write(f"### File: `{name}`\n")
            f.write(f"- **Đường dẫn**: `{res['file_path']}`\n")
            f.write(f"- **Số dòng**: {res['num_rows']}\n")
            f.write(f"- **Bảng mã (Encoding)**: `{res['encoding']}`\n")
            f.write(f"- **Các cột**: `{', '.join(res['columns'])}`\n")
            f.write(f"- **Số dòng trùng lặp**: {res['duplicate_count']}\n")
            f.write("- **Giá trị Null**:\n")
            for col, val in res['null_counts'].items():
                f.write(f"  - `{col}`: {val} dòng null\n")
            
            # Identify keys and fields based on dataset
            if name == "metadata.csv":
                f.write("- **Khóa đề xuất (Candidate Key)**: `document_id` (mã định danh văn bản)\n")
                f.write("- **Trường Metadata phù hợp Citation**: `title`, `document_type`, `effective_date`, `status`\n")
            elif name == "content.csv":
                f.write("- **Khóa đề xuất (Candidate Key)**: `chunk_id` (định danh duy nhất cho từng chunk)\n")
                f.write("- **Trường Text phù hợp Retrieval**: `text` (nội dung chi tiết của điều khoản)\n")
                f.write("- **Trường Metadata phù hợp Citation**: `document_id`, `chapter`, `section`, `article`, `clause`\n")
            elif name == "relationships.csv":
                f.write("- **Khóa liên kết**: `source_id`, `target_id`\n")
                f.write("- **Loại quan hệ (Relationship Types)**: Xem mẫu dữ liệu để trích xuất thêm.\n")
                
            f.write("\n- **Mẫu dữ liệu (3 dòng đầu)**:\n")
            f.write("```json\n")
            import json
            f.write(json.dumps(res['head_samples'], indent=2, ensure_ascii=False))
            f.write("\n```\n\n")
            
        f.write("## 4. Kiểm tra rủi ro mã nguồn cũ (Kiểm tra lệnh phá hủy/ghi đè dữ liệu)\n")
        if dangerous_matches:
            f.write("CẢNH BÁO: Phát hiện các dòng lệnh chứa từ khóa nhạy cảm:\n")
            for path, line_no, kw, content in dangerous_matches:
                f.write(f"- File `{path}` (Dòng {line_no}) [{kw}]: `{content}`\n")
        else:
            f.write("Không phát hiện lệnh nguy hại nào (`os.remove`, `shutil.rmtree`, `DELETE`, `DROP`...) trong code hiện có.\n")
            
    print(f"Report written successfully to {report_path}")

if __name__ == "__main__":
    main()
