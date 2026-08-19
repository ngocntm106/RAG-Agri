import os
import sys
import argparse
import pandas as pd

# Reconfigure stdout to UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever

def print_results(results: list[dict], title: str):
    print(f"\n==================== {title} ====================")
    if not results:
        print("Không tìm thấy kết quả phù hợp.")
        return
        
    for r in results:
        print(f"[{r['rank']}] Score: {r['retrieval_score']} | {r['citation']}")
        print(f"    Chunk ID: {r['chunk_id']} (Doc ID: {r['document_id']})")
        print(f"    Text: {r['text'][:180]}...\n")

def run_evaluation_examples(bm25: BM25Retriever, dense: DenseRetriever, top_k: int = 5):
    """
    Chạy 3 loại câu hỏi và ghi báo cáo ra outputs/retrieval_examples.md
    """
    queries = [
        {
            "type": "1. Exact Keyword (Số hiệu / Điều khoản cụ thể)",
            "query": "Thông tư số 01/2014/TT-NHNN Điều 4 quy định đóng gói niêm phong tiền mặt"
        },
        {
            "type": "2. Semantic (Diễn đạt ngữ nghĩa, không dùng đúng từ khóa)",
            "query": "Ai có quyền phê duyệt quản lý dự trữ ngoại hối nhà nước và trách nhiệm của Thống đốc?"
        },
        {
            "type": "3. Mixed (Kết hợp từ khóa văn bản và ngữ nghĩa nghiệp vụ)",
            "query": "Điều kiện cấp Giấy phép thành lập doanh nghiệp bảo hiểm theo Nghị định 73/2016/NĐ-CP"
        }
    ]
    
    os.makedirs("outputs", exist_ok=True)
    report_path = os.path.join("outputs", "retrieval_examples.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO KẾT QUẢ RETRIEVAL BASELINE (BM25 vs DENSE)\n\n")
        f.write("Báo cáo này so sánh kết quả truy vấn độc lập giữa **BM25 (Lexical Search)** và **Dense Retrieval (Embedding Search)** trên 3 loại câu hỏi đại diện.\n\n")
        
        for q_info in queries:
            q_type = q_info["type"]
            query = q_info["query"]
            
            bm25_res = bm25.search(query, top_k=top_k)
            dense_res = dense.search(query, top_k=top_k)
            
            f.write(f"## {q_type}\n")
            f.write(f"**Câu hỏi truy vấn**: `{query}`\n\n")
            
            f.write("### BM25 RESULTS\n")
            f.write("| Rank | Score | Citation | Chunk ID | Snippet |\n")
            f.write("|---|---|---|---|---|\n")
            for r in bm25_res:
                snippet = r['text'].replace("\n", " ")[:120].replace("|", "\\|")
                f.write(f"| {r['rank']} | {r['retrieval_score']} | `{r['citation']}` | `{r['chunk_id']}` | {snippet}... |\n")
            f.write("\n")
            
            f.write("### DENSE RESULTS\n")
            f.write("| Rank | Score | Citation | Chunk ID | Snippet |\n")
            f.write("|---|---|---|---|---|\n")
            for r in dense_res:
                snippet = r['text'].replace("\n", " ")[:120].replace("|", "\\|")
                f.write(f"| {r['rank']} | {r['retrieval_score']} | `{r['citation']}` | `{r['chunk_id']}` | {snippet}... |\n")
            f.write("\n---\n\n")
            
    print(f"\n[Báo cáo mẫu] Đã lưu kết quả thực nghiệm ra: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Chạy baseline retrieval: BM25-only và Dense-only")
    parser.add_argument("--query", type=str, default=None, help="Câu hỏi cần tìm kiếm")
    parser.add_argument("--top-k", type=int, default=5, help="Số lượng kết quả trả về cho mỗi retriever")
    parser.add_argument("--eval-examples", action="store_true", help="Chạy và xuất báo cáo 3 câu hỏi mẫu ra outputs/retrieval_examples.md")
    args = parser.parse_args()
    
    corpus_path = os.path.join("data", "processed", "chunks_normalized.csv")
    if not os.path.exists(corpus_path):
        print(f"Error: Không tìm thấy corpus tại {corpus_path}. Hãy chạy `scripts/prepare_corpus.py` trước!")
        sys.exit(1)
        
    print(f"Đang nạp corpus từ {corpus_path}...")
    df_chunks = pd.read_csv(corpus_path, encoding='utf-8')
    print(f"Đã nạp {len(df_chunks)} chunks.")
    
    # Khởi tạo hai retriever
    print("\nKhởi tạo BM25 Retriever...")
    bm25 = BM25Retriever(df_chunks)
    
    print("\nKhởi tạo Dense Retriever...")
    dense = DenseRetriever(df_chunks)
    
    if args.query:
        print(f"\n=== ĐANG THỰC HIỆN TRUY VẤN: '{args.query}' ===")
        bm25_res = bm25.search(args.query, top_k=args.top_k)
        print_results(bm25_res, "BM25 RESULTS")
        
        dense_res = dense.search(args.query, top_k=args.top_k)
        print_results(dense_res, "DENSE RESULTS")
        
    if args.eval_examples or not args.query:
        run_evaluation_examples(bm25, dense, top_k=args.top_k)

if __name__ == "__main__":
    main()
