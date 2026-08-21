# BÁO CÁO ĐÁNH GIÁ SỰ PHỤ THUỘ VÀ TÁI SỬ DỤNG CODE (DEPENDENCY & REUSE REPORT)
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Kiểm tra & So sánh Dữ liệu Nguồn (Source Data Inspection)

### 1.1. Thống kê tổng quan dữ liệu
* **Tệp dữ liệu bảo mật (`chunks_secure.csv`)**:
  * **Vị trí**: `buoi_14/data/processed/chunks_secure.csv` (tham chiếu qua `../buoi_16/data/processed/chunks_secure.csv`).
  * **Số dòng**: **6,593** dòng.
  * **Số cột**: **13** cột.
  * **Danh sách cột**: `['chunk_id', 'document_id', 'text', 'source_file', 'title', 'document_type', 'chapter', 'section', 'article', 'clause', 'effective_date', 'status', 'allowed_roles']`.

* **Tệp dữ liệu đối chiếu (`chunks_normalized.csv`)**:
  * **Vị trí**: `buoi_14/data/processed/chunks_normalized.csv` (tham chiếu qua `../buoi_16/data/processed/chunks_normalized.csv`).
  * **Số dòng**: **6,593** dòng.
  * **Số cột**: **12** cột.
  * **Danh sách cột**: `['chunk_id', 'document_id', 'text', 'source_file', 'title', 'document_type', 'chapter', 'section', 'article', 'clause', 'effective_date', 'status']`.

---

### 1.2. Ánh xạ các trường dữ liệu quan trọng

| Trường thông tin | Tên cột thực tế trong CSV | Trạng thái kiểm tra |
| :--- | :--- | :--- |
| `chunk_id` | `chunk_id` | Có mặt (UUID chuỗi) |
| `document_id` | `document_id` | Có mặt (Mã định danh văn bản) |
| `citation` | Sinh động qua `build_citation()` | Khởi tạo động trong pipeline |
| `title` | `title` | Có mặt (Tên văn bản quy định) |
| `loai_van_ban` | `document_type` | Có mặt (Loại văn bản: Nghị định, Thông tư, Quy chế...) |
| `co_quan_ban_hanh` | Trích xuất từ `source_file` / `title` | Có mặt trong metadata văn bản |
| `ngay_ban_hanh` | `effective_date` | Có mặt (Ngày có hiệu lực) |
| `allowed_roles` | `allowed_roles` | Có mặt trong `chunks_secure.csv` (JSON List) |

---

### 1.3. Kết luận so sánh hai tệp dữ liệu
* **Khẳng định**: **`chunks_secure.csv` = `chunks_normalized.csv` + `allowed_roles`**.
* **Kiểm chứng thực nghiệm**: 100% dữ liệu ở 12 cột dùng chung khớp tuyệt đối trên từng dòng giữa 2 tệp CSV (`6,593` / `6,593` dòng). Không có sai lệch hoặc mất mát dữ liệu nào khác.
* **Phân bố `allowed_roles`**:
  * `["Admin", "HR", "Staff", "Guest"]`: **4,302** chunks (Công khai / Tất cả vai trò).
  * `["Admin", "Staff"]`: **2,027** chunks (Nội bộ nhân viên).
  * `["Admin", "HR"]`: **264** chunks (Giới hạn Nhân sự).

---

## 2. Phân tích Chi tiết `SecureRetriever` (Buổi 16 / Buổi 14)

### 2.1. Thông tin Module & Cấu trúc
* **File/Module**: `buoi_14/src/secure_retriever.py`
* **Lớp chính (Class)**: `SecureRetriever`
* **Phương thức khởi tạo**: `SecureRetriever(corpus_path, embedding_model_name, cache_dir)`
* **Phương thức truy xuất chính**: `retrieve(query, user_roles, method='hybrid_rerank', top_k=5, candidate_k=20)`

---

