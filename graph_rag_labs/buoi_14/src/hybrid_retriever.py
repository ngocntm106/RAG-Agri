import pandas as pd
from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever

class HybridRetriever:
    def __init__(
        self, 
        df_chunks: pd.DataFrame = None, 
        bm25_retriever: BM25Retriever = None, 
        dense_retriever: DenseRetriever = None
    ):
        """
        Khởi tạo Hybrid Retriever kết hợp BM25 và Dense Retrieval bằng RRF.
        Có thể truyền trực tiếp retriever instances hoặc df_chunks để tự khởi tạo.
        """
        if bm25_retriever is not None and dense_retriever is not None:
            self.bm25_retriever = bm25_retriever
            self.dense_retriever = dense_retriever
            self.df_chunks = bm25_retriever.df_chunks
        elif df_chunks is not None:
            self.df_chunks = df_chunks.copy().reset_index(drop=True)
            self.bm25_retriever = BM25Retriever(self.df_chunks)
            self.dense_retriever = DenseRetriever(self.df_chunks)
        else:
            raise ValueError("Phải cung cấp df_chunks hoặc cả bm25_retriever và dense_retriever!")

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        candidate_k: int = 20, 
        rrf_k: int = 60
    ) -> list[dict]:
        """
        Thực hiện tìm kiếm Hybrid kết hợp BM25 và Dense bằng Reciprocal Rank Fusion (RRF).
        
        RRF Score:
            Score(d) = sum_{m in {bm25, dense}} 1 / (rrf_k + rank_m(d))
        """
        if not query or not query.strip():
            return []

        # 1. Thu thập candidate_k từ mỗi retriever
        bm25_candidates = self.bm25_retriever.search(query, top_k=candidate_k)
        dense_candidates = self.dense_retriever.search(query, top_k=candidate_k)

        # 2. Hợp nhất candidates theo chunk_id
        candidates_map = {}

        for item in bm25_candidates:
            cid = item["chunk_id"]
            rank = item["rank"]
            if cid not in candidates_map:
                candidates_map[cid] = {
                    "chunk_id": cid,
                    "document_id": item["document_id"],
                    "text": item["text"],
                    "citation": item["citation"],
                    "bm25_rank": rank,
                    "dense_rank": None,
                    "rrf_score": 0.0
                }
            else:
                candidates_map[cid]["bm25_rank"] = rank
            candidates_map[cid]["rrf_score"] += 1.0 / (rrf_k + rank)

        for item in dense_candidates:
            cid = item["chunk_id"]
            rank = item["rank"]
            if cid not in candidates_map:
                candidates_map[cid] = {
                    "chunk_id": cid,
                    "document_id": item["document_id"],
                    "text": item["text"],
                    "citation": item["citation"],
                    "bm25_rank": None,
                    "dense_rank": rank,
                    "rrf_score": 0.0
                }
            else:
                candidates_map[cid]["dense_rank"] = rank
            candidates_map[cid]["rrf_score"] += 1.0 / (rrf_k + rank)

        # 3. Sắp xếp theo rrf_score giảm dần
        sorted_candidates = sorted(
            candidates_map.values(), 
            key=lambda x: x["rrf_score"], 
            reverse=True
        )

        # 4. Cắt top_k và chuẩn hóa schema đầu ra
        results = []
        for rank, c in enumerate(sorted_candidates[:top_k], 1):
            results.append({
                "final_rank": rank,
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "bm25_rank": c["bm25_rank"] if c["bm25_rank"] is not None else "-",
                "dense_rank": c["dense_rank"] if c["dense_rank"] is not None else "-",
                "rrf_score": round(c["rrf_score"], 6),
                "text": c["text"],
                "citation": c["citation"],
                "retrieval_method": "Hybrid (RRF)"
            })

        return results
