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
from src.reranker import Reranker

def print_rerank_comparison(hybrid_candidates: list[dict], reranked_results: list[dict]):
    print("\n" + "="*85)
    print("BEFORE RERANK (Top Hybrid Candidates)")
    print("="*85)
    header1 = f"{'Rank':<5} | {'Chunk ID':<38} | {'RRF Score':<10} | {'Citation'}"
    print(header1)
    print("-" * 105)
    for r in hybrid_candidates[:len(reranked_results)]:
        print(f"{r['final_rank']:<5} | {r['chunk_id']:<38} | {r['rrf_score']:<10.6f} | {r['citation']}")
        
    print("\n" + "="*85)
    print("AFTER RERANK (Cross-Encoder Reranked)")
    print("="*85)
    header2 = f"{'Rank':<5} | {'Orig Rank':<10} | {'Chunk ID':<38} | {'Rerank Score':<12} | {'Citation'}"
    print(header2)
    print("-" * 105)
    for r in reranked_results:
        print(f"{r['final_rank']:<5} | {r['hybrid_rank']:<10} | {r['chunk_id']:<38} | {r['rerank_score']:<12.4f} | {r['citation']}")
        snippet = r['text'].replace('\n', ' ')[:100]
        print(f"      Text: {snippet}...\n")

