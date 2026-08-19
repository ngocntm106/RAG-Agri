"""Logic RAG đơn giản cho buổi 06.

- Đọc JSON chunk từ buổi 05
- Tạo embedding bằng Gemini (384 chiều)
- Lưu vào PostgreSQL nếu có, otherwise local SQLite
- Lưu embedding vào ChromaDB
- Hỗ trợ retrieval và trả lời câu hỏi
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import sqlite3
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

HERE = os.path.dirname(__file__)
BUOI05_CHUNKS = os.path.abspath(os.path.join(HERE, "..", "buoi_05", "output", "chunks"))
DB_PATH = os.path.join(HERE, "buoi_06_local.db")
CHROMA_DIR = os.path.join(HERE, "storage", "chroma")
COLLECTION_NAME = "buoi_06_collection"
EMBED_DIM = 384
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _deterministic_embedding(text: str, dim: int = EMBED_DIM) -> List[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [((digest[i % len(digest)] / 255.0) * 2) - 1 for i in range(dim)]


def _get_storage_connection() -> tuple[Any, bool]:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "rag_db")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")

    try:
        import psycopg

        conn = psycopg.connect(host=host, port=int(port), dbname="postgres", user=user, password=password)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
        cur.close()
        conn.close()
        conn = psycopg.connect(host=host, port=int(port), dbname=db_name, user=user, password=password)
        conn.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, source TEXT, text TEXT)")
        conn.commit()
        return conn, True
    except Exception:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, source TEXT, text TEXT)")
        conn.commit()
        return conn, False


def _get_collection() -> Any:
    try:
        from chromadb import PersistentClient

        client = PersistentClient(path=CHROMA_DIR)
        try:
            return client.get_collection(name=COLLECTION_NAME)
        except Exception:
            return client.create_collection(name=COLLECTION_NAME)
    except Exception:
        return None


def _embed_text(text: str) -> List[float]:
    if GEMINI_API_KEY:
        try:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.embed_content(model="gemini-embedding-2", contents=text)
            embeddings = getattr(response, "embeddings", None)
            values = getattr(embeddings[0], "values", None) if embeddings else None
            if values:
                return list(values)[:EMBED_DIM]
        except Exception:
            pass
    return _deterministic_embedding(text)


def index() -> int:
    files = sorted(glob.glob(os.path.join(BUOI05_CHUNKS, "*.json")))
    conn, _ = _get_storage_connection()
    collection = _get_collection()
    count = 0

    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            continue

        items = payload if isinstance(payload, list) else [payload]
        for idx, item in enumerate(items):
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("chunk") or ""
            else:
                text = str(item)
            if not text:
                continue

            doc_id = f"{os.path.basename(path)}::{idx}"
            conn.execute(
                "INSERT OR REPLACE INTO documents (id, source, text) VALUES (?, ?, ?)",
                (doc_id, os.path.basename(path), text),
            )
            embedding = _embed_text(text)
            if collection is not None:
                try:
                    collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        metadatas=[{"source": os.path.basename(path)}],
                        documents=[text],
                    )
                except Exception:
                    pass
            count += 1

    conn.commit()
    conn.close()
    return count


def retrieve(question: str, k: int = 5) -> List[Dict[str, Any]]:
    if not question.strip():
        return []

    conn, _ = _get_storage_connection()
    collection = _get_collection()
    results: List[Dict[str, Any]] = []

    if collection is not None:
        try:
            embedding = _embed_text(question)
            query_result = collection.query(query_embeddings=[embedding], n_results=k)
            ids = query_result.get("ids", [])
            if ids:
                first_ids = ids[0] if isinstance(ids[0], list) else ids
                for doc_id in first_ids:
                    row = conn.execute("SELECT source, text FROM documents WHERE id = ?", (doc_id,)).fetchone()
                    if row:
                        results.append({"id": doc_id, "source": row[0], "text": row[1]})
        except Exception:
            pass

    if not results:
        needle = question.lower()
        for row in conn.execute("SELECT id, source, text FROM documents"):
            if needle in row[2].lower():
                results.append({"id": row[0], "source": row[1], "text": row[2]})

    conn.close()
    return results[:k]


def ask(question: str, k: int = 5) -> str:
    docs = retrieve(question, k)
    if not docs:
        return "Không tìm thấy dữ liệu phù hợp."

    context = "\n\n".join(doc["text"][:1200] for doc in docs)
    if GEMINI_API_KEY:
        try:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = (
                "Dựa trên ngữ cảnh sau, trả lời câu hỏi ngắn gọn và chính xác.\n\n"
                f"Ngữ cảnh:\n{context}\n\nCâu hỏi:\n{question}\n\nTrả lời:"
            )
            response = client.models.generate_content(model="gemini-flash-litelatest", contents=prompt)
            text = getattr(response, "text", None)
            if text:
                return text
        except Exception:
            pass

    return "\n\n".join(f"[{doc['source']}] {doc['text'][:800]}" for doc in docs)


def answer(question: str, k: int = 5) -> str:
    return ask(question, k)


def status() -> Dict[str, int]:
    conn, _ = _get_storage_connection()
    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    conn.close()

    collection = _get_collection()
    chunk_count = 0
    if collection is not None:
        try:
            chunk_count = int(collection.count())
        except Exception:
            chunk_count = 0

    return {"documents": int(doc_count), "chunks": int(chunk_count)}

