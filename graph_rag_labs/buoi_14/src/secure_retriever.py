"""
Module: secure_retriever.py
Purpose: Enterprise-grade Secure Role-Based Access Control (RBAC) Retrieval Pipeline.
Supports:
  - BM25 Search with pre/post access filtering
  - Dense Embedding Search with vectorized access masking
  - Graph Retrieval (Neo4j) with parameterized Cypher RBAC WHERE filters
  - Hybrid Search (Reciprocal Rank Fusion - RRF) on authorized candidates
  - Cross-Encoder Reranking strictly restricted to authorized candidates
  - Secure Graph Context & 1-hop Citation exploration with role filtering
"""

import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# Ensure root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.citation import build_citation
from src.bm25_retriever import tokenize_legal_text
from src.reranker import Reranker
from src.config import (
    get_neo4j_config,
    validate_roles,
    VALID_ROLES,
    ROLE_GUEST,
    CHUNKS_SECURE_PATH,
    CACHE_DIR
)


class SecureRetriever:
    def __init__(
        self,
        corpus_path: Path | str = CHUNKS_SECURE_PATH,
        embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir: Path | str = CACHE_DIR
    ):
        """
        Khởi tạo Secure Retrieval Pipeline với dữ liệu có gắn thẻ bảo mật (chunks_secure.csv).
        """
        self.corpus_path = Path(corpus_path)
        self.cache_dir = Path(cache_dir)
        self.embedding_model_name = embedding_model_name

        if not self.corpus_path.exists():
            raise FileNotFoundError(
                f"[SecureRetriever] Không tìm thấy file dữ liệu bảo mật tại: {self.corpus_path}.\n"
                "Vui lòng chạy 'python scripts/assign_security_tags.py' trước!"
            )

        print(f"[SecureRetriever] Đang nạp tập dữ liệu bảo mật từ: {self.corpus_path.name}...")
        self.df_chunks = pd.read_csv(self.corpus_path, encoding="utf-8")
        self.df_chunks["text"] = self.df_chunks["text"].fillna("")
        self.df_chunks["title"] = self.df_chunks["title"].fillna("")
        self.df_chunks["article"] = self.df_chunks["article"].fillna("")
        self.df_chunks["source_file"] = self.df_chunks["source_file"].fillna("")

        # Parse allowed_roles thành Python set & list để lọc siêu nhanh
        self._parsed_roles = []
        self._parsed_sets = []
        for raw in self.df_chunks["allowed_roles"]:
            try:
                roles = json.loads(raw) if isinstance(raw, str) else list(raw)
            except Exception:
                roles = [ROLE_GUEST]
            self._parsed_roles.append(roles)
            self._parsed_sets.append(set(roles))

        self.df_chunks["_allowed_roles_list"] = self._parsed_roles
        self.df_chunks["_allowed_roles_set"] = self._parsed_sets

        # 1. Khởi tạo BM25 index trên toàn bộ corpus
        print("[SecureRetriever] Đang khởi tạo chỉ mục BM25...")
        self.corpus_tokens = [
            tokenize_legal_text(f"{row['text']} {row.get('article', '')} {row.get('source_file', '')}")
            for _, row in self.df_chunks.iterrows()
        ]
        self.bm25_index = BM25Okapi(self.corpus_tokens)

        # 2. Khởi tạo Dense Embedding Model & Vector Cache
        print(f"[SecureRetriever] Đang nạp mô hình Dense Embedding: {self.embedding_model_name}...")
        self.dense_model = SentenceTransformer(self.embedding_model_name)
        self.embeddings = self._get_or_compute_embeddings()

        # 3. Khởi tạo Lazy Reranker (chỉ nạp khi cần)
        self._reranker = None

        # 4. Khởi tạo Neo4j Driver từ cấu hình .env
        self.neo4j_driver = None
        self.neo4j_db = "neo4j"
        self._init_neo4j()

    def _init_neo4j(self):
        """Khởi tạo kết nối Neo4j an toàn từ cấu hình file .env (timeout ngắn nếu offline)."""
        try:
            from neo4j import GraphDatabase
            cfg = get_neo4j_config()
            self.neo4j_db = cfg["database"]
            driver = GraphDatabase.driver(
                cfg["uri"],
                auth=(cfg["user"], cfg["password"]),
                connection_timeout=2.0
            )
            with driver.session(database=self.neo4j_db) as session:
                res = session.run("RETURN 1 AS connected")
                rec = res.single()
                if rec and rec["connected"] == 1:
                    self.neo4j_driver = driver
                    print(f"[SecureRetriever] Kết nối Neo4j Graph DB thành công ({cfg['uri']}).")
                else:
                    self.neo4j_driver = None
        except Exception:
            self.neo4j_driver = None


    def _get_or_compute_embeddings(self) -> np.ndarray:
        """Tạo hoặc nạp vector embeddings từ cache npy."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        emb_file = self.cache_dir / "dense_embeddings.npy"
        ids_file = self.cache_dir / "dense_chunk_ids.json"

        current_ids = self.df_chunks["chunk_id"].astype(str).tolist()

        if emb_file.exists() and ids_file.exists():
            try:
                with open(ids_file, "r", encoding="utf-8") as f:
                    cached_ids = json.load(f)
                if cached_ids == current_ids:
                    print(f"[SecureRetriever] Nạp {len(cached_ids):,} embeddings từ cache: {emb_file.name}")
                    return np.load(emb_file)
            except Exception as e:
                print(f"[SecureRetriever] Lỗi đọc cache ({e}), tiến hành tính toán lại...")

        print(f"[SecureRetriever] Đang tính toán embeddings cho {len(self.df_chunks):,} chunks...")
        texts_to_embed = [
            f"{row.get('title', '')} - {row.get('article', '')}: {row['text']}".strip()
            if (row.get("title") or row.get("article")) else row["text"]
            for _, row in self.df_chunks.iterrows()
        ]

        embeddings = self.dense_model.encode(
            texts_to_embed,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        embeddings = np.array(embeddings, dtype=np.float32)

        np.save(emb_file, embeddings)
        with open(ids_file, "w", encoding="utf-8") as f:
            json.dump(current_ids, f, ensure_ascii=False)

        print(f"[SecureRetriever] Đã lưu vector cache vào: {emb_file.name}")
        return embeddings

    @property
    def reranker(self) -> Reranker:
        """Lazy load Cross-Encoder Reranker."""
        if self._reranker is None:
            self._reranker = Reranker()
        return self._reranker

    def _get_role_mask(self, user_roles: list[str]) -> np.ndarray:
        """
        Tạo boolean mask numpy đại diện cho các chunk mà user_roles có quyền đọc.
        Điều kiện: user_roles giao với allowed_roles_set != rỗng.
        """
        user_roles_set = set(validate_roles(user_roles))
        mask = np.array([bool(s & user_roles_set) for s in self._parsed_sets], dtype=bool)
        return mask

    # ==========================================================================
    # 1. SECURE BM25 SEARCH
    # ==========================================================================
    def search_bm25(self, query: str, user_roles: list[str], top_k: int = 5) -> list[dict]:
        """
        Tìm kiếm BM25 an toàn: Lọc bỏ hoàn toàn các tài liệu ngoài phạm vi quyền trước khi lấy Top-K.
        """
        if not query or not query.strip():
            return []

        clean_roles = validate_roles(user_roles)
        tokens = tokenize_legal_text(query)
        if not tokens:
            return []

        # Tính điểm BM25 toàn bộ corpus
        raw_scores = np.array(self.bm25_index.get_scores(tokens), dtype=np.float32)

        # Lọc quyền bằng Boolean Mask (gán -inf cho các tài liệu bị cấm)
        auth_mask = self._get_role_mask(clean_roles)
        masked_scores = np.where(auth_mask, raw_scores, -np.inf)

        # Lấy top_k index điểm cao nhất (chỉ trong tập được phép)
        valid_indices = np.where(auth_mask)[0]
        if len(valid_indices) == 0:
            return []

        top_indices = np.argsort(masked_scores)[::-1][:top_k]
        # Lọc bỏ các phần tử có score == -inf nếu tổng số văn bản hợp lệ < top_k
        top_indices = [idx for idx in top_indices if masked_scores[idx] != -np.inf]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df_chunks.iloc[idx]
            score = float(masked_scores[idx])
            citation = build_citation(row)
            results.append({
                "rank": rank,
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "source_file": str(row.get("source_file", "")),
                "title": str(row.get("title", "")),
                "article": str(row.get("article", "")),
                "clause": str(row.get("clause", "")),
                "text": str(row["text"]),
                "score": round(score, 4),
                "citation": citation,
                "retrieval_method": "BM25 (Secure)",
                "allowed_roles": self._parsed_roles[idx],
                "hybrid_score": None,
                "rerank_score": None
            })
        return results

    # ==========================================================================
    # 2. SECURE DENSE SEARCH
    # ==========================================================================
    def search_dense(self, query: str, user_roles: list[str], top_k: int = 5) -> list[dict]:
        """
        Tìm kiếm Dense Embedding an toàn: Lọc bỏ các chunk cấm qua Vectorized Access Masking.
        """
        if not query or not query.strip():
            return []

        clean_roles = validate_roles(user_roles)
        query_emb = self.dense_model.encode([query], normalize_embeddings=True)[0]

        # Tính Cosine Similarity toàn bộ corpus
        raw_scores = np.dot(self.embeddings, query_emb)

        # Áp dụng RBAC Mask
        auth_mask = self._get_role_mask(clean_roles)
        masked_scores = np.where(auth_mask, raw_scores, -np.inf)

        valid_indices = np.where(auth_mask)[0]
        if len(valid_indices) == 0:
            return []

        top_indices = np.argsort(masked_scores)[::-1][:top_k]
        top_indices = [idx for idx in top_indices if masked_scores[idx] != -np.inf]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df_chunks.iloc[idx]
            score = float(masked_scores[idx])
            citation = build_citation(row)
            results.append({
                "rank": rank,
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "source_file": str(row.get("source_file", "")),
                "title": str(row.get("title", "")),
                "article": str(row.get("article", "")),
                "clause": str(row.get("clause", "")),
                "text": str(row["text"]),
                "score": round(score, 4),
                "citation": citation,
                "retrieval_method": "Dense (Secure)",
                "allowed_roles": self._parsed_roles[idx],
                "hybrid_score": None,
                "rerank_score": None
            })
        return results

    # ==========================================================================
    # 3. SECURE GRAPH SEARCH (Neo4j)
    # ==========================================================================
    def search_graph(self, query: str, user_roles: list[str], top_k: int = 5) -> list[dict]:
        """
        Truy vấn đồ thị Neo4j có tích hợp mệnh đề kiểm tra quyền truy cập:
        WHERE any(role IN d.allowed_roles WHERE role IN $user_roles)
        """
        clean_roles = validate_roles(user_roles)
        if not self.neo4j_driver:
            # Fallback nếu Neo4j chưa khởi động: sử dụng BM25 an toàn
            return self.search_bm25(query, clean_roles, top_k=top_k)

        try:
            with self.neo4j_driver.session(database=self.neo4j_db) as session:
                cypher_query = """
                MATCH (v:VanBan)-[:CONTAINS]->(d:DieuKhoan)
                WHERE any(role IN d.allowed_roles WHERE role IN $user_roles)
                  AND (
                    toLower(d.text) CONTAINS toLower($query) 
                    OR toLower(d.article) CONTAINS toLower($query)
                    OR toLower(v.title) CONTAINS toLower($query)
                  )
                RETURN 
                    d.id AS chunk_id,
                    v.id AS document_id,
                    v.source_file AS source_file,
                    v.title AS title,
                    d.chapter AS chapter,
                    d.section AS section,
                    d.article AS article,
                    d.clause AS clause,
                    d.text AS text,
                    d.allowed_roles AS allowed_roles
                LIMIT $top_k
                """
                res = session.run(cypher_query, user_roles=clean_roles, query=query.strip(), top_k=top_k)
                results = []
                for rank, record in enumerate(res, 1):
                    row_dict = dict(record)
                    citation = build_citation(row_dict)
                    results.append({
                        "rank": rank,
                        "chunk_id": str(row_dict["chunk_id"]),
                        "document_id": str(row_dict["document_id"]),
                        "source_file": str(row_dict.get("source_file", "")),
                        "title": str(row_dict.get("title", "")),
                        "article": str(row_dict.get("article", "")),
                        "clause": str(row_dict.get("clause", "")),
                        "text": str(row_dict.get("text", "")),
                        "score": 1.0,
                        "citation": citation,
                        "retrieval_method": "Neo4j Graph (Secure)",
                        "allowed_roles": row_dict.get("allowed_roles", [ROLE_GUEST]),
                        "hybrid_score": None,
                        "rerank_score": None
                    })
                return results
        except Exception as e:
            print(f"[SecureRetriever] Lỗi truy vấn Neo4j Graph ({e}), chuyển sang fallback...")
            return self.search_bm25(query, clean_roles, top_k=top_k)

    # ==========================================================================
    # 4. SECURE HYBRID SEARCH (RRF)
    # ==========================================================================
    def search_hybrid(
        self,
        query: str,
        user_roles: list[str],
        top_k: int = 5,
        candidate_k: int = 20,
        rrf_k: int = 60
    ) -> list[dict]:
        """
        Kết hợp BM25 an toàn và Dense an toàn theo Reciprocal Rank Fusion (RRF).
        Chỉ các ứng viên hợp lệ mới được đưa vào bảng xếp hạng.
        """
        clean_roles = validate_roles(user_roles)
        bm25_cands = self.search_bm25(query, clean_roles, top_k=candidate_k)
        dense_cands = self.search_dense(query, clean_roles, top_k=candidate_k)

        # Tính toán điểm RRF
        rrf_scores = {}
        cand_map = {}

        for rank, item in enumerate(bm25_cands, 1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            cand_map[cid] = item

        for rank, item in enumerate(dense_cands, 1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            if cid not in cand_map:
                cand_map[cid] = item

        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:top_k]

        results = []
        for rank, cid in enumerate(sorted_cids, 1):
            item = cand_map[cid].copy()
            score = round(rrf_scores[cid], 6)
            item["rank"] = rank
            item["score"] = score
            item["hybrid_score"] = score
            item["retrieval_method"] = "Hybrid (RRF Secure)"
            results.append(item)

        return results

    # ==========================================================================
    # 5. SECURE HYBRID + RERANK SEARCH
    # ==========================================================================
    def search_hybrid_rerank(
        self,
        query: str,
        user_roles: list[str],
        top_k: int = 5,
        candidate_k: int = 20
    ) -> list[dict]:
        """
        Pipeline cao cấp nhất:
        1. Lấy Top candidate_k ứng viên đã qua bộ lọc quyền truy cập (Secure Hybrid).
        2. Đưa các ứng viên an toàn này vào Cross-Encoder Reranker.
        3. Tuyệt đối không để tài liệu cấm lọt vào Reranker.
        """
        clean_roles = validate_roles(user_roles)
        # 1. Lấy ứng viên an toàn
        candidates = self.search_hybrid(
            query=query,
            user_roles=clean_roles,
            top_k=candidate_k,
            candidate_k=candidate_k
        )
        if not candidates:
            return []

        # Map candidate details by chunk_id
        cand_map = {c["chunk_id"]: c for c in candidates}

        # 2. Xếp hạng lại bằng Cross-Encoder
        raw_reranked = self.reranker.rerank(query, candidates, top_k=top_k)

        # 3. Chuẩn hóa kết quả và giữ đầy đủ metadata phân quyền
        results = []
        for r in raw_reranked:
            cid = r["chunk_id"]
            orig = cand_map.get(cid, {})
            results.append({
                "rank": r["final_rank"],
                "chunk_id": cid,
                "document_id": str(orig.get("document_id", r.get("document_id", ""))),
                "source_file": orig.get("source_file", ""),
                "title": orig.get("title", ""),
                "article": orig.get("article", ""),
                "clause": orig.get("clause", ""),
                "text": orig.get("text", r.get("text", "")),
                "score": round(float(r["rerank_score"]), 4),
                "citation": orig.get("citation", r.get("citation", "")),
                "retrieval_method": "Hybrid + Rerank (Secure)",
                "allowed_roles": orig.get("allowed_roles", [ROLE_GUEST]),
                "hybrid_score": orig.get("score"),
                "rerank_score": round(float(r["rerank_score"]), 4)
            })
        return results


    # ==========================================================================
    # 6. UNIFIED RETRIEVE API
    # ==========================================================================
    def retrieve(
        self,
        query: str,
        user_roles: list[str],
        method: str = "hybrid_rerank",
        top_k: int = 5,
        candidate_k: int = 20
    ) -> list[dict]:
        """
        Hàm retrieval thống nhất nhận vào query và user_roles bắt buộc.
        
        Args:
            query: Câu hỏi tìm kiếm
            user_roles: Danh sách vai trò của người dùng (vd: ["Guest"] hoặc ["Admin", "HR"])
            method: 'bm25' | 'dense' | 'graph' | 'hybrid' | 'hybrid_rerank'
            top_k: Số lượng kết quả cuối cùng
            candidate_k: Số lượng ứng viên trung gian cho Hybrid/Rerank
        """
        clean_roles = validate_roles(user_roles)
        method = method.lower().strip()

        if method == "bm25":
            return self.search_bm25(query, clean_roles, top_k=top_k)
        elif method == "dense":
            return self.search_dense(query, clean_roles, top_k=top_k)
        elif method == "graph":
            return self.search_graph(query, clean_roles, top_k=top_k)
        elif method == "hybrid":
            return self.search_hybrid(query, clean_roles, top_k=top_k, candidate_k=candidate_k)
        elif method in ("hybrid_rerank", "hybrid_reranker", "rerank"):
            return self.search_hybrid_rerank(query, clean_roles, top_k=top_k, candidate_k=candidate_k)
        else:
            raise ValueError(
                f"Phương thức '{method}' không hỗ trợ. Chọn: 'bm25', 'dense', 'graph', 'hybrid', 'hybrid_rerank'"
            )

    # ==========================================================================
    # 7. SECURE GRAPH CONTEXT & CITATION HINTS
    # ==========================================================================
    def get_secure_graph_hints(self, results: list[dict], user_roles: list[str]) -> list[dict]:
        """
        Trích xuất ngữ cảnh liên kết đồ thị (Prev/Next chunk, Mối quan hệ liên văn bản)
        đã được lọc quyền bảo mật để tránh rò rỉ thông tin qua đồ thị.
        """
        clean_roles = validate_roles(user_roles)
        user_roles_set = set(clean_roles)
        hints = []

        for r in results:
            cid = r["chunk_id"]
            doc_id = str(r["document_id"])
            source_file = r.get("source_file", doc_id)

            # Lấy các chunk trong cùng văn bản
            doc_chunks = self.df_chunks[self.df_chunks["document_id"].astype(str) == doc_id].reset_index(drop=True)
            chunk_indices = doc_chunks[doc_chunks["chunk_id"] == cid].index

            prev_id = "None"
            next_id = "None"

            if len(chunk_indices) > 0:
                idx = chunk_indices[0]
                # Kiểm tra chunk trước
                if idx > 0:
                    prev_row = doc_chunks.iloc[idx - 1]
                    prev_roles = prev_row["_allowed_roles_set"]
                    if prev_roles & user_roles_set:
                        prev_id = prev_row["chunk_id"]
                    else:
                        prev_id = "[Bị ẩn do không đủ quyền truy cập]"
                
                # Kiểm tra chunk sau
                if idx < len(doc_chunks) - 1:
                    next_row = doc_chunks.iloc[idx + 1]
                    next_roles = next_row["_allowed_roles_set"]
                    if next_roles & user_roles_set:
                        next_id = next_row["chunk_id"]
                    else:
                        next_id = "[Bị ẩn do không đủ quyền truy cập]"

            hints.append({
                "chunk_id": cid,
                "document_id": doc_id,
                "source_file": source_file,
                "prev_chunk_id": prev_id,
                "next_chunk_id": next_id,
                "user_roles": clean_roles
            })

        return hints