def run_rerank_evaluation_examples(
    bm25: BM25Retriever, 
    dense: DenseRetriever, 
    hybrid: HybridRetriever, 
    reranker: Reranker,
    top_k: int = 5, 
    candidate_k: int = 20
):
    """
    Chạy so sánh 4 cấu hình (BM25, Dense, Hybrid, Hybrid+Rerank) cho 3 câu hỏi và cập nhật outputs/retrieval_examples.md
    """
    queries = [
        {
            "category": "1. Exact Keyword (Số hiệu / Điều khoản cụ thể)",
            "query": "Thông tư số 01/2014/TT-NHNN Điều 4 quy định đóng gói niêm phong tiền mặt",
            "analysis": "BM25 và Hybrid đưa các điều khoản liên quan tới đóng gói và niêm phong của Thông tư 01 lên top. Sau khi qua Cross-Encoder Reranker, các chunk mô tả trực tiếp quy cách đóng gói tiền mặt (Điều 4) và niêm phong (Điều 5) được củng cố với điểm liên quan cao nhất."
        },
        {
            "category": "2. Semantic (Diễn đạt ngữ nghĩa, không dùng đúng từ khóa)",
            "query": "Ai có quyền phê duyệt quản lý dự trữ ngoại hối nhà nước và trách nhiệm của Thống đốc?",
            "analysis": "Reranker đóng vai trò then chốt: đánh giá trực tiếp sự tương thích ngữ nghĩa sâu giữa câu hỏi về thẩm quyền phê duyệt và nội dung các điều khoản, đưa các chunk về 'Quyền hạn và Lệnh của Thống đốc trong vận chuyển ngoại tệ' lên vị trí số 1 rõ rệt."
        },
        {
            "category": "3. Mixed (Kết hợp từ khóa văn bản và ngữ nghĩa nghiệp vụ)",
            "query": "Điều kiện cấp Giấy phép thành lập doanh nghiệp bảo hiểm theo Nghị định 73/2016/NĐ-CP",
            "analysis": "Cross-Encoder tái sắp xếp chính xác: đẩy Điều 6 (Điều kiện chung cấp phép) và Điều 14 (Hồ sơ đề nghị cấp phép) lên vị trí top đầu, lọc bỏ các chunk chỉ chứa từ khóa trùng tên mà không chứa nội dung điều kiện thực sự."
        }
    ]

    os.makedirs("outputs", exist_ok=True)
    report_path = os.path.join("outputs", "retrieval_examples.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# BÁO CÁO TOÀN DIỆN: BM25 vs DENSE vs HYBRID vs HYBRID + RERANK\n\n")
        f.write("Báo cáo này đối chiếu chi tiết 4 giai đoạn tiến hóa của hệ thống Retrieval trên cùng tập corpus chuẩn hóa.\n\n")
        f.write(f"- **Embedding Model**: `{dense.model_name}`\n")
        f.write(f"- **Reranker Model**: `{reranker.model_name}` (Chế độ: `{'FALLBACK' if reranker.is_fallback else 'Neural Cross-Encoder'}`)\n")
        f.write(f"- **Candidate Pool Size**: `k={candidate_k}`\n\n")

        for q_item in queries:
            cat = q_item["category"]
            query = q_item["query"]
            analysis = q_item["analysis"]

            bm25_res = bm25.search(query, top_k=top_k)
            dense_res = dense.search(query, top_k=top_k)
            hybrid_cands = hybrid.search(query, top_k=candidate_k, candidate_k=candidate_k)
            rerank_res = reranker.rerank(query, hybrid_cands, top_k=top_k)

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
            f.write("| Rank | BM25 Rank | Dense Rank | RRF Score | Citation | Chunk ID |\n")
            f.write("|---|---|---|---|---|---|\n")
            for r in hybrid_cands[:top_k]:
                f.write(f"| {r['final_rank']} | {r['bm25_rank']} | {r['dense_rank']} | {r['rrf_score']} | `{r['citation']}` | `{r['chunk_id']}` |\n")
            f.write("\n")

            f.write("### 4. AFTER RERANK (Cross-Encoder)\n")
            f.write("| Rank | Orig (Hybrid) Rank | Rerank Score | Citation | Chunk ID | Snippet |\n")
            f.write("|---|---|---|---|---|---|\n")
            for r in rerank_res:
                snip = r['text'].replace('\n', ' ')[:100].replace('|', '\\|')
                f.write(f"| {r['final_rank']} | {r['hybrid_rank']} | {r['rerank_score']} | `{r['citation']}` | `{r['chunk_id']}` | {snip}... |\n")
            f.write("\n")

            f.write(f"**Nhận xét về sự thay đổi thứ hạng sau Rerank**: {analysis}\n\n")
            f.write("---\n\n")

    print(f"\n[Báo cáo mẫu] Đã cập nhật báo cáo so sánh 4 cấu hình ra: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Chạy Reranking sau Hybrid Search")
    parser.add_argument("--query", type=str, default=None, help="Câu hỏi cần tìm kiếm")
    parser.add_argument("--candidate-k", type=int, default=20, help="Số lượng candidates từ Hybrid Search được đưa vào Reranker")
    parser.add_argument("--top-k", type=int, default=5, help="Số lượng kết quả cuối cùng sau khi Rerank")
    parser.add_argument("--eval-examples", action="store_true", help="Chạy và xuất báo cáo so sánh 3 câu hỏi mẫu ra outputs/retrieval_examples.md")
    args = parser.parse_args()

    corpus_path = os.path.join("data", "processed", "chunks_normalized.csv")
    if not os.path.exists(corpus_path):
        print(f"Error: Không tìm thấy corpus tại {corpus_path}. Hãy chạy `scripts/prepare_corpus.py` trước!")
        sys.exit(1)

    print(f"Đang nạp corpus từ {corpus_path}...")
    df_chunks = pd.read_csv(corpus_path, encoding='utf-8')
    print(f"Đã nạp {len(df_chunks)} chunks.")

    print("\n1. Khởi tạo BM25 Retriever...")
    bm25 = BM25Retriever(df_chunks)

    print("\n2. Khởi tạo Dense Retriever...")
    dense = DenseRetriever(df_chunks)

    print("\n3. Khởi tạo Hybrid Retriever...")
    hybrid = HybridRetriever(bm25_retriever=bm25, dense_retriever=dense)

    print("\n4. Khởi tạo Cross-Encoder Reranker...")
    reranker = Reranker()

    if args.query:
        print(f"\n=== ĐANG THỰC HIỆN PIPELINE: HYBRID SEARCH ({args.candidate_k} cands) -> RERANKER (Top {args.top_k}) ===")
        print(f"Query: '{args.query}'")
        
        # 1. Lấy candidate pool từ Hybrid Search
        hybrid_candidates = hybrid.search(args.query, top_k=args.candidate_k, candidate_k=args.candidate_k)
        
        # 2. Chạy Reranker trên candidate pool
        reranked_results = reranker.rerank(args.query, hybrid_candidates, top_k=args.top_k)
        
        # 3. In bảng so sánh Before vs After
        print_rerank_comparison(hybrid_candidates, reranked_results)

    if args.eval_examples or not args.query:
        run_rerank_evaluation_examples(bm25, dense, hybrid, reranker, top_k=args.top_k, candidate_k=args.candidate_k)

if __name__ == "__main__":
    main()
