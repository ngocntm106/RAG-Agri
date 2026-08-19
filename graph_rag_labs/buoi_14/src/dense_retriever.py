import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from src.citation import build_citation

class DenseRetriever:
    def __init__(
        self, 
        df_chunks: pd.DataFrame, 
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir: str = "cache"
    ):
        """
        Khởi tạo Dense Retriever với SentenceTransformer và cơ chế cache vector embeddings.
        """
        self.df_chunks = df_chunks.copy().reset_index(drop=True)
        self.df_chunks['text'] = self.df_chunks['text'].fillna('')
        self.model_name = model_name
        self.cache_dir = cache_dir
        
        # Load embedding model
        print(f"[DenseRetriever] Đang khởi tạo embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Tạo hoặc nạp vector cache
        self.embeddings = self._get_or_compute_embeddings()

    def _get_or_compute_embeddings(self) -> np.ndarray:
        os.makedirs(self.cache_dir, exist_ok=True)
        emb_file = os.path.join(self.cache_dir, "dense_embeddings.npy")
        ids_file = os.path.join(self.cache_dir, "dense_chunk_ids.json")
        
        current_ids = self.df_chunks['chunk_id'].astype(str).tolist()
        
        if os.path.exists(emb_file) and os.path.exists(ids_file):
            try:
                with open(ids_file, "r", encoding="utf-8") as f:
                    cached_ids = json.load(f)
                if cached_ids == current_ids:
                    print(f"[DenseRetriever] Nạp {len(cached_ids)} embeddings từ cache: {emb_file}")
                    return np.load(emb_file)
            except Exception as e:
                print(f"[DenseRetriever] Không thể đọc cache ({e}), sẽ tiến hành tính lại...")

        print(f"[DenseRetriever] Đang tính toán embeddings cho {len(self.df_chunks)} chunks...")
        # Kết hợp title, article và text để embedding đầy đủ ngữ cảnh nhất
        texts_to_embed = [
            f"{row.get('title', '')} - {row.get('article', '')}: {row['text']}".strip()
            if (row.get('title') or row.get('article')) else row['text']
            for _, row in self.df_chunks.iterrows()
        ]
        
        embeddings = self.model.encode(
            texts_to_embed, 
            batch_size=64, 
            show_progress_bar=True, 
            normalize_embeddings=True
        )
        embeddings = np.array(embeddings, dtype=np.float32)
        
        # Lưu cache
        np.save(emb_file, embeddings)
        with open(ids_file, "w", encoding="utf-8") as f:
            json.dump(current_ids, f, ensure_ascii=False)
            
        print(f"[DenseRetriever] Đã lưu vector embeddings vào {emb_file}")
        return embeddings

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Tìm kiếm ngữ nghĩa (Dense Retrieval) dựa trên Cosine Similarity.
        """
        if not query or not query.strip():
            return []
            
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]
        # Tính Cosine Similarity (dot product giữa các vector đã normalize)
        scores = np.dot(self.embeddings, query_embedding)
        
        # Lấy top_k index điểm cao nhất
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df_chunks.iloc[idx]
            score = float(scores[idx])
            citation = build_citation(row)
            
            results.append({
                "rank": rank,
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "text": str(row["text"]),
                "retrieval_score": round(score, 4),
                "retrieval_method": "Dense",
                "citation": citation
            })
            
        return results
