import os
import numpy as np
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(
        self, 
        model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    ):
        """
        Khởi tạo Cross-Encoder Reranker cho tiếng Việt & đa ngôn ngữ.
        """
        self.model_name = model_name
        self.is_fallback = False
        self.model = None
        
        print(f"[Reranker] Đang tải mô hình Cross-Encoder: {model_name}...")
        try:
            self.model = CrossEncoder(model_name)
            print(f"[Reranker] Khởi tạo mô hình Cross-Encoder thành công!")
        except Exception as e:
            print(f"[Reranker] [CẢNH BÁO] Không thể nạp mô hình neural {model_name}: {e}")
            print(f"[Reranker] Kích hoạt chế độ FALLBACK (Non-Neural Reranker)")
            self.is_fallback = True

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        """
        Tái xếp hạng danh sách candidates từ Hybrid Search theo ngữ cảnh query.
        Input: candidates (chỉ từ Hybrid candidate pool, không chạy trên toàn corpus).
        """
        if not candidates or not query or not query.strip():
            return []

        # Nếu đang ở chế độ Fallback
        if self.is_fallback or self.model is None:
            # Fallback đơn giản: giữ nguyên hybrid score hoặc tính điểm overlap tượng trưng
            results = []
            for rank, c in enumerate(candidates[:top_k], 1):
                results.append({
                    "final_rank": rank,
                    "chunk_id": str(c["chunk_id"]),
                    "document_id": str(c["document_id"]),
                    "hybrid_rank": c.get("final_rank", rank),
                    "hybrid_score": c.get("rrf_score", 0.0),
                    "rerank_score": round(float(c.get("rrf_score", 0.0)), 4),
                    "text": str(c["text"]),
                    "citation": str(c["citation"]),
                    "retrieval_method": "FALLBACK (Non-Neural)"
                })
            return results

        # Chuẩn bị cặp (query, candidate text)
        pairs = []
        for c in candidates:
            # Tạo đoạn text ngữ cảnh gồm cả tiêu đề văn bản/điều khoản nếu có
            context_text = f"{c.get('title', '')} - {c.get('article', '')}: {c['text']}".strip()
            pairs.append((query, context_text if context_text else c['text']))

        # Tính điểm Cross-Encoder
        scores = self.model.predict(pairs)

        # Gán điểm và sắp xếp lại candidates
        scored_candidates = []
        for i, c in enumerate(candidates):
            scored_candidates.append({
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "hybrid_rank": c.get("final_rank", i + 1),
                "hybrid_score": c.get("rrf_score", 0.0),
                "rerank_score": float(scores[i]),
                "text": c["text"],
                "citation": c["citation"]
            })

        # Sắp xếp giảm dần theo rerank_score
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Lấy top_k kết quả sau rerank
        results = []
        for rank, c in enumerate(scored_candidates[:top_k], 1):
            results.append({
                "final_rank": rank,
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "hybrid_rank": c["hybrid_rank"],
                "hybrid_score": c["hybrid_score"],
                "rerank_score": round(c["rerank_score"], 4),
                "text": c["text"],
                "citation": c["citation"],
                "retrieval_method": "Cross-Encoder Rerank"
            })

        return results
