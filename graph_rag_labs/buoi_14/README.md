# Buổi 14: Hybrid Search + Reranking + Mini Knowledge Graph

Thư mục này chứa toàn bộ mã nguồn, cấu hình, dữ liệu chuẩn hóa và kết quả thực hành của **Buổi 14: Hệ thống RAG nâng cao kết hợp Lexical/Dense Search, Reranker và Đồ thị tri thức (Mini Knowledge Graph)**.

---

## 1. Thiết lập môi trường

### Bước 1: Tạo môi trường ảo (Virtual Environment)
Nếu chưa có thư mục `.venv`, khởi tạo môi trường ảo bằng lệnh sau:
```bash
python -m venv .venv
```

### Bước 2: Kích hoạt môi trường ảo
- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### Bước 3: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

---

## 2. Chuẩn hóa Corpus dữ liệu nguồn

Dữ liệu nguồn được đọc trực tiếp từ thư mục `../kb+hops/` bao gồm:
- `metadata.csv` (Thông tin văn bản)
- `content.csv` (Nội dung văn bản dạng HTML)
- `relationships.csv` (Mối quan hệ giữa các văn bản)

Lưu ý: **Tuyệt đối không chỉnh sửa dữ liệu gốc trong `../kb+hops/`**.

### Hướng dẫn chạy chuẩn hóa dữ liệu:
Chạy script `prepare_corpus.py` để bóc tách nội dung HTML phân cấp và liên kết thông tin metadata:
```bash
python scripts/prepare_corpus.py
```

### Kết quả đầu ra:
Dữ liệu corpus chuẩn hóa dạng bảng được tạo tại:
- `data/processed/chunks_normalized.csv` (6,593 chunks duy nhất từ 15 văn bản pháp lý).

---

## 3. Chạy Baseline Retrieval (BM25 & Dense Search)

Chúng ta xây dựng 2 phương pháp tìm kiếm độc lập:
1. **BM25 Retriever (`src/bm25_retriever.py`)**: Tìm kiếm từ khóa chính xác (lexical matching).
2. **Dense Retriever (`src/dense_retriever.py`)**: Tìm kiếm ngữ nghĩa (semantic embedding) với SentenceTransformers và tự động lưu cache vector vào `cache/dense_embeddings.npy`.

### Lệnh chạy truy vấn đơn lẻ:
```bash
python scripts/baseline_retrieval.py --query "Thông tư số 01/2014/TT-NHNN Điều 4 quy định đóng gói niêm phong tiền mặt" --top-k 5
```

---

## 4. Chạy Hybrid Search (Reciprocal Rank Fusion - RRF)

**Hybrid Retriever (`src/hybrid_retriever.py`)** kết hợp kết quả từ BM25 ($N$ ứng viên) và Dense Retrieval ($N$ ứng viên) theo công thức Reciprocal Rank Fusion:

$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{BM25}, \text{Dense}\}} \frac{1}{60 + \text{rank}_m(d)}$$

### Lệnh chạy truy vấn Hybrid Search:
```bash
python scripts/hybrid_search.py --query "Quy định về giao nhận vận chuyển tiền mặt trong ngành Ngân hàng" --candidate-k 20 --top-k 5
```

---

## 5. Chạy Tầng Reranking sau Hybrid Search

**Reranker (`src/reranker.py`)** sử dụng mô hình Cross-Encoder đa ngôn ngữ `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` để đánh giá trực tiếp độ tương quan ngữ nghĩa sâu giữa `(Query, Candidate Text)`.

### Lệnh chạy pipeline Hybrid -> Rerank:
```bash
python scripts/rerank.py --query "Ai có thẩm quyền phê duyệt việc mở chi nhánh ngân hàng nước ngoài?" --candidate-k 20 --top-k 5
```

---

## 6. Đánh giá Định lượng Retrieval (Evaluation Protocol)

Đo lường định lượng các chỉ số **Hit@1, Hit@3, Hit@5 và MRR** trên bộ câu hỏi vàng `data/eval/questions.csv` cho cả 4 cấu hình tìm kiếm:
```bash
python scripts/compare_retrieval.py
```

Kết quả chi tiết được lưu tại:
- `outputs/retrieval_comparison.csv`
- `outputs/evaluation_report.md`

---

## 7. Xây dựng Mini Knowledge Graph với Neo4j

Ontology đồ thị bao gồm:
- **Node**: `(:VanBan)`, `(:DieuKhoan)`
- **Relationships**:
  - `(:VanBan)-[:CONTAINS]->(:DieuKhoan)`
  - `(:DieuKhoan)-[:NEXT]->(:DieuKhoan)` (chuỗi thứ tự điều khoản)
  - Quan hệ liên văn bản từ dữ liệu: `SUA_DOI_BO_SUNG`, `CAN_CU`, `VAN_BAN_BO_SUNG`, `THAY_THE`, `HOP_NHAT`.

### Hướng dẫn nạp đồ thị:
1. Cấu hình file `buoi_14/.env` (tham khảo `.env.example`).
2. Chạy script nạp dữ liệu:
   ```bash
   python scripts/load_mini_kg.py
   ```

---

## 8. Hệ Thống Retrieval Thống Nhất & Graph Hints

