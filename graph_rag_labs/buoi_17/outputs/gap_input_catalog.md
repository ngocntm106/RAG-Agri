# BÁO CÁO PHÂN LOẠI DANH MỤC DỮ LIỆU ĐẦU VÀO (GAP INPUT CATALOG)
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Thống kê Tổng quan Corpus Dữ liệu Kết hợp (Combined Corpus)
* **Nguồn Dữ liệu**: `buoi_17/data/chunks_combined_secure.csv`
* **Tổng số Chunks**: `811` chunks
* **Tổng số Văn bản (Unique Document IDs)**: `25` văn bản
* **Số văn bản Yêu cầu Bên ngoài (EXTERNAL_REQUIREMENT)**: `15` văn bản
* **Số văn bản Quy định Nội bộ (INTERNAL_POLICY)**: `10` văn bản

---

## 2. Bảng Danh mục Phân loại Chi tiết 100% Văn bản trong Corpus
| STT | Document ID | Số ký hiệu | Loại văn bản | Cơ quan ban hành | Phân loại | Chứng cứ phân loại (Real Evidence) | Số chunks |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| 1 | `112025` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 117 |
| 2 | `112924` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 22 |
| 3 | `117310` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 25 |
| 4 | `163441` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 143 |
| 5 | `166269` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 116 |
| 6 | `168220` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 35 |
| 7 | `169221` | `content.csv` |  | Ngân hàng Nhà nước Việt Nam (NHNN) | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Ngân hàng Nhà nước Việt Nam (NHNN) ban hành (Ký hiệu: content.csv, Loại: ). | 5 |
| 8 | `173695` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 26 |
| 9 | `174218` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 31 |
| 10 | `177271` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 22 |
| 11 | `185630` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 17 |
| 12 | `25692` | `content.csv` |  | Ngân hàng Nhà nước Việt Nam (NHNN) | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Ngân hàng Nhà nước Việt Nam (NHNN) ban hành (Ký hiệu: content.csv, Loại: ). | 68 |
| 13 | `44209` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 74 |
| 14 | `6e689cd0-6f81-11f1-94d6-fd5d6d5ff793` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 46 |
| 15 | `95652` | `content.csv` |  | Cơ quan Nhà nước bên ngoài | **EXTERNAL_REQUIREMENT** | Văn bản quy phạm pháp luật do Cơ quan Nhà nước bên ngoài ban hành (Ký hiệu: content.csv, Loại: ). | 40 |
| 16 | `agr_at01` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank). | 4 |
| 17 | `agr_bh06` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy định nội bộ số 180/QĐ-NHNO-BH về Mua bảo hiểm rủi ro nghiệp vụ và tài sản Agribank). | 2 |
| 18 | `agr_car02` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy định nội bộ số 250/QĐ-NHNO-QLRR về Quản lý tỷ lệ an toàn vốn và định mức rủi ro Agribank). | 3 |
| 19 | `agr_fx04` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy định nội bộ số 410/QĐ-NHNO-TTNH về Quản lý trạng thái ngoại tệ và giao dịch ngoại hối Agribank). | 2 |
| 20 | `agr_gp05` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy chế số 520/QC-NHNO-MANGLUOI về Mở rộng mạng lưới chi nhánh và phòng giao dịch Agribank). | 2 |
| 21 | `agr_hr08` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy định nội bộ số 88/QĐ-NHNO-NS về Quy hoạch, bổ nhiệm và quản lý nhân sự Agribank). | 2 |
| 22 | `agr_it07` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT về An toàn thông tin và Quản trị dữ liệu AI Agribank). | 2 |
| 23 | `agr_tc09` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy chế tài chính số 720/QC-NHNO-TC về Chế độ chi tiêu và mua sắm tài sản nội bộ Agribank). | 2 |
| 24 | `agr_td03` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy chế tín dụng nội bộ số 315/QC-NHNO-TD về Phán quyết và Phân cấp ủy quyền cho vay tại Agribank). | 3 |
| 25 | `agr_xln10` | `agribank_internal_policies.csv` |  | Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **INTERNAL_POLICY** | Văn bản quy định/quy chế nội bộ do Agribank ban hành (Ký hiệu: agribank_internal_policies.csv, Tiêu đề: Quy định nội bộ số 390/QĐ-NHNO-XLN về Phân loại nợ và Xử lý nợ xấu tại Agribank). | 2 |

---

## 3. Đánh giá Minh chứng & Đã chứng minh Thực tế

1. **Đã bổ sung đầy đủ văn bản nội bộ**: Tệp `chunks_combined_secure.csv` trong `buoi_17/data` đã tích hợp 10 văn bản quy định/quy chế nội bộ thực tế của Agribank (`INTERNAL_POLICY`).
2. **Đủ dữ liệu đối chiếu 2 phía**: Corpus hiện chứa đầy đủ cả 15 văn bản quy phạm pháp luật bên ngoài (`EXTERNAL_REQUIREMENT`) và 10 văn bản quy định nội bộ (`INTERNAL_POLICY`).
3. **Kết luận**: Tập dữ liệu đã sẵn sàng cho bài toán phân tích khoảng trống tuân thủ AI Compliance Gap Checker.

## STATUS SUMMARY

```text
COMPLIANCE GAP DATA: READY
```