# BÁO CÁO MÔ PHỎNG MÃ HÓA DỮ LIỆU AT-REST (DATA AT-REST ENCRYPTION DEMO)
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Mục tiêu Demo & Phạm vi Ứng dụng

Mô hình mã hóa dữ liệu lưu trữ (Data At-Rest Encryption) trong bài lab Buổi 17 được cài đặt nhằm minh họa nguyên lý bảo mật tệp nhật ký kiểm toán (`audit_log.jsonl`) trên đĩa cứng, ngăn ngừa truy cập trái phép trực tiếp vào hệ thống tệp.

> [!WARNING]
> Đây là mô hình demo kỹ thuật minh họa cho bài lab đào tạo. Hệ thống không tuyên bố sẵn sàng cho môi trường sản xuất (Production-Ready) do cần tích hợp các hệ thống quản lý khóa chuyên dụng như AWS KMS, Azure Key Vault hoặc HashiCorp Vault.

---

## 2. Thư viện & Cơ chế Quản lý Khóa (Key Management)

* **Thư viện chuẩn**: Sử dụng `cryptography.fernet.Fernet` (Thuật toán AES-128 ở chế độ CBC với HMAC SHA-256 để xác thực tính toàn vẹn).
* **Quản lý Khóa Mã hóa**:
  * **Không Hard-code**: Khóa không được lưu cứng trong mã nguồn Python.
  * **Tạo động**: Khóa mã hóa ngẫu nhiên được khởi tạo qua `Fernet.generate_key()` và lưu ra tệp cục bộ `buoi_17/secret.key`.
  * **Bảo vệ Git Repository**: Đã bổ sung quy tắc `*.key` và `.env` vào tệp `.gitignore` để đảm bảo khóa bảo mật tuyệt đối không bị commit lên hệ thống quản lý phiên bản.

---

## 3. Kết quả Thực nghiệm Mã hóa và Giải mã

Chạy thử nghiệm trực tiếp qua tập lệnh [buoi_17/scripts/encryption_demo.py](file:///c:/Users/minhn/OneDrive/Desktop/H%E1%BB%8Dc%20AI/RAG/graph_rag_labs/buoi_17/scripts/encryption_demo.py):

| Bước thực hiện | Tệp dữ liệu | Kích thước | Kết quả thực thi |
| :--- | :--- | :---: | :--- |
| **1. Tệp gốc** | `audit_log.jsonl` | `3,642` bytes | Đọc thành công dữ liệu nhật ký kiểm toán dạng JSONL. |
| **2. Mã hóa (Encrypt)** | `audit_log.jsonl.enc` | `4,940` bytes | Mã hóa thành công dữ liệu nhị phân không thể đọc trực tiếp. |
| **3. Giải mã (Decrypt)** | `audit_log_decrypted.jsonl` | `3,642` bytes | Giải mã thành công sử dụng khóa Fernet lưu tại `secret.key`. |

---

## 4. Đối chiếu Tính Toàn vẹn Dữ liệu (Byte-for-Byte Verification)

* **So sánh nhị phân**: `original_bytes == decrypted_bytes`
* **Kết quả**: **True** (Trùng khớp 100% tuyệt đối đến từng byte).
* **Không sửa đổi dữ liệu nguồn**: Dữ liệu nguồn của Buổi 16 và tệp nhật ký kiểm toán không bị thay đổi hay biến dạng sau quá trình mã hóa/giải mã.

---

## STATUS SUMMARY

```text
ENCRYPT: PASS
DECRYPT MATCH: PASS
PRODUCTION READY: NO
```
