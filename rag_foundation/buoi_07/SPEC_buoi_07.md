# Agent Specification - Buổi 07

## Workspace
- Được đọc: rag_foundation/buoi_05/output/chunks/, rag_foundation/buoi_05/.venv/, rag_foundation/buoi_06/, rag_foundation/buoi_07/
- Được ghi: rag_foundation/buoi_07/
- Không sửa Buổi 05 và Buổi 06.

## Python
- Dùng interpreter Buổi 05.
- Không tạo virtual environment mới.

## Input
- JSON trong buoi_05/output/chunks/.
- Buổi 05 là nguồn dữ liệu đã chuẩn bị.
- Không OCR, parse PDF hoặc chunk lại.

## Packages
- Chỉ dùng các package được quy định trong requirements.txt.

## Pipeline
- validate
- embedding
- Chroma persistent
- retrieval
- confidence gate
- generation
- citation
- Streamlit
- unittest offline

## Data Contract
- Bắt buộc có các field: chunk_id, strategy, source, page_start, page_end, text.

## Index Contract
- Một strategy trong một collection.
- Model và dimension của index/query phải khớp.
- Dùng embedding thật, không dùng vector giả.
- Chặn NaN, Infinity, boolean và zero vector.
- Chroma cosine, embedding_function=None.
- Idempotent.
- Status read-only.
- Validate embedding trước khi reset/upsert.

## Retrieval Contract
- Trả evidence thật.
- Có distance.
- Chỉ evidence đạt threshold được đưa vào generation.
- Evidence yếu thì không gọi generation.

## Citation Contract
- Citation lấy từ metadata thật.
- Không tin source/page/chunk_id do LLM tự tạo.
- Result có citations và warnings; code thay label hợp lệ bằng citation thật.

## Security
- Không lộ secret.

## Testing
- unittest
- mock API
- temporary storage
- không Internet/key thật

## Coding Style
- Ít file
- Ít class
- Ít function
- Không kiến trúc phức tạp
