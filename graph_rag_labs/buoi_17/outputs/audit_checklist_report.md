# BÁO CÁO BẢN NHÁP CHECKLIST KIỂM TOÁN (UC4 — AI AUDIT CHECKLIST GENERATOR)
## Hệ thống Sinh Checklist Kiểm toán theo Phạm vi Domain & Unit Agribank

- **Số lượng Domain đã thử nghiệm:** 2
- **Tổng số đầu mục Checklist đã tạo (`CHECKLIST ITEMS CREATED`):** 5
- **Citation Gốc:** 100% các mục checklist đều được gắn Citation chính xác (`CITATIONS ATTACHED: YES`).
- **Guardrail Bảo mật:** Tất cả kết quả đều gắn cờ `review_status = NEEDS_HUMAN_REVIEW`.

## 1. Danh sách Bảng Checklist Kiểm toán (`audit_checklist_results.csv`)
| STT | Mã Mục | Domain | Scope Đơn vị | Câu hỏi Kiểm toán | Mức Rủi ro | Citation Văn bản Gốc | Trạng thái Review |
|---|---|---|---|---|---|---|---|
| 1 | `CHK_KHO_01` | An toàn Kho quỹ & Vận chuyển | Chi nhánh loại I & Phòng Giao dịch | Chi nhánh/Phòng giao dịch có bố trí xe ô tô bọc thép chuyên dùng và 02 bảo vệ chuyên trách khi vận chuyển tiền mặt từ 3 tỷ đồng trở lên hoặc đi liên tỉnh không? | 🔴 **HIGH** | `[100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-N...` | `NEEDS_HUMAN_REVIEW` |
| 2 | `CHK_KHO_02` | An toàn Kho quỹ & Vận chuyển | Chi nhánh loại I & Phòng Giao dịch | Đơn vị có tuân thủ nghiêm ngặt quy định không mang chìa khóa kho tiền ra khỏi trụ sở làm việc trong mọi trường hợp không? | 🔴 **HIGH** | `[100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-N...` | `NEEDS_HUMAN_REVIEW` |
| 3 | `CHK_KHO_03` | An toàn Kho quỹ & Vận chuyển | Chi nhánh loại I & Phòng Giao dịch | Đơn vị có mua bảo hiểm rủi ro tiền mặt tại kho và tiền mặt trên đường vận chuyển (BBB Insurance) với định mức bồi thường 100% không? | 🟡 **MEDIUM** | `[180/QĐ-NHNO-BH - Quy định nội bộ số 180/QĐ-N...` | `NEEDS_HUMAN_REVIEW` |
| 4 | `CHK_IT_01` | Bảo mật CNTT & AI | Khối CNTT & Trung tâm Dữ liệu | Khối CNTT có áp dụng chuẩn mã hóa AES-128 trở lên đối với dữ liệu tri thức RAG và dữ liệu cá nhân khách hàng trên ứng dụng AI không? | 🔴 **HIGH** | `[600/QC-NHNO-CNTT - Quy chế bảo mật CNTT số 6...` | `NEEDS_HUMAN_REVIEW` |
| 5 | `CHK_IT_02` | Bảo mật CNTT & AI | Khối CNTT & Trung tâm Dữ liệu | Hệ thống AI RAG có lưu trữ Audit Log tối thiểu 12 tháng bao gồm user_id, action, timestamp, document_id và citation_id không? | 🔴 **HIGH** | `[600/QC-NHNO-CNTT - Quy chế bảo mật CNTT số 6...` | `NEEDS_HUMAN_REVIEW` |

## 2. Chi tiết Các Mục Checklist theo Domain

### 📋 Domain: An toàn Kho quỹ (Đơn vị: Chi nhánh loại I & Phòng Giao dịch)
#### 📌 [CHK_KHO_01] Chi nhánh/Phòng giao dịch có bố trí xe ô tô bọc thép chuyên dùng và 02 bảo vệ chuyên trách khi vận chuyển tiền mặt từ 3 tỷ đồng trở lên hoặc đi liên tỉnh không?
- **Rủi ro tiềm ẩn:** Thất thoát tiền mặt, rủi ro an ninh cướp bóc trên đường vận chuyển.
- **Mức độ rủi ro (Risk Level):** `HIGH`
- **Trích dẫn quy định gốc (Source Citation):** [100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-NHNO-AT | Điều 12]
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Kiểm toán viên rà soát thực tế tại đơn vị trước khi ghi nhận biên bản.

#### 📌 [CHK_KHO_02] Đơn vị có tuân thủ nghiêm ngặt quy định không mang chìa khóa kho tiền ra khỏi trụ sở làm việc trong mọi trường hợp không?
- **Rủi ro tiềm ẩn:** Lạm dụng chìa khóa, chiếm đoạt tài sản, thất thoát tiền mặt trong kho.
- **Mức độ rủi ro (Risk Level):** `HIGH`
- **Trích dẫn quy định gốc (Source Citation):** [100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-NHNO-AT | Điều 1]
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Kiểm toán viên rà soát thực tế tại đơn vị trước khi ghi nhận biên bản.

#### 📌 [CHK_KHO_03] Đơn vị có mua bảo hiểm rủi ro tiền mặt tại kho và tiền mặt trên đường vận chuyển (BBB Insurance) với định mức bồi thường 100% không?
- **Rủi ro tiềm ẩn:** Tự chịu tổn thất tài chính khi xảy ra sự cố bất khả kháng hoặc thảm họa thiên tai.
- **Mức độ rủi ro (Risk Level):** `MEDIUM`
- **Trích dẫn quy định gốc (Source Citation):** [180/QĐ-NHNO-BH - Quy định nội bộ số 180/QĐ-NHNO-BH | Điều 5]
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Kiểm toán viên rà soát thực tế tại đơn vị trước khi ghi nhận biên bản.


### 📋 Domain: Bảo mật CNTT & AI (Đơn vị: Khối CNTT & Trung tâm Dữ liệu)
#### 📌 [CHK_IT_01] Khối CNTT có áp dụng chuẩn mã hóa AES-128 trở lên đối với dữ liệu tri thức RAG và dữ liệu cá nhân khách hàng trên ứng dụng AI không?
- **Rủi ro tiềm ẩn:** Rò rỉ dữ liệu tài chính nhạy cảm và thông tin riêng tư của khách hàng ngân hàng.
- **Mức độ rủi ro (Risk Level):** `HIGH`
- **Trích dẫn quy định gốc (Source Citation):** [600/QC-NHNO-CNTT - Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT | Điều 9]
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Kiểm toán viên rà soát thực tế tại đơn vị trước khi ghi nhận biên bản.

#### 📌 [CHK_IT_02] Hệ thống AI RAG có lưu trữ Audit Log tối thiểu 12 tháng bao gồm user_id, action, timestamp, document_id và citation_id không?
- **Rủi ro tiềm ẩn:** Vi phạm quy định quản trị an ninh thông tin, không thể truy vết vi phạm khi xảy ra sự cố.
- **Mức độ rủi ro (Risk Level):** `HIGH`
- **Trích dẫn quy định gốc (Source Citation):** [600/QC-NHNO-CNTT - Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT | Điều 16]
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Kiểm toán viên rà soát thực tế tại đơn vị trước khi ghi nhận biên bản.

---

## 3. Kết luận Nghiệm thu Engine
CHECKLIST GENERATOR ENGINE: PASS
CHECKLIST ITEMS CREATED: 5
CITATIONS ATTACHED: YES