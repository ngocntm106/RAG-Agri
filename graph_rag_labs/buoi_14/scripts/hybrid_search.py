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
from src.hybrid_retriever import HybridRetriever

def print_hybrid_table(results: list[dict]):
    print("\n" + "="*80)
    print("HYBRID RESULTS")
    print("="*80)
    if not results:
        print("Không có kết quả phù hợp.")
        return
        
    header = f"{'Rank':<5} | {'Chunk ID':<38} | {'BM25':<6} | {'Dense':<6} | {'RRF Score':<10} | {'Citation'}"
    print(header)
    print("-" * 110)
    for r in results:
        bm25_r = str(r['bm25_rank'])
        dense_r = str(r['dense_rank'])
        print(f"{r['final_rank']:<5} | {r['chunk_id']:<38} | {bm25_r:<6} | {dense_r:<6} | {r['rrf_score']:<10.6f} | {r['citation']}")
        snippet = r['text'].replace('\n', ' ')[:100]
        print(f"      Text: {snippet}...\n")

def run_hybrid_evaluation_examples(
    bm25: BM25Retriever, 
    dense: DenseRetriever, 
    hybrid: HybridRetriever, 
    top_k: int = 5, 
    candidate_k: int = 20
):
    """
    So sánh BM25, Dense, và Hybrid trên 3 loại câu hỏi và ghi nhận vào outputs/retrieval_examples.md
    """
    queries = [
        {
            "category": "1. Exact Keyword (Số hiệu / Điều khoản cụ thể)",
            "query": "Thông tư số 01/2014/TT-NHNN Điều 4 quy định đóng gói niêm phong tiền mặt",
            "analysis_hybrid": "Hybrid kết hợp được tính chính xác tuyệt đối của BM25 (tìm đúng Điều 4, 5, 6 của TT 01/2014) với độ tương đồng ngữ cảnh của Dense, giúp đưa các điều khoản cốt lõi về đóng gói lên các vị trí đầu bảng mà không bị phân tán."
        },
        {
            "category": "2. Semantic (Diễn đạt ngữ nghĩa, không dùng đúng từ khóa)",
            "query": "Ai có quyền phê duyệt quản lý dự trữ ngoại hối nhà nước và trách nhiệm của Thống đốc?",
            "analysis_hybrid": "BM25 bị loãng do câu hỏi chứa nhiều từ khóa chung chung ('trách nhiệm', 'phê duyệt'), trong khi Dense xác định đúng các quy định về 'Trách nhiệm vận chuyển ngoại tệ & thanh tra giám sát của Thống đốc'. Hybrid tận dụng điểm số cao của Dense để nâng các chunk có liên quan thực sự lên top 1-2."
        },
        {
            "category": "3. Mixed (Kết hợp từ khóa văn bản và ngữ nghĩa nghiệp vụ)",
            "query": "Điều kiện cấp Giấy phép thành lập doanh nghiệp bảo hiểm theo Nghị định 73/2016/NĐ-CP",
            "analysis_hybrid": "Đây là kịch bản Hybrid phát huy hiệu quả cao nhất: BM25 neo giữ chính xác văn bản mục tiêu 'Nghị định 73/2016/NĐ-CP', trong khi Dense giúp xếp hạng các điều kiện cụ thể (Điều 6, Điều 14) lên hàng đầu, loại bỏ các chunk râu ria."
        }
    ]

    os.makedirs("outputs", exist_ok=True)
    report_path = os.path.join("outputs", "retrieval_examples.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO SO SÁNH RETRIEVAL: BM25 vs DENSE vs HYBRID (RRF)\n\n")
        f.write("Báo cáo này đối chiếu chi tiết hiệu quả tìm kiếm giữa **BM25**, **Dense Retrieval**, và **Hybrid Search (Reciprocal Rank Fusion)** trên cùng tập corpus chuẩn hóa.\n\n")

        for q_item in queries:
            cat = q_item["category"]
            query = q_item["query"]
            analysis = q_item["analysis_hybrid"]

            bm25_res = bm25.search(query, top_k=top_k)
            dense_res = dense.search(query, top_k=top_k)
            hybrid_res = hybrid.search(query, top_k=top_k, candidate_k=candidate_k)

            f.write(f"## {cat}\n")
            f.write(f"**Câu hỏi**: `{query}`\n\n")

            f.write("### 1. BM25 RESULTS\n")
            f.write("| Rank | Score | Citation | Chunk ID | Snippet |\n")
            f.write("|---|---|---|---|---|\n")
            for r in bm25_res:
                snip = r['text'].replace('\n', ' ')[:100].replace('|', '\\|')
                f.write(f"| {r['rank']} | {r['retrieval_score']} | `{r['citation']}` | `{r['chunk_id']}` | {snip}... |\n")
            f.write("\n")

            f.write("### 2. DENSE RESULTS\n")
            f.write("| Rank | Score | Citation | Chunk ID | Snippet |\n")
            f.write("|---|---|---|---|---|\n")
            for r in dense_res:
                snip = r['text'].replace('\n', ' ')[:100].replace('|', '\\|')
                f.write(f"| {r['rank']} | {r['retrieval_score']} | `{r['citation']}` | `{r['chunk_id']}` | {snip}... |\n")
            f.write("\n")

            f.write("### 3. HYBRID RESULTS (RRF)\n")
            f.write("| Rank | BM25 Rank | Dense Rank | RRF Score | Citation | Chunk ID | Snippet |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for r in hybrid_res:
                snip = r['text'].replace('\n', ' ')[:100].replace('|', '\\|')
                f.write(f"| {r['final_rank']} | {r['bm25_rank']} | {r['dense_rank']} | {r['rrf_score']} | `{r['citation']}` | `{r['chunk_id']}` | {snip}... |\n")
            f.write("\n")

            f.write(f"**Đánh giá cải thiện**: {analysis}\n\n")
            f.write("---\n\n")

    print(f"\n[Báo cáo mẫu] Đã lưu báo cáo so sánh chi tiết ra: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Chạy Hybrid Search (BM25 + Dense kết hợp RRF)")
    parser.add_argument("--query", type=str, default=None, help="Câu hỏi cần tìm kiếm")
    parser.add_argument("--candidate-k", type=int, default=20, help="Số lượng candidates từ mỗi retriever trước khi fusion")
    parser.add_argument("--top-k", type=int, default=5, help="Số lượng kết quả cuối cùng")
    parser.add_argument("--eval-examples", action="store_true", help="Chạy và xuất báo cáo so sánh 3 câu hỏi mẫu ra outputs/retrieval_examples.md")
    args = parser.parse_args()

    corpus_path = os.path.join("data", "processed", "chunks_normalized.csv")
    if not os.path.exists(corpus_path):
        print(f"Error: Không tìm thấy corpus tại {corpus_path}. Hãy chạy `scripts/prepare_corpus.py` trước!")
        sys.exit(1)

    print(f"Đang nạp corpus từ {corpus_path}...")
    df_chunks = pd.read_csv(corpus_path, encoding='utf-8')
    print(f"Đã nạp {len(df_chunks)} chunks.")

    print("\nKhởi tạo BM25 Retriever...")
    bm25 = BM25Retriever(df_chunks)

    print("\nKhởi tạo Dense Retriever...")
    dense = DenseRetriever(df_chunks)

    print("\nKhởi tạo Hybrid Retriever (RRF)...")
    hybrid = HybridRetriever(bm25_retriever=bm25, dense_retriever=dense)

    if args.query:
        print(f"\n=== ĐANG THỰC HIỆN HYBRID SEARCH: '{args.query}' (candidate_k={args.candidate_k}, top_k={args.top_k}) ===")
        results = hybrid.search(args.query, top_k=args.top_k, candidate_k=args.candidate_k)
        print_hybrid_table(results)

    if args.eval_examples or not args.query:
        run_hybrid_evaluation_examples(bm25, dense, hybrid, top_k=args.top_k, candidate_k=args.candidate_k)

if __name__ == "__main__":
    main()
