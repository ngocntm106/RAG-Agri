# BÁO CÁO PHÂN TÍCH KHOẢNG TRỐNG TUÂN THỦ (AI COMPLIANCE GAP CHECKER REPORT)
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Kết quả Rà soát Hiện trạng Dữ liệu (Data Gap Assessment)

* **Cập nhật dữ liệu**: Tệp `buoi_17/data/chunks_combined_secure.csv` tích hợp đầy đủ 15 văn bản quy phạm pháp luật nhà nước bên ngoài (`EXTERNAL_REQUIREMENT`) và 10 văn bản quy định/quy chế nội bộ thực tế của Agribank (`INTERNAL_POLICY`).
* **Trạng thái Dữ liệu đối chiếu**: `COMPLIANCE GAP DATA: READY`.
* **Quy trình phân tích**: Tiến hành khớp nối bằng chứng hai phía (Evidence Package) giữa Yêu cầu NHNN và Quy định nội bộ Agribank qua thuật toán Hybrid Search + Reranker.

---

## 2. Bảng Tổng hợp Kết quả Đánh giá Evidence Package

| STT | Ma Req | Yêu cầu NHNN (External Requirement) | Citation NHNN | Bằng chứng Nội bộ Agribank (Internal Evidence) | Trạng thái Gap | Lý do phân loại | Review Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| 1 | `REQ-NHNN-01-VALUABLES` | Quy định về tiêu chuẩn bảo quản, vận chuyển tiền mặt, tài sản quý và giấy tờ có giá trong kho tiền. | `[Thông tư 01/2014/TT-NHNN | Điều 15. Sắp xếp, bảo quản tài sản tại quầy giao dịch và trong kho tiền | 9fe3fbee-2d53-11f1-9d3d-e316384c20ed]` | KHÔNG CÓ (Thiếu văn bản quy định nội bộ INTERNAL_POLICY trong corpus đối chiếu) | **CHUA_DU_BANG_CHUNG** | Hệ thống ghi nhận yêu cầu quy định NHNN nhưng không tìm thấy tệp quy định nội bộ (INTERNAL_POLICY) tương ứng trong corpus để đối chiếu bằng chứng hai phía. Cần bổ sung tài liệu nội bộ trước khi đánh giá. | **NEEDS_HUMAN_REVIEW** |
| 2 | `REQ-NHNN-41-CAPITAL` | Quy định tỷ lệ an toàn vốn tối thiểu và quản lý rủi ro hoạt động đối với ngân hàng thương mại. | `[Thông tư 41/2016/TT-NHNN | Điều 3. Tỷ lệ an toàn vốn | 93f5c852-df3e-11f0-b44b-8573f7cc12b3]` | Tỷ lệ an toàn vốn tối thiểu (CAR) của Agribank được quy định duy trì ở mức tối thiểu 8.5%, cao hơn 0... | **CHENH_LECH** | Quy định nội bộ Agribank (250/QĐ-NHNO-QLRR) quy định CAR tối thiểu 8.5%, cao hơn 0.5% so với mức 8.0% chung tại Thông tư 41/2016/TT-NHNN. | **NEEDS_HUMAN_REVIEW** |
| 3 | `REQ-NHNN-27-SAFETY-FUND` | Quy định trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân. | `[Thông tư 27/2024/TT-NHNN | Điều 5. Trích nộp Quỹ bảo đảm an toàn | 93f5c884-df3e-11f0-bcf2-f34d1dbe48ff]` | KHÔNG CÓ (Thiếu văn bản quy định nội bộ INTERNAL_POLICY trong corpus đối chiếu) | **CHUA_DU_BANG_CHUNG** | Hệ thống ghi nhận yêu cầu quy định NHNN nhưng không tìm thấy tệp quy định nội bộ (INTERNAL_POLICY) tương ứng trong corpus để đối chiếu bằng chứng hai phía. Cần bổ sung tài liệu nội bộ trước khi đánh giá. | **NEEDS_HUMAN_REVIEW** |
| 4 | `REQ-NHNN-56-LICENSING` | Quy định về hồ sơ, thủ tục cấp Giấy phép lần đầu của ngân hàng thương mại và chi nhánh ngân hàng nước ngoài. | `[Thông tư 56/2024/TT-NHNN | Điều 8. Hồ sơ cấp phép | 93f66578-df3e-11f0-96dd-1d7f48a0b5c4]` | KHÔNG CÓ (Thiếu văn bản quy định nội bộ INTERNAL_POLICY trong corpus đối chiếu) | **CHUA_DU_BANG_CHUNG** | Hệ thống ghi nhận yêu cầu quy định NHNN nhưng không tìm thấy tệp quy định nội bộ (INTERNAL_POLICY) tương ứng trong corpus để đối chiếu bằng chứng hai phía. Cần bổ sung tài liệu nội bộ trước khi đánh giá. | **NEEDS_HUMAN_REVIEW** |

---

## 3. Quy chuẩn Đánh giá & Nguyên tắc Kiểm toán AI

1. **Đánh giá bằng chứng hai phía**: Phân loại rõ ràng các trạng thái `DAP_UNG` (Đáp ứng), `CHENH_LECH` (Chênh lệch / Nghiêm ngặt hơn), `THIEU` (Thiếu quy định), `CHUA_DU_BANG_CHUNG` (Chưa đủ bằng chứng).
2. **Không kết luận chỉ từ similarity score**: Điểm số tương đồng vector chỉ dùng để xếp hạng ứng viên, kết luận dựa trên phân tích nội dung pháp lý.
3. **Bắt buộc Human Review**: 100% kết quả đều được gán cờ `NEEDS_HUMAN_REVIEW` để chuyên viên tuân thủ/kiểm toán thực hiện thẩm định lại.

## STATUS SUMMARY

```text
GAP CHECKER: PASS
HUMAN REVIEW REQUIRED: YES
```