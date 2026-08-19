# Buổi 08: Advanced RAG System & Evaluation Engine

Hệ thống RAG nâng cao kết hợp **BM25 Keyword Search**, **Gemini Vector Search**, **Reciprocal Rank Fusion (RRF)** và **Cross-Encoder Reranker** (`BAAI/bge-reranker-v2-m3`), đối chứng trực tiếp với **Baseline Semantic RAG** của Buổi 07.

---

## 1. Mục tiêu và khác biệt chính giữa Buổi 07 & Buổi 08

| Đặc điểm | Buổi 07 (Baseline RAG) | Buổi 08 (Advanced RAG) |
|---|---|---|
| **Retrieval Architecture** | Đơn tầng: Semantic (Vector distance) | Multi-stage: BM25 + Semantic → RRF Fusion → Cross-Encoder Rerank |
| **Từ khóa viết tắt & Số hiệu** | Dễ bị trượt nếu embedding không bao quát | BM25 đảm bảo tìm chính xác từ khóa, số Điều/Khoản |
| **Xếp hạng ứng viên** | Theo khoảng cách cosine/L2 | RRF kết hợp thứ hạng + Cross-Encoder tính tương quan ngữ cảnh sâu |
| **Pipeline Trace** | Chỉ hiển thị kết quả cuối | Cho phép theo dõi từng tầng candidate, rank movement & latency |
| **Đánh giá tự động** | Không có hoặc kiểm thử thủ công | Engine đánh giá offline Recall@K, MRR@K, nDCG@K & Latency |

---

## 2. Sơ đồ Kiến trúc Pipeline Nhiều Tầng

```mermaid
flowgraph TD
    Q[User Question] --> BM25[BM25 Keyword Search]
    Q --> SEM[Gemini Vector Search]
    
    BM25 -->|Top BM25 Candidates| RRF[Reciprocal Rank Fusion]
    SEM -->|Top Semantic Candidates| RRF
    
    RRF -->|Fused Top Candidates| RERANK[Cross-Encoder Reranker]
    RERANK -->|Final Top-K Contexts| GATE[Confidence Gate / Filter]
    
    GATE -->|Passed Contexts| LLM[Gemini Generation LLM]
    LLM --> ANS[Final Answer & Citations]
```

---

## 3. Cấu trúc Project

```
rag_foundation/buoi_08/
├── rag.py                       # Baseline Semantic RAG (chỉ dùng public APIs)
├── advanced_rag.py              # Advanced RAG Logic (BM25, RRF, Reranker)
├── evaluate.py                  # Evaluation Engine (Recall@K, MRR@K, nDCG@K, Latency)
├── app.py                       # Dashboard Streamlit 4 Tab
├── requirements.txt             # Danh sách thư viện phụ thuộc
├── .env.example                 # Mẫu cấu hình môi trường
├── eval/
│   └── questions.json           # Bộ câu hỏi test & gold labels
├── tests/
│   ├── test_tokenizer_bm25.py   # Test BM25 & Tokenizer
│   ├── test_semantic_retrieval.py# Test Vector Search
│   ├── test_rrf_fusion.py       # Test RRF Logic
│   ├── test_reranker.py         # Test Cross-Encoder Reranker
│   ├── test_advanced_answer.py  # Test pipeline answer, trace & UI helpers
│   └── fixtures/
├── reports/                     # Lưu báo cáo đánh giá tự động (JSON)
└── storage/                     # Nơi lưu trữ ChromaDB vector store
```

---

## 4. Setup `.venv`, requirements và `.env`

### Bước 1: Tạo và kích hoạt môi trường ảo
```bash
python -m venv .venv
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
source .venv/bin/activate
```

### Bước 2: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình biến môi trường
Tạo file `.env` từ file `.env.example`:
```ini
GEMINI_API_KEY=your_api_key_here
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
GEMINI_GENERATION_MODEL=gemini-3.5-flash-lite
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
RERANK_DEVICE=auto
```

---

## 5. Cảnh báo Kích thước & Tài nguyên Reranker Model

> [!WARNING]
> Model Cross-Encoder `BAAI/bge-reranker-v2-m3` có kích thước xấp xỉ **2.2 GB**.
> - Lần đầu tiên khởi chạy `hybrid_rerank` hoặc gọi load model, hệ thống sẽ tự động tải weights từ HuggingFace Hub.
> - **Yêu cầu phần cứng**: Tối thiểu **4 GB RAM rảnh** (hoặc GPU VRAM > 2 GB nếu dùng CUDA).
> - Nếu môi trường không đủ tài nguyên hoặc không có kết nối Internet để tải weights, pipeline sẽ đánh dấu `NOT RUN` hoặc ghi nhận status `reranker_unavailable` mà không làm sập ứng dụng.

---

## 6. Các Lệnh CLI chính

### Kiểm tra trạng thái hệ thống (Read-only)
```bash
python advanced_rag.py status
```