Module [src/unified_retriever.py](file:///c:/Users/minhn/OneDrive/Desktop/H%E1%BB%8Dc%20AI/RAG/graph_rag_labs/buoi_14/src/unified_retriever.py) cung cấp hàm thống nhất:
```python
results = retriever.retrieve(question="...", method="hybrid_rerank", top_k=5)
hints = retriever.get_graph_hints(results)
```

### Chạy CLI truy vấn mẫu kèm Graph Hints:
```bash
python scripts/query_demo.py --query "Điều kiện thành lập doanh nghiệp bảo hiểm theo Nghị định 73/2016/NĐ-CP" --method hybrid_rerank --top-k 3
```

---

## 9. Khởi chạy Giao diện Trực quan Streamlit (Web Demo)

Ứng dụng web trực quan [app.py](file:///c:/Users/minhn/OneDrive/Desktop/H%E1%BB%8Dc%20AI/RAG/graph_rag_labs/buoi_14/app.py) cung cấp bảng điều khiển tìm kiếm hoàn chỉnh.

### Hướng dẫn khởi chạy:
```bash
streamlit run app.py
```
*(Nếu cổng mặc định 8501 bận, Streamlit sẽ tự động chọn cổng khả dụng tiếp theo ví dụ `http://localhost:8504`).*

### Cách dừng ứng dụng:
- Bấm tổ hợp phím `Ctrl + C` tại cửa sổ Terminal đang chạy Streamlit.

### Hướng dẫn sử dụng giao diện:
1. **Lựa chọn phương pháp tìm kiếm (Method)** tại thanh bên trái:
   - **BM25**: Tìm kiếm theo từ khóa chính xác.
   - **Dense**: Tìm kiếm theo tương đồng ngữ nghĩa vector.
   - **Hybrid**: Kết hợp BM25 + Dense bằng Reciprocal Rank Fusion (RRF).
   - **Hybrid + Rerank**: Lọc top ứng viên qua Hybrid rồi tái sắp xếp chính xác bằng Neural Cross-Encoder.
2. **Chọn Top-K & Candidate-K**: Điều chỉnh số lượng kết quả mong muốn.
3. **Ý nghĩa các trường kết quả**:
   - `Rank`: Thứ hạng xuất hiện của chunk.
   - `Score`: Điểm liên quan (BM25 score, Cosine similarity, RRF score hoặc Cross-Encoder logit).
   - `Citation`: Trích dẫn quy chuẩn định dạng `[Số hiệu văn bản | Điều khoản | chunk_id]`.
   - `Before vs After Rerank Table`: Bảng hiển thị sự hoán đổi vị trí của các chunk trước và sau khi qua Cross-Encoder.
   - `Graph Hints`: Hiển thị liên kết tuần tự `PREV` / `NEXT` và quan hệ liên văn bản trực tiếp 1-hop (ví dụ: văn bản bị thay thế hoặc sửa đổi).

---

## 10. Cấu trúc thư mục dự án

```text
buoi_14/
│
├── .env.example                    # Mẫu cấu hình kết nối Neo4j
├── .env                            # File cấu hình môi trường thực tế
├── app.py                          # Giao diện web demo Streamlit
│
├── cache/
│   ├── dense_embeddings.npy        # Vector embeddings cache của 6,593 chunks
│   └── dense_chunk_ids.json        # Danh sách chunk_id tương ứng với cache
│
├── cypher/
│   ├── schema.cypher               # Constraints và Index cho Neo4j
│   └── demo_queries.cypher         # Các câu truy vấn mẫu trên đồ thị
│
├── data/
│   ├── processed/
│   │   └── chunks_normalized.csv    # Dữ liệu corpus đã chuẩn hóa
│   └── eval/
│       └── questions.csv            # Bộ câu hỏi kiểm thử chuẩn (Gold dataset)
│
├── src/
│   ├── citation.py                 # Module định dạng trích dẫn chuẩn
│   ├── bm25_retriever.py           # Module tìm kiếm BM25
│   ├── dense_retriever.py          # Module tìm kiếm ngữ nghĩa Dense
│   ├── hybrid_retriever.py         # Module tìm kiếm Hybrid (RRF)
│   ├── reranker.py                 # Module tái xếp hạng Cross-Encoder Reranker
│   └── unified_retriever.py        # Module Retrieval thống nhất & Graph Hints
│
├── scripts/
│   ├── inspect_project.py          # Script kiểm tra dự án & dữ liệu nguồn
│   ├── prepare_corpus.py           # Script chuẩn hóa dữ liệu từ HTML
│   ├── baseline_retrieval.py       # Script chạy và so sánh 2 baseline
│   ├── hybrid_search.py            # Script chạy Hybrid Search (RRF)
│   ├── rerank.py                   # Script chạy Hybrid + Rerank
│   ├── compare_retrieval.py        # Script đánh giá định lượng Hit@k & MRR
│   ├── load_mini_kg.py             # Script nạp dữ liệu vào Neo4j an toàn
│   └── query_demo.py               # Script chạy truy vấn demo kèm Graph Hints
│
├── outputs/
│   ├── inspection_report.md        # Báo cáo phân tích dữ liệu nguồn
│   ├── retrieval_examples.md       # Báo cáo so sánh chi tiết 4 cấu hình Retrieval
│   ├── retrieval_comparison.csv    # Bảng điểm chi tiết từng câu hỏi kiểm thử
│   ├── evaluation_report.md        # Báo cáo đánh giá định lượng Hit@k & MRR
│   └── kg_build_report.md          # Báo cáo trạng thái nạp đồ thị Neo4j
│
├── requirements.txt                # Danh sách thư viện phụ thuộc
└── README.md                       # Tài liệu hướng dẫn sử dụng
```
