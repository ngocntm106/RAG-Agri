# BÁO CÁO ĐÁNH GIÁ VÀ KHAI THÁC KNOWLEDGE GRAPH CHO GAP CHECKER
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Kết quả Rà soát Thực tế Schema & Mối quan hệ trong Graph (Graph Schema Audit)

Đã rà soát 100% tệp dữ liệu đồ thị trong kho lưu trữ (`kb+hops/relationships.csv`, `ner_kb/relationships.csv`, `buoi_13/data/relationships_seed.csv`) và kiểm tra trạng thái kết nối Neo4j Live Database:

### Bảng Đánh giá Các Loại Quan hệ (Relationship Types) Thực tế:

| Loại Quan hệ (Relationship Type) | Tệp dữ liệu chứa | Bản chất & Mục đích sử dụng | Đánh giá Giá trị đối với Compliance Gap Matching |
| :--- | :--- | :--- | :--- |
| `CONTAINS` | Graph Database | Cấu trúc cây: Văn bản chứa Điều khoản (`VanBan -> DieuKhoan`) | **KHÔNG LIÊN QUAN**: Chỉ nối quan hệ cha-con trong cùng 1 văn bản. |
| `NEXT` | Graph Database | Cấu trúc tuyến tính: Điều khoản tiếp theo (`DieuKhoan -> DieuKhoan`) | **KHÔNG LIÊN QUAN**: Chỉ nối thứ tự các điều khoản kế tiếp. |
| `BAN_HANH_BOI` / `KY_BOI` | `ner_kb/relationships.csv` | Metadata: Nối văn bản với cơ quan ban hành (Chính phủ, NHNN) hoặc người ký | **KHÔNG LIÊN QUAN**: Không giúp nối ngữ nghĩa giữa quy định NHNN và nội quy nội bộ. |
| `CAN_CU` / `SUA_DOI_BO_SUNG` | `kb+hops/relationships.csv` | Pháp lý: Nối giữa 2 văn bản pháp luật bên ngoài (vd: Thông tư 43 sửa đổi Thông tư 01) | **HẠN CHẾ**: Chỉ nối văn bản nhà nước với văn bản nhà nước, không nối tới quy định nội bộ. |
| `MITIGATES` | `buoi_13/data/relationships_seed.csv` | Dữ liệu mô phỏng bài lab 13 (Kiểm soát nối Rủi ro) | **KHÔNG SỬ DỤNG**: Dữ liệu giả lập cho bài lab trước, không có trong corpus thực tế. |

---

## 2. Đánh giá Trạng thái Kết nối Neo4j Database

* **Trạng thái kết nối**: Neo4j Database hiện đang ở trạng thái **Offline / Not Connected** (`[WinError 10061] No connection could be made`).
* **Cơ chế An toàn**: Pipeline `SecureRetriever` và `ComplianceGapChecker` hoạt động dựa trên cơ chế Fallback tự động về Hybrid Search (BM25 + Dense Vector) + Cross-Encoder Reranker.

---

## 3. Quyết định Kiến trúc & Khai thác Đồ thị (Architecture Decision)

1. **Không tự tạo edge giả**: Tuân thủ nguyên tắc không bịa đặt mối quan hệ cạnh (edge) giữa văn bản nhà nước và quy định nội bộ khi dữ liệu chưa có.
2. **Giữ nguyên trạng Hybrid + Rerank**: Thuật toán truy xuất Hybrid Search (BM25 + Dense) kết hợp Reranker là giải pháp tối ưu, ổn định và chính xác nhất cho Use Case 2 ở thời điểm hiện tại.
3. **Kết luận khai thác**: **GRAPH NOT USED FOR GAP MATCHING** (Không sử dụng Graph cho bài toán khớp Gap tuân thủ do thiếu mối quan hệ liên văn bản nội bộ - ngoại bộ trong cơ sở dữ liệu đồ thị hiện tại).

---

## STATUS SUMMARY

```text
GRAPH USED: NO
REASON: Các quan hệ trong đồ thị hiện tại chỉ bao gồm cấu trúc hình học (CONTAINS/NEXT), metadata ban hành (BAN_HANH_BOI), và căn cứ pháp lý giữa các văn bản nhà nước (CAN_CU). Chưa có edge nối ngữ nghĩa giữa Yêu cầu NHNN và Quy định nội bộ. Ngoài ra Neo4j DB hiện không khả dụng nên hệ thống duy trì Hybrid Search + Reranker an toàn.
```
