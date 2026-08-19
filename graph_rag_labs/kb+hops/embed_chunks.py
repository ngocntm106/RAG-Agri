import os
import json
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np
import sys

# Configure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

# Paths
WORKSPACE_DIR = r"c:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\kb+hops"
INPUT_JSON = os.path.join(WORKSPACE_DIR, "chunks.json")
OUTPUT_JSON = os.path.join(WORKSPACE_DIR, "chunks_with_embeddings.json")

def mean_pooling(model_output, attention_mask):
    """
    Mean Pooling - Take attention mask into account for correct averaging.
    """
    token_embeddings = model_output[0] # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def main():
    print("Đang đọc tệp chunks.json...")
    if not os.path.exists(INPUT_JSON):
        print(f"Lỗi: Không tìm thấy tệp {INPUT_JSON}. Hãy chắc chắn đã chạy Bước 1 trước.")
        return
        
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    print(f"Tổng số phân đoạn cần nhúng: {len(chunks)}")
    
    # Filter content to embed
    # Ensure we use empty string fallback if content is None
    contents = [c.get('content', '') or '' for c in chunks]
    
    # Load HuggingFace model and tokenizer
    model_name = "thuannc/vi-distilled-msmarco-MiniLM-L12-cos-v5"
    print(f"Đang tải mô hình nhúng: {model_name}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Ensure running strictly on CPU
    device = torch.device('cpu')
    model.to(device)
    model.eval()
    
    print("Bắt đầu tạo vector nhúng (Embedding) trên CPU...")
    batch_size = 32
    embeddings = []
    
    for i in range(0, len(contents), batch_size):
        batch_texts = contents[i:i+batch_size]
        
        # Tokenize batch
        encoded_input = tokenizer(
            batch_texts, 
            padding=True, 
            truncation=True, 
            max_length=512, 
            return_tensors='pt'
        )
        
        # Move inputs to CPU device
        encoded_input = {k: v.to(device) for k, v in encoded_input.items()}
        
        with torch.no_grad():
            model_output = model(**encoded_input)
            
        # Perform mean pooling
        batch_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
        
        # Normalize embeddings to unit length (L2 norm)
        batch_embeddings = F.normalize(batch_embeddings, p=2, dim=1)
        
        # Append embeddings
        embeddings.extend(batch_embeddings.numpy().tolist())
        
        print(f"  Đã xử lý {min(i + batch_size, len(contents))}/{len(contents)} phân đoạn...")
        
    # Append embedding vector to each chunk object
    for idx, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[idx]
        
    # Save back to JSON
    print(f"Đang lưu các phân đoạn kèm vector nhúng vào tệp: {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
        
    # Print validation information
    print("\n" + "="*80)
    print("XÁC MINH VÀ KIỂM TRA ĐẦU RA VECTOR NHÚNG (EMBEDDING):")
    print("="*80)
    print(f"Kích thước tệp đầu ra: {len(chunks)} phân đoạn.")
    
    # Check dimensions
    emb_dim = len(chunks[0]['embedding'])
    print(f"Kích thước Vector Nhúng (Embedding Dimensions): {emb_dim} (Kỳ vọng: 384)")
    
    # Check for NaN / Null values
    has_nan_or_null = False
    for idx, c in enumerate(chunks):
        emb = c['embedding']
        if emb is None or len(emb) != 384 or any(np.isnan(x) for x in emb):
            has_nan_or_null = True
            print(f"  Cảnh báo: Phân đoạn {c['id']} tại chỉ mục {idx} bị lỗi vector nhúng!")
            break
            
    if not has_nan_or_null:
        print("Trạng thái: Tất cả các vector nhúng đều đầy đủ, không có NaN/Null và đạt kích thước 384.")
    else:
        print("Trạng thái: Có lỗi xảy ra trong quá trình nhúng dữ liệu!")
        
    print("\nMẫu vector nhúng của phân đoạn đầu tiên:")
    first_chunk_text = chunks[0]['content']
    print(f"  ID: {chunks[0]['id']}")
    print(f"  Nội dung: {first_chunk_text[:120]}...")
    print(f"  Vector nhúng (10 phần tử đầu tiên): {chunks[0]['embedding'][:10]}")
    
if __name__ == "__main__":
    main()
