# Buổi 07 - RAG Foundation

## 1. Mục tiêu

Buổi 07 xây dựng một backend RAG đơn giản với:
- loader JSON cho các chunk từ Buổi 05
- embed bằng Gemini thật ở runtime
- chỉ số persistent Chroma theo strategy/model/dimension
- retrieval, confidence gate, generation prompt và citation mapping
- Streamlit UI nhẹ để trigger index và query
- unittest offline với fake client và temporary storage

## 2. Quan hệ với Buổi 05 và Buổi 06

- Buổi 05 cung cấp dữ liệu đã chunk sẵn tại `rag_foundation/buoi_05/output/chunks/`.
- Buổi 07 chỉ dùng JSON này, không chunk lại, không OCR, không parse PDF.
- Buổi 06 không bị sửa. Buổi 07 là một module độc lập xây trên dữ liệu Buổi 05.

## 3. Sơ đồ pipeline

1. Validate JSON chunk input
2. Load chunk theo strategy (`hierarchical`, `semantic`, `fixed-size`)
3. Tạo embedding bằng Gemini
4. Validate vector trước khi upsert
5. Tạo hoặc tái sử dụng collection Chroma persistent
6. Query top-k và tính distance cosine
7. Lọc evidence theo threshold `RAG_MAX_DISTANCE`
8. Nếu đủ evidence thì gọi generator Gemini
9. Map label `[E1]`, `[E2]` sang citation metadata thật

## 4. Cấu trúc thư mục

- `rag.py` - backend RAG chính
- `app.py` - Streamlit UI
- `requirements.txt` - dependencies Buổi 07
- `.env.example` - mẫu biến môi trường
- `.gitignore` - ignore `.env`, storage/chroma, cache
- `tests/` - unittest offline
- `tests/fixtures/` - test fixture JSON

## 5. Điều kiện đầu vào

- JSON list hoặc object có key `chunks`
- mỗi record cần: `chunk_id`, `strategy`, `source`, `page_start`, `page_end`, `text`
- strategy phải nằm trong `hierarchical`, `semantic`, `fixed-size`
- `text` có thể rỗng nhưng sẽ bị bỏ qua và đếm vào `empty_text_skipped`
- duplicate `chunk_id` sẽ bị chặn

## 6. Cách dùng `.venv` Buổi 05

Dùng Python trong `rag_foundation/buoi_05/.venv` để chạy Buổi 07.
Điều này đảm bảo không tạo environment mới và dùng đúng interpreter yêu cầu.

## 7. Cách cài requirements

Windows PowerShell:
```powershell
Set-Location "...\RAG\rag_foundation\buoi_07"
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```
Linux/macOS:
```bash
cd .../RAG/rag_foundation/buoi_07
/path/to/buoi_05/.venv/bin/python -m pip install -r requirements.txt
```

## 8. Cách tạo `.env` từ `.env.example`

Sao chép file mẫu và điền API key:

```powershell
Copy-Item .env.example .env
```

Hoặc Linux/macOS:

```bash
cp .env.example .env
```

## 9. Giải thích từng biến môi trường

- `GEMINI_API_KEY`: API key Gemini thực tế. Bắt buộc để index và query.
- `GEMINI_EMBEDDING_MODEL`: mô hình embedding, ví dụ `gemini-embedding-2`.
- `GEMINI_EMBEDDING_DIM`: số chiều embedding, ví dụ `768`.
- `GEMINI_GENERATION_MODEL`: mô hình generation thực tế.
- `DEFAULT_TOP_K`: số lượng top-k mặc định.
- `RAG_MAX_DISTANCE`: ngưỡng cosine distance chấp nhận evidence.

## 10. Lệnh validate

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" rag.py validate --strategy hierarchical
```

## 11. Lệnh status

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" rag.py status --strategy hierarchical
```

## 12. Lệnh index

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" rag.py index --strategy hierarchical
```

## 13. Lệnh reset đúng collection

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" rag.py index --strategy hierarchical --reset
```

## 14. Lệnh query CLI

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" rag.py query --strategy hierarchical --top-k 5 --question "Câu hỏi của bạn"
```

## 15. Lệnh chạy test

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py" -v
```

## 16. Lệnh chạy Streamlit

```powershell
& "...\RAG\rag_foundation\buoi_05\.venv\Scripts\python.exe" -m streamlit run app.py
```

## 17. Giải thích thuật ngữ

- `strategy`: mỗi collection chỉ chứa một loại strategy
- `embedding model`: mô hình Gemini dùng để tạo vector
- `embedding dimension`: số chiều embedding, phải cùng giữa index và query
- `collection identity`: tách bởi strategy/model/dimension
- `top-k`: số chunk trả về trước khi lọc threshold
- `cosine distance`: `1 - cosine_similarity`, số nhỏ hơn tốt hơn
- `RAG_MAX_DISTANCE`: ngưỡng chấp nhận evidence
- `confidence gate`: chỉ gọi generation khi evidence có `accepted=True`
- `retrieval-only`: khi generation lỗi hoặc answer rỗng sau khi đã truy xuất evidence
- `citation`: label `[E1]` map sang metadata thật, không dựa trên nội dung LLM tự sinh

## 18. Cách dừng Streamlit bằng Ctrl+C

Trong terminal nhấn `Ctrl+C` để dừng server Streamlit.

## 19. Troubleshooting

- Thiếu package: cài `requirements.txt` bằng interpreter Buổi 05.
- Sai interpreter: phải dùng `buoi_05/.venv`.
- Thiếu API key: nhập `GEMINI_API_KEY` vào `.env`.
- Collection rỗng: check `status` trước, nếu chưa tồn tại hoặc count 0 thì chạy `index`.
- Model/dimension mismatch: nếu `status` báo collection có metadata khác, dùng `--reset` để recreate.
- JSON lỗi: kiểm tra định dạng JSON và cấu trúc `chunks`.
- Embedding lỗi/rate limit: nếu Gemini trả lỗi, kiểm tra key và quyền dự án.

## 20. Giới hạn của demo

- Chỉ dùng dữ liệu chunk từ Buổi 05.
- Không chunk lại, không OCR, không đánh giá PDF.
- Chỉ demo RAG cơ bản, không phải một hệ thống sản xuất.
- Không đảm bảo trả lời pháp lý.

## 21. Cảnh báo

- Không phải tư vấn pháp lý.
- `RAG_MAX_DISTANCE` cần hiệu chỉnh theo dữ liệu và chất lượng embedding.
- Retrieval có thể bỏ sót thông tin.
- Nội dung chunk được gửi tới Gemini khi embedding/generation; chỉ dùng dữ liệu mà người vận hành được phép gửi lên dịch vụ bên ngoài.

## 22. Manual test plan

A. Có khả năng thuộc tài liệu:
- `Cơ cấu lại thời hạn trả nợ được quy định như thế nào?`

B. Có khả năng thuộc tài liệu:
- `Việc phân loại nợ và trích lập dự phòng được thực hiện như thế nào?`

C. Ngoài phạm vi:
- `Ngân hàng nào có lãi suất tiết kiệm cao nhất hôm nay?`

> A/B không được đảm bảo chắc chắn, nhưng query nên dựa trên dữ liệu thật đã index.
> Với C, nếu evidence không đạt threshold thì không gọi generation và câu trả lời nên là `Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp.` hoặc tương tự. Nếu vẫn đạt threshold thì coi như false positive của retrieval/gate.
