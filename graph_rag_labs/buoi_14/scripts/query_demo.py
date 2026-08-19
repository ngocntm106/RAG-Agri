import os
import sys
import argparse

# Reconfigure stdout to UTF-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.insert(0, os.path.abspath('.'))

from src.unified_retriever import UnifiedRetriever

def print_retrieval_results(results: list[dict], method: str):
    print("\n" + "="*88)
    print(f"RETRIEVAL RESULTS (Method: {method.upper()})")
    print("="*88)
    
    if not results:
        print("Không tìm thấy kết quả phù hợp.")
        return

    header = f"{'Rank':<5} | {'Score':<10} | {'Chunk ID':<38} | {'Citation'}"
    print(header)
    print("-" * 110)
    for r in results:
        score_str = f"{r['score']:.4f}"
        print(f"{r['rank']:<5} | {score_str:<10} | {r['chunk_id']:<38} | {r['citation']}")
        
        # In thêm thông tin score chi tiết nếu là hybrid_rerank
        if r.get("hybrid_score") is not None and r.get("rerank_score") is not None:
            print(f"      [Scores] Hybrid RRF: {r['hybrid_score']:.6f} | Rerank Score: {r['rerank_score']:.4f}")
            
        snippet = r['text'].replace('\n', ' ')[:110]
        print(f"      Text: {snippet}...\n")

def print_graph_hints(hints: list[dict]):
    print("="*88)
    print("GRAPH HINTS (1-Hop Context for Retrieved Chunks)")
    print("="*88)
    
    if not hints:
        print("Không có thông tin Graph Hints.")
        return

    for idx, h in enumerate(hints, 1):
        print(f"[{idx}] Chunk ID: {h['chunk_id']}")
        print(f"    - Văn bản gốc     : {h['source_file']} (Document ID: {h['document_id']})")
        print(f"    - Cấu trúc tuần tự: [PREV: {h['prev_chunk_id'][:18]}...] -> [THIS CHUNK] -> [NEXT: {h['next_chunk_id'][:18]}...]")
        
        if h['document_relations']:
            print(f"    - Quan hệ văn bản :")
            for rel in h['document_relations']:
                arrow = f"--[:{rel['type']}]--> {rel['target']}" if rel.get('direction') == 'OUTGOING' else f"<--[:{rel['type']}]-- {rel['target']}"
                print(f"      * {arrow} ({rel['desc']})")
        else:
            print(f"    - Quan hệ văn bản : Không có quan hệ trực tiếp trong dữ liệu")
        print()

def main():
    parser = argparse.ArgumentParser(description="Hệ thống Retrieval Thống Nhất & Graph Hints")
    parser.add_argument("--query", type=str, default="Quy định về niêm phong và đóng gói tiền mặt trong ngành Ngân hàng", help="Câu hỏi cần tìm kiếm")
    parser.add_argument("--method", type=str, default="hybrid_rerank", choices=["bm25", "dense", "hybrid", "hybrid_rerank"], help="Phương pháp tìm kiếm")
    parser.add_argument("--top-k", type=int, default=5, help="Số lượng kết quả trả về")
    parser.add_argument("--candidate-k", type=int, default=20, help="Số lượng candidates cho RRF / Reranker")
    args = parser.parse_args()

    print(f"=== UNIFIED RETRIEVAL DEMO: '{args.query}' ===")
    print(f"Cấu hình: Method={args.method.upper()}, Top-K={args.top_k}, Candidate-K={args.candidate_k}\n")

    retriever = UnifiedRetriever()
    
    # 1. Thực hiện retrieval qua hàm thống nhất
    results = retriever.retrieve(
        question=args.query,
        method=args.method,
        top_k=args.top_k,
        candidate_k=args.candidate_k
    )
    
    # 2. In bảng kết quả
    print_retrieval_results(results, args.method)
    
    # 3. Trích xuất và in Graph Hints
    hints = retriever.get_graph_hints(results)
    print_graph_hints(hints)

if __name__ == "__main__":
    main()
