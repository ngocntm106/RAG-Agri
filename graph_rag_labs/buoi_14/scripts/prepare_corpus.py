import os
import sys
import pandas as pd
from bs4 import BeautifulSoup

# Reconfigure output to utf-8 for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    if not text:
        return ""
    # Normalize whitespaces: replace multiple spaces/tabs with single space, strip
    cleaned = " ".join(text.strip().split())
    return cleaned

def parse_html_to_chunks(df_merged):
    chunks = []
    seen_chunk_ids = {}
    duplicate_count = 0
    empty_text_count = 0
    
    for _, row in df_merged.iterrows():
        doc_id = str(row['id'])
        so_ky_hieu = str(row['so_ky_hieu'])
        title = str(row['title'])
        doc_type = str(row['loai_van_ban'])
        effective_date = str(row['ngay_co_hieu_luc']) if pd.notna(row['ngay_co_hieu_luc']) else ""
        status = str(row['tinh_trang_hieu_luc']) if pd.notna(row['tinh_trang_hieu_luc']) else ""
        
        soup = BeautifulSoup(row['content_html'], 'html.parser')
        
        current_chapter = ""
        current_section = ""
        current_article = ""
        current_clause = ""
        
        # Traverse tags in the order they appear in the HTML
        for tag in soup.find_all(True):
            if not tag.has_attr('id'):
                continue
                
            cls = tag.get('class', [])
            if cls is None:
                cls = []
            elif isinstance(cls, str):
                cls = [cls]
                
            txt = clean_text(tag.get_text())
            
            # State machine to track hierarchy
            if 'prov-chapter' in cls:
                current_chapter = txt
                current_section = ""
                current_article = ""
                current_clause = ""
            elif 'prov-section' in cls:
                current_section = txt
                current_article = ""
                current_clause = ""
            elif 'prov-article' in cls:
                current_article = txt
                current_clause = ""
            elif 'prov-clause' in cls:
                current_clause = txt
                
            # Process chunk ID uniqueness
            raw_chunk_id = str(tag.get('id')).strip()
            if not raw_chunk_id:
                continue
                
            if raw_chunk_id in seen_chunk_ids:
                seen_chunk_ids[raw_chunk_id] += 1
                chunk_id = f"{raw_chunk_id}-{seen_chunk_ids[raw_chunk_id]}"
                duplicate_count += 1
            else:
                seen_chunk_ids[raw_chunk_id] = 0
                chunk_id = raw_chunk_id
                
            if not txt:
                empty_text_count += 1
                
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "text": txt,
                "source_file": so_ky_hieu,
                "title": title,
                "document_type": doc_type,
                "chapter": current_chapter,
                "section": current_section,
                "article": current_article,
                "clause": current_clause,
                "effective_date": effective_date,
                "status": status
            })
            
    return chunks, duplicate_count, empty_text_count

def main():
    print("=== CORPUS PREPARATION ===")
    
    # Path to source CSV files
    kb_path = os.path.join("..", "kb+hops")
    metadata_path = os.path.join(kb_path, "metadata.csv")
    content_path = os.path.join(kb_path, "content.csv")
    
    if not os.path.exists(metadata_path) or not os.path.exists(content_path):
        print("Error: Source data files not found in ../kb+hops/!")
        sys.exit(1)
        
    df_meta = pd.read_csv(metadata_path, encoding='utf-8')
    df_content = pd.read_csv(content_path, encoding='utf-8')
    
    print(f"Loaded {len(df_meta)} metadata records and {len(df_content)} content records.")
    
    # Merge metadata and content on id
    df_merged = pd.merge(df_meta, df_content, on='id')
    print(f"Merged records count: {len(df_merged)}")
    
    # Parse HTML to chunks
    chunks, duplicate_count, empty_text_count = parse_html_to_chunks(df_merged)
    
    df_chunks = pd.DataFrame(chunks)
    
    # Verify uniqueness of chunk_id
    is_unique = df_chunks['chunk_id'].is_unique
    print(f"Unique chunk_id verification: {is_unique}")
    
    # Ensure output directory exists
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "chunks_normalized.csv")
    
    # Save output
    df_chunks.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Normalized corpus saved to: {output_file}")
    
    # Print metrics
    total_docs = df_merged['id'].nunique()
    print("\nMETRICS:")
    print(f"- Total chunks: {len(df_chunks)}")
    print(f"- Total documents: {total_docs}")
    print(f"- Chunks with missing/empty text: {empty_text_count}")
    print(f"- Duplicate IDs resolved: {duplicate_count}")
    
    # Print 3 samples
    print("\nSAMPLE RECORDS (First 3):")
    samples = df_chunks.head(3)
    for idx, row in samples.iterrows():
        print(f"\nSample #{idx+1}:")
        print(f"  Chunk ID: {row['chunk_id']}")
        print(f"  Doc ID: {row['document_id']}")
        print(f"  Source File: {row['source_file']}")
        print(f"  Chapter: {row['chapter']}")
        print(f"  Section: {row['section']}")
        print(f"  Article: {row['article']}")
        print(f"  Clause: {row['clause']}")
        print(f"  Text: {row['text'][:200]}...")

if __name__ == "__main__":
    main()
