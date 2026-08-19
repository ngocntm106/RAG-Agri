# Specification - Buổi 08: Advanced RAG Architecture & Evaluation

## 1. Workspace & Security Contract
- **Workspace Scope**: Tất cả code, tài nguyên, dữ liệu trung gian, index và kết quả đánh giá chỉ được lưu trữ trong `rag_foundation/buoi_08/`.
- **Thư mục cấm sửa**: Tuyệt đối không chỉnh sửa các tài nguyên thuộc `rag_foundation/buoi_05/`, `buoi_06/` và `buoi_07/`.
- **Bảo mật Secret**: Không commit tệp `.env` chứa API key thật. File `.env.example` cung cấp mẫu cấu hình chuẩn. Các bài kiểm thử tự động (unittests) phải chạy offline sử dụng mock API hoặc stub.

## 2. Quan hệ với Buổi 05 và Buổi 07
- **Buổi 05**: Nguồn cung cấp dữ liệu JSON chunks chuẩn hóa tại `rag_foundation/buoi_05/output/chunks/`.
- **Buổi 07**: Nguồn mã nguồn baseline semantic retrieval. `rag_foundation/buoi_08/rag.py` là bản sao trực tiếp từ `buoi_07/rag.py` dùng làm baseline đối chứng độc lập.
- **Buổi 08**: Mở rộng hệ thống RAG nâng cao kết hợp BM25 Keyword Search, Gemini Semantic Retrieval, Reciprocal Rank Fusion (RRF) và Cross-Encoder Reranking.

## 3. Data Contract
- Mỗi document chunk bắt buộc chứa 6 thuộc tính chuẩn:
  - `chunk_id` (string, duy nhất)
  - `strategy` (string: "fixed-size" | "semantic" | "hierarchical")
  - `source` (string)
  - `page_start` (int >= 1)
  - `page_end` (int >= page_start)
  - `text` (string, không rỗng)

## 4. BM25 Tokenizer & Retrieval Contract
- **Tokenizer**: Sử dụng tokenizer xử lý tiếng Việt / tách từ phù hợp (nhiệm vụ loại bỏ punctuation, đưa về lowercase, giữ lại thuật ngữ pháp lý và con số Điều/Khoản).
- **BM25 Scoring**: Trích xuất Top-K ứng viên dựa trên BM25 Okapi score từ tập chunks của strategy tương ứng.
- **Output**: Mỗi kết quả BM25 phải kèm `bm25_score` và thứ hạng `bm25_rank`.

## 5. Semantic Candidate Contract
- Sử dụng Gemini Embedding API (hoặc mock embedding trong môi trường test).
- Lưu trữ và truy vấn qua Chroma PersistentClient với khoảng cách `cosine`.
- **Output**: Trích xuất Top-K ứng viên semantic kèm theo `semantic_distance` và thứ hạng `semantic_rank`.

## 6. RRF Fusion Contract (Reciprocal Rank Fusion)
- Kết hợp thứ hạng từ BM25 List và Semantic List theo công thức:
  $$\text{RRF\_Score}(d) = \frac{1}{k + \text{rank}_{\text{bm25}}(d)} + \frac{1}{k + \text{rank}_{\text{semantic}}(d)}$$
  với $k = 60$ (mặc định).
- Kết quả được sắp xếp giảm dần theo `rrf_score` để chọn ra danh sách Top-N ứng viên rút gọn cho bước Rerank.

## 7. Cross-Encoder Reranker Contract
- Đưa danh sách Top-N ứng viên từ RRF qua mô hình Cross-Encoder để tính điểm tương quan ngữ nghĩa trực tiếp (query, document_text).
- Chấp nhận điểm số `rerank_score` chuẩn hóa.
- Chặn ngưỡng điểm tối thiểu (`RAG_MAX_DISTANCE` / threshold) để loại bỏ các đoạn không liên quan.

## 8. Final Evidence & Citation Contract
- Chỉ các chunk vượt qua ngưỡng rerank / confidence gate mới được đưa vào ngữ cảnh sinh câu trả lời (Generation).
- Trích xuất citation dựa vào metadata thực tế (`source`, `page_start`, `page_end`, `chunk_id`), không tin tưởng số trang hoặc nguồn do LLM tự bịa ra.
- Định dạng trích dẫn chuẩn: `[Nguồn: <source>, tr. <page_start>-<page_end>, chunk: <chunk_id>]`.

## 9. Pipeline Trace Contract
- Mỗi truy vấn Advanced RAG phải trả về cấu trúc Trace chi tiết phục vụ kiểm thử và UI visualization:
  - `query`: Câu hỏi đầu vào
  - `bm25_candidates`: Danh sách Top-K BM25 (kèm score, rank)
  - `semantic_candidates`: Danh sách Top-K Semantic (kèm distance, rank)
  - `rrf_fused`: Danh sách hợp nạp RRF (kèm rrf_score, rrf_rank)
  - `reranked`: Danh sách sau Cross-Encoder (kèm rerank_score, rank cuối)
  - `final_evidence`: Danh sách evidence gửi sang LLM
  - `latency_ms`: Thời gian xử lý chi tiết từng công đoạn

## 10. Evaluation Metrics Contract
- Tập `eval/questions.json` là **starter kit**: mọi mục phải có `needs_human_review: true` cho đến khi có người có thẩm quyền duyệt gold labels. Không được coi đây là bộ đánh giá đã được chuyên gia pháp lý xác nhận.
- Đánh giá hiệu năng trích xuất (Retrieval Performance) dựa trên tập `eval/questions.json`:
  - **Hit Rate@K**: Tỷ lệ câu hỏi tìm thấy ít nhất 1 chunk relevant trong Top-K.
  - **MRR@K (Mean Reciprocal Rank)**: Thứ hạng trung bình của chunk relevant đầu tiên.
  - **Precision@K**: Tỷ lệ chunk relevant trên tổng số K chunk trả về.
  - **Recall@K**: Tỷ lệ chunk relevant tìm thấy trên tổng số chunk relevant của câu hỏi.
  - **Latency**: Thời gian phản hồi trung bình (ms).

## 11. Offline Testing Contract
- Tất cả unit test và integration test phải chạy hoàn toàn offline không cần Internet hay API key thật.
- Sử dụng fixture `tests/fixtures/chunks_advanced_sample.json` và mock embeddings/LLM responses.

## 12. UI Comparison Contract
- Ứng dụng Streamlit ([app.py](file:///c:/Users/minhn/OneDrive/Desktop/H%E1%BB%8Dc%20AI/05_m%E1%BA%ABu/Rag_thuchanh/RAG/rag_foundation/buoi_08/app.py)) hỗ trợ so sánh trực quan song song (Side-by-Side):
  - Bên trái: **Baseline Semantic RAG (Buổi 07)**
  - Bên phải: **Advanced RAG (BM25 + Semantic + RRF + Reranker)**
- Hiển thị bảng so sánh thứ hạng candidate, điểm RRF, điểm Rerank, thời gian phản hồi và độ chính xác của trích dẫn.