### 2.2. Tham số Đầu vào & Đầu ra (Input/Output API)
* **Input Role**:
  * Tham số: `user_roles: list[str] | str` (Ví dụ: `["Guest"]`, `["Staff"]`, `["Admin", "HR"]`).
  * Chuẩn hóa qua hàm `validate_roles(user_roles)` từ `src/config.py`.
* **Output Format**: Danh sách các `dict` biểu diễn chunk tài liệu được phép truy xuất, bao gồm:
  ```python
  {
      "rank": 1,
      "chunk_id": "b0cf278a-df4c-11f0-b9ad-59e9810e1792",
      "document_id": "112025",
      "source_file": "73/2016/NĐ-CP",
      "title": "Nghị định số 73/2016/NĐ-CP...",
      "article": "Điều 1",
      "clause": "Khoản 1",
      "text": "Nội dung quy định...",
      "score": 0.0325,
      "citation": "Trích dẫn: [Nghị định 73/2016/NĐ-CP, Điều 1, Khoản 1]",
      "retrieval_method": "Hybrid + Rerank (Secure)",
      "allowed_roles": ["Admin", "HR", "Staff", "Guest"],
      "hybrid_score": 0.0325,
      "rerank_score": 0.8954
  }
  ```

---

### 2.3. Cơ chế Lọc RBAC: Pre-Filtering (Lọc TRƯỚC)
* **BM25 Search (`search_bm25`)**: Tạo NumPy Boolean Mask `_get_role_mask(user_roles)` và gán score `-inf` cho các chunk không có quyền TRƯỚC KHI lấy Top-K.
* **Dense Search (`search_dense`)**: Nhân Cosine Similarity vector với Boolean Access Mask TRƯỚC KHI sắp xếp lấy Top-K.
* **Neo4j Graph Search (`search_graph`)**: Sử dụng Cypher `WHERE any(role IN d.allowed_roles WHERE role IN $user_roles)` để lọc trực tiếp trong Database Engine.
* **Hybrid + Reranker (`search_hybrid_rerank`)**: Cross-Encoder Reranker CHỈ nhận tập ứng viên đã vượt qua bộ lọc RBAC (Secure Hybrid Candidates Pool). **Tuyệt đối không để văn bản cấm lọt vào Reranker hoặc Context của LLM.**

---

### 2.4. Bảo toàn Metadata & Citation
* Cả 3 trường định danh `document_id`, `chunk_id`, và `citation` đều được **BẢO TOÀN NGUYÊN VẸN** trong mọi phương thức truy xuất của `SecureRetriever`.

---

## 3. Kế hoạch Tái sử dụng cho Buổi 17 (Reuse Plan)

1. **Giữ nguyên trạng Buổi 16 / Buổi 14**: Không chỉnh sửa `chunks_secure.csv` hay `buoi_14/src/secure_retriever.py`.
2. **Khởi tạo Adapter trong Buổi 17 (`buoi_17/scripts/secure_retrieval.py`)**:
   * Nạp `SecureRetriever` từ `buoi_14/src/secure_retriever.py` bằng `sys.path`.
   * Tạo wrapper/adapter nếu cần để đảm bảo giao diện đồng nhất cho Use Case 1 (Internal Lookup) và Use Case 2 (Compliance Gap).
3. **Cấu hình Môi trường Buổi 17 (`buoi_17/.env`)**: Trỏ đường dẫn `SOURCE_SECURE_CSV` và `SOURCE_NORMALIZED_CSV` tới các tệp dữ liệu đã sẵn có.

---

## STATUS SUMMARY

```text
SOURCE DATA: PASS
RBAC DATA AVAILABLE: YES
SECURE RETRIEVER REUSABLE: YES
REUSE PLAN: Tái sử dụng 100% dữ liệu chunks_secure.csv và SecureRetriever từ buoi_14 qua Adapter script trong buoi_17 mà không viết lại hay thay đổi code cũ.
```
