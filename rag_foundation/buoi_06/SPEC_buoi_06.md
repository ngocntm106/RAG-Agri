# SPEC_buoi_06 — Hướng dẫn AI Agent

## Workspace

Chỉ được phép đọc:

- `RAG/rag_foundation/buoi_05/output/chunks/`
- `RAG/rag_foundation/buoi_05/.venv/`
- `RAG/rag_foundation/buoi_06/`

Ghi chú: buoi_06.md 2026-08-05

Không được đọc:

- Source code của Buổi 5
- README các buổi trước
- Notebook
- Git history
- Các thư mục khác

Buổi 5 được coi là black box: không reverse-engineering và không phân tích cách Buổi 5 hoạt động.

## Python

Sử dụng đúng interpreter trong: `RAG/rag_foundation/buoi_05/.venv/`

Không tạo virtual environment mới.

## Package

Chỉ được cài (nếu cần):

- `streamlit`
- `google-genai`
- `chromadb`
- `psycopg` (hoặc `psycopg2` tùy môi trường)
- `python-dotenv`

Không cài thêm framework hoặc thư viện khác.

## Coding Style

- Ưu tiên: ít file, ít class, ít function; code dễ đọc.
- Tránh patterns phức tạp: không sử dụng repository pattern, service layer, dependency injection, factory, plugin.

## Scope

Chỉ cần implement các phần sau:

- index (giao diện Streamlit)
- retrieval (tìm kiếm/tải dữ liệu từ kho đã cho)
- answer (tạo phản hồi dựa trên retrieval + model)
- streamlit (giao diện và flow đơn giản)

Không phát triển ngoài yêu cầu.

## Error Handling

Chỉ cần try/except tối thiểu để bắt lỗi rõ ràng và trả về thông báo hữu ích.

Không cần: retry logic, hệ thống logging, hoặc monitoring phức tạp.

## Security

- Không in bất kỳ API key, password hoặc secret nào ra console hoặc UI.

## Code Size

Mục tiêu: ~300–500 dòng Python tổng cộng.
Nếu vượt ~700 dòng, đơn giản hóa thiết kế
