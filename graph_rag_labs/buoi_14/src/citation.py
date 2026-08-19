import pandas as pd

def build_citation(record: dict | pd.Series) -> str:
    """
    Tạo chuỗi citation chuẩn từ metadata của chunk:
    Định dạng: [<source_file/title> | <article/section/clause> | <chunk_id>]
    Không bịa metadata, chỉ dùng thông tin thực tế có trong record.
    """
    source = record.get("source_file") or record.get("title") or "Văn bản"
    chunk_id = record.get("chunk_id", "")
    
    article = record.get("article")
    clause = record.get("clause")
    chapter = record.get("chapter")
    section = record.get("section")
    
    loc_parts = []
    if article and pd.notna(article) and str(article).strip():
        loc_parts.append(str(article).strip())
    elif section and pd.notna(section) and str(section).strip():
        loc_parts.append(str(section).strip())
    elif chapter and pd.notna(chapter) and str(chapter).strip():
        loc_parts.append(str(chapter).strip())
    elif clause and pd.notna(clause) and str(clause).strip():
        loc_parts.append(str(clause).strip()[:50])
        
    if loc_parts:
        return f"[{source} | {' - '.join(loc_parts)} | {chunk_id}]"
    else:
        return f"[{source} | {chunk_id}]"