### Lập chỉ mục Vector (Prepare Semantic Index)
```bash
python advanced_rag.py prepare-semantic --strategy hierarchical
```

### Tìm kiếm BM25 đơn lẻ
```bash
python advanced_rag.py bm25 "Điều 7 quy định cơ cấu lại thời hạn trả nợ"
```

### Tìm kiếm Hybrid (BM25 + Semantic + RRF)
```bash
python advanced_rag.py hybrid "Điều 7 quy định cơ cấu lại thời hạn trả nợ"
```

### Tìm kiếm Hybrid + Rerank
```bash
python advanced_rag.py rerank "Điều 7 quy định cơ cấu lại thời hạn trả nợ"
```

### Trả lời câu hỏi đầy đủ (Answer Generation)
```bash
python advanced_rag.py query "Điều 7 quy định cơ cấu lại thời hạn trả nợ" --mode hybrid_rerank
```

### So sánh các Mode Retrieval
```bash
python advanced_rag.py compare "Điều 7 quy định cơ cấu lại thời hạn trả nợ"
```

---

## 7. Kiểm thử, Đánh giá & Khởi chạy Streamlit UI

### Chạy toàn bộ Unit Tests (100% Offline)
```bash
python -m unittest discover -s tests
```

### Chạy Engine Đánh giá Metric Offline
```bash
python evaluate.py --strategy hierarchical --k 5
```

### Khởi chạy Giao diện Streamlit Dashboard
```bash
python -m streamlit run app.py
```

---

## 8. Giải thích các Điểm số RAG

1. **BM25 Score**: Điểm tần suất từ khóa điều chỉnh theo độ dài văn bản (Okapi BM25). Điểm càng cao thể hiện mức độ khớp từ khóa càng lớn.
2. **Cosine Distance**: Khoảng cách ngữ nghĩa trong không gian vector (0.0 đến 2.0). Giá trị càng nhỏ thể hiện mức độ tương đồng ngữ nghĩa càng cao.
3. **RRF Score**: Điểm kết hợp vị thứ thứ hạng: 
   $$RRF\_Score = \frac{w_{bm25}}{k + rank_{bm25}} + \frac{w_{sem}}{k + rank_{sem}}$$
4. **Rerank Score**: Điểm số tương quan ngữ cảnh sâu do mô hình Cross-Encoder đánh giá (sau khi qua hàm Sigmoid chuẩn hóa về khoảng $[0.0, 1.0]$).

---

## 9. Phân biệt Candidate K và Final K

- **BM25 Candidate K ($K_{bm25}$)**: Số lượng đoạn văn bản tối đa lấy ra từ tầng tìm kiếm BM25.
- **Semantic Candidate K ($K_{sem}$)**: Số lượng đoạn văn bản tối đa lấy ra từ tầng Vector Search.
- **Rerank Candidate K ($K_{rrf}$)**: Số lượng ứng viên hợp nhất sau RRF truyền vào cho Reranker.
- **Final Top-K ($K_{final}$)**: Số lượng đoạn văn bản tốt nhất cuối cùng được giữ lại để đưa vào Prompt cho LLM sinh câu trả lời.

---

## 10. Evaluation Metrics & Giới hạn Gold Labels

- **Recall@K**: Tỷ lệ tìm thấy ít nhất 1 chunk đúng trong Top-K kết quả.
- **MRR@K (Mean Reciprocal Rank)**: Điểm vị trí xuất hiện của chunk đúng đầu tiên ($\frac{1}{rank}$).
- **nDCG@K (Normalized Discounted Cumulative Gain)**: Đánh giá chất lượng xếp hạng có tính đến vị trí xuất hiện của các chunk liên quan.

> [!IMPORTANT]
> Tất cả nhãn trong `eval/questions.json` có `needs_human_review=true`. Kết quả đánh giá chỉ mang tính chất baseline thử nghiệm và **không tuyên bố mode thắng chính thức** cho đến khi có xác nhận của chuyên gia pháp lý.

---

## 11. Xử lý Lỗi thường gặp (Troubleshooting)

1. **Không tải được mô hình Reranker**: Kiểm tra kết nối mạng hoặc đặt `RERANK_DEVICE=cpu` trong `.env`.
2. **Quá tải Memory / CPU**: Giảm `BM25_CANDIDATES` và `RERANK_CANDIDATES` xuống `10` hoặc `5`.
3. **Thiếu API Key**: Đảm bảo file `.env` đã khai báo `GEMINI_API_KEY`. Nếu thiếu API Key, hệ thống tự động chuyển sang chế độ `retrieval_only`.

---

## 12. Tuyên bố Khuyến cáo

> [!CAUTION]
> Sản phẩm này phục vụ mục đích nghiên cứu và học tập học thuật RAG. Kết quả tra cứu **không có giá trị pháp lý chính thức** và không thể thay thế văn bản quy phạm pháp luật hoặc tư vấn chuyên môn từ luật sư/chuyên gia tài chính.
