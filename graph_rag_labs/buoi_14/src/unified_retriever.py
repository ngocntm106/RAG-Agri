import os
import pandas as pd
from dotenv import load_dotenv

from src.bm25_retriever import BM25Retriever
from src.dense_retriever import DenseRetriever
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker

class UnifiedRetriever:
    def __init__(
        self,
        corpus_path: str = os.path.join("data", "processed", "chunks_normalized.csv"),
        rel_path: str = os.path.join("..", "kb+hops", "relationships.csv"),
        meta_path: str = os.path.join("..", "kb+hops", "metadata.csv")
    ):
        """
        Hệ thống Retrieval thống nhất tích hợp BM25, Dense, Hybrid (RRF), Reranker và Graph Hints.
        """
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"Không tìm thấy file corpus tại {corpus_path}")

        print(f"[UnifiedRetriever] Đang nạp dữ liệu corpus từ {corpus_path}...")
        self.df_chunks = pd.read_csv(corpus_path, encoding='utf-8')
        
        self.df_rel = pd.read_csv(rel_path, encoding='utf-8') if os.path.exists(rel_path) else pd.DataFrame()
        self.df_meta = pd.read_csv(meta_path, encoding='utf-8') if os.path.exists(meta_path) else pd.DataFrame()

        # Ánh xạ document_id -> source_file/title để tra cứu nhanh
        self.meta_map = {}
        if not self.df_meta.empty:
            for _, row in self.df_meta.iterrows():
                self.meta_map[str(row['id'])] = {
                    "source_file": str(row.get('so_ky_hieu', row['id'])),
                    "title": str(row.get('title', ''))
                }

        # Khởi tạo các retrieval modules
        self.bm25 = BM25Retriever(self.df_chunks)
        self.dense = DenseRetriever(self.df_chunks)
        self.hybrid = HybridRetriever(bm25_retriever=self.bm25, dense_retriever=self.dense)
        self._reranker = None

        # Khởi tạo kết nối Neo4j (nếu có)
        load_dotenv()
        self.neo4j_driver = None
        self.neo4j_db = os.getenv("NEO4J_DATABASE", "neo4j")
        self._init_neo4j()

    def _init_neo4j(self):
        try:
            from neo4j import GraphDatabase
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session(database=self.neo4j_db) as session:
                res = session.run("RETURN 1 AS connected")
                if res.single() and res.single()["connected"] == 1:
                    self.neo4j_driver = driver
        except Exception:
            self.neo4j_driver = None

    @property
    def reranker(self):
        if self._reranker is None:
            self._reranker = Reranker()
        return self._reranker

    def retrieve(
        self, 
        question: str, 
        method: str = "hybrid_rerank", 
        top_k: int = 5, 
        candidate_k: int = 20
    ) -> list[dict]:
        """
        Hàm retrieval thống nhất.
        
        Args:
            question: Câu hỏi cần tìm kiếm
            method: 'bm25' | 'dense' | 'hybrid' | 'hybrid_rerank'
            top_k: Số lượng kết quả cuối cùng
            candidate_k: Số lượng candidate đưa vào RRF / Reranker
        """
        method = method.lower().strip()
        if not question or not question.strip():
            return []

        results = []
        if method == "bm25":
            raw_res = self.bm25.search(question, top_k=top_k)
            for r in raw_res:
                results.append({
                    "rank": r["rank"],
                    "chunk_id": r["chunk_id"],
                    "document_id": str(r["document_id"]),
                    "text": r["text"],
                    "score": round(float(r["retrieval_score"]), 4),
                    "citation": r["citation"],
                    "retrieval_method": "BM25",
                    "hybrid_score": None,
                    "rerank_score": None
                })

        elif method == "dense":
            raw_res = self.dense.search(question, top_k=top_k)
            for r in raw_res:
                results.append({
                    "rank": r["rank"],
                    "chunk_id": r["chunk_id"],
                    "document_id": str(r["document_id"]),
                    "text": r["text"],
                    "score": round(float(r["retrieval_score"]), 4),
                    "citation": r["citation"],
                    "retrieval_method": "Dense",
                    "hybrid_score": None,
                    "rerank_score": None
                })

        elif method == "hybrid":
            raw_res = self.hybrid.search(question, top_k=top_k, candidate_k=candidate_k)
            for r in raw_res:
                results.append({
                    "rank": r["final_rank"],
                    "chunk_id": r["chunk_id"],
                    "document_id": str(r["document_id"]),
                    "text": r["text"],
                    "score": round(float(r["rrf_score"]), 6),
                    "citation": r["citation"],
                    "retrieval_method": "Hybrid (RRF)",
                    "hybrid_score": round(float(r["rrf_score"]), 6),
                    "rerank_score": None
                })

        elif method == "hybrid_rerank":
            candidates = self.hybrid.search(question, top_k=candidate_k, candidate_k=candidate_k)
            raw_res = self.reranker.rerank(question, candidates, top_k=top_k)
            for r in raw_res:
                results.append({
                    "rank": r["final_rank"],
                    "chunk_id": r["chunk_id"],
                    "document_id": str(r["document_id"]),
                    "text": r["text"],
                    "score": round(float(r["rerank_score"]), 4),
                    "citation": r["citation"],
                    "retrieval_method": r.get("retrieval_method", "Hybrid + Rerank"),
                    "hybrid_score": round(float(r["hybrid_score"]), 6) if r.get("hybrid_score") is not None else None,
                    "rerank_score": round(float(r["rerank_score"]), 4)
                })

        else:
            raise ValueError(f"Method '{method}' không hợp lệ! Chọn: 'bm25', 'dense', 'hybrid', hoặc 'hybrid_rerank'")

        return results

    def get_graph_hints(self, results: list[dict]) -> list[dict]:
        """
        Trích xuất thông tin ngữ cảnh đồ thị 1-hop (Prev/Next chunk, Document Relations).
        Nếu Neo4j sẵn sàng sẽ query Neo4j; nếu không sẽ tra cứu an toàn từ DataFrame.
        """
        hints = []
        
        # Thử lấy từ Neo4j nếu driver kết nối được
        if self.neo4j_driver is not None:
            try:
                with self.neo4j_driver.session(database=self.neo4j_db) as session:
                    for r in results:
                        cid = r["chunk_id"]
                        doc_id = str(r["document_id"])
                        cypher_query = """
                        MATCH (d:DieuKhoan {id: $cid, lab_session: 'buoi_14'})
                        OPTIONAL MATCH (prev:DieuKhoan)-[:NEXT]->(d)
                        OPTIONAL MATCH (d)-[:NEXT]->(next:DieuKhoan)
                        OPTIONAL MATCH (v:VanBan {id: $doc_id})-[rel:SUA_DOI_BO_SUNG|CAN_CU|VAN_BAN_BO_SUNG|THAY_THE|HOP_NHAT]->(other:VanBan)
                        RETURN 
                            prev.id AS prev_id, 
                            next.id AS next_id,
                            collect({type: type(rel), target: other.source_file, desc: rel.relationship}) AS relations
                        """
                        record = session.run(cypher_query, cid=cid, doc_id=doc_id).single()
                        doc_info = self.meta_map.get(doc_id, {"source_file": doc_id, "title": ""})
                        hints.append({
                            "chunk_id": cid,
                            "document_id": doc_id,
                            "source_file": doc_info["source_file"],
                            "prev_chunk_id": record["prev_id"] if record and record["prev_id"] else "None",
                            "next_chunk_id": record["next_id"] if record and record["next_id"] else "None",
                            "document_relations": record["relations"] if record and record["relations"] else [],
                            "graph_source": "Neo4j Knowledge Graph"
                        })
                return hints
            except Exception:
                pass # Fallback to local dataframe

        # Fallback tra cứu bằng DataFrames
        for r in results:
            cid = r["chunk_id"]
            doc_id = str(r["document_id"])
            doc_info = self.meta_map.get(doc_id, {"source_file": doc_id, "title": ""})
            
            # Tìm chunk liền trước & liền sau trong cùng văn bản
            doc_chunks = self.df_chunks[self.df_chunks['document_id'].astype(str) == doc_id].reset_index(drop=True)
            chunk_indices = doc_chunks[doc_chunks['chunk_id'] == cid].index
            
            prev_id = "None"
            next_id = "None"
            if len(chunk_indices) > 0:
                idx = chunk_indices[0]
                if idx > 0:
                    prev_id = doc_chunks.iloc[idx - 1]['chunk_id']
                if idx < len(doc_chunks) - 1:
                    next_id = doc_chunks.iloc[idx + 1]['chunk_id']

            # Tìm quan hệ liên văn bản (cả 2 chiều)
            doc_rels = []
            if not self.df_rel.empty:
                # Chiều đi: doc_id -> other_doc_id
                outgoing = self.df_rel[self.df_rel['doc_id'].astype(str) == doc_id]
                for _, rel_row in outgoing.iterrows():
                    other_id = str(rel_row['other_doc_id'])
                    other_info = self.meta_map.get(other_id, {"source_file": other_id})
                    doc_rels.append({
                        "type": rel_row.get('relationship_type', 'RELATION'),
                        "target": other_info.get("source_file", other_id),
                        "direction": "OUTGOING",
                        "desc": rel_row.get('relationship', '')
                    })
                # Chiều đến: other_doc_id -> doc_id
                incoming = self.df_rel[self.df_rel['other_doc_id'].astype(str) == doc_id]
                for _, rel_row in incoming.iterrows():
                    src_id = str(rel_row['doc_id'])
                    src_info = self.meta_map.get(src_id, {"source_file": src_id})
                    doc_rels.append({
                        "type": rel_row.get('relationship_type', 'RELATION'),
                        "target": src_info.get("source_file", src_id),
                        "direction": "INCOMING",
                        "desc": f"Được liên kết từ {src_info.get('source_file', src_id)}: {rel_row.get('relationship', '')}"
                    })

            hints.append({
                "chunk_id": cid,
                "document_id": doc_id,
                "source_file": doc_info["source_file"],
                "prev_chunk_id": prev_id,
                "next_chunk_id": next_id,
                "document_relations": doc_rels,
                "graph_source": "Local Relational Cache"
            })

        return hints
