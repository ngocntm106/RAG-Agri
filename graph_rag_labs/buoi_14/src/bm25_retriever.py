import re
import pandas as pd
from rank_bm25 import BM25Okapi
from src.citation import build_citation

def tokenize_legal_text(text: str) -> list[str]:
    """
    Tokenizer giữ lại:
    - Mã văn bản (vd: 73/2016/nđ-cp, 01/2014/tt-nhnn)
    - Ký tự số hiệu, điều khoản (vd: điều, khoản, chương, mục, số 1, 2...)
    - Các từ tiếng Việt thường
    """
    if not text or not isinstance(text, str):
        return []
    # Chuyển về chữ thường
    text = text.lower()
    # Tìm các chuỗi gồm từ ngữ, số, dấu gạch nối, gạch chéo
    tokens = re.findall(r'[\w/_\-\.]+', text)
    # Loại bỏ các dấu chấm đơn lẻ ở cuối token
    cleaned_tokens = [t.strip('.,:;!?()[]{}"\'') for t in tokens if t.strip('.,:;!?()[]{}"\'')]
    return cleaned_tokens

class BM25Retriever:
    def __init__(self, df_chunks: pd.DataFrame):
        """
        Khởi tạo BM25 index trên corpus đã chuẩn hóa.
        """
        self.df_chunks = df_chunks.copy().reset_index(drop=True)
        # Điền chuỗi rỗng nếu text bị null
        self.df_chunks['text'] = self.df_chunks['text'].fillna('')
        
        # Tokenize toàn bộ corpus
        self.corpus_tokens = [
            tokenize_legal_text(f"{row['text']} {row.get('article', '')} {row.get('source_file', '')}")
            for _, row in self.df_chunks.iterrows()
        ]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Thực hiện tìm kiếm theo BM25 và trả về danh sách theo schema chuẩn.
        """
        tokenized_query = tokenize_legal_text(query)
        if not tokenized_query:
            return []
            
        scores = self.bm25.get_scores(tokenized_query)
        # Lấy top_k index có score cao nhất
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
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
                "retrieval_method": "BM25",
                "citation": citation
            })
            
        return results
