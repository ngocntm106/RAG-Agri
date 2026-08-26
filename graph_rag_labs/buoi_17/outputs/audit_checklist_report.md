# BÁO CÁO BẢN NHÁP CHECKLIST KIỂM TOÁN (UC4 — AI AUDIT CHECKLIST GENERATOR)
## Hệ thống Sinh Checklist Kiểm toán theo Phạm vi Domain & Unit Agribank

- **LLM Provider:** `OLLAMA`
- **Tổng số lượt sinh checklist:** 2
- **Tổng số hạng mục kiểm toán đã tạo:** 5
- **Guardrail Bảo mật:** 100% kết quả đều gắn cờ `review_status = NEEDS_HUMAN_REVIEW`.

## 1. Bảng Tổng hợp Checklist Kiểm toán (`audit_checklist_results.csv`)
| STT | Mã Mục | Lĩnh vực (Domain) | Đơn vị áp dụng (Unit) | Câu hỏi Kiểm toán | Mức độ Rủi ro | Trích dẫn (Citation) | Trạng thái Review |
|---|---|---|---|---|---|---|---|
| 1 | `CHK_KHO_01` | An toàn Kho quỹ & Vận chuyển | Chi nhánh loại I & Phòng Giao dịch | Chi nhánh/Phòng giao dịch có bố trí xe ô tô bọc th... | 🔴 **HIGH** | `[100/QĐ-NHNO-AT - Quy định nội bộ số 100...` | `NEEDS_HUMAN_REVIEW` |
| 2 | `CHK_KHO_02` | An toàn Kho quỹ & Vận chuyển | Chi nhánh loại I & Phòng Giao dịch | Đơn vị có tuân thủ nghiêm ngặt quy định không mang... | 🔴 **HIGH** | `[100/QĐ-NHNO-AT - Quy định nội bộ số 100...` | `NEEDS_HUMAN_REVIEW` |
| 3 | `CHK_KHO_03` | An toàn Kho quỹ & Vận chuyển | Chi nhánh loại I & Phòng Giao dịch | Đơn vị có mua bảo hiểm rủi ro tiền mặt tại kho và ... | 🟡 **MEDIUM** | `[180/QĐ-NHNO-BH - Quy định nội bộ số 180...` | `NEEDS_HUMAN_REVIEW` |
| 4 | `CHK_IT_01` | Bảo mật CNTT & AI | Khối CNTT & Trung tâm Dữ liệu | Khối CNTT có áp dụng chuẩn mã hóa AES-128 trở lên ... | 🔴 **HIGH** | `[600/QC-NHNO-CNTT - Quy chế bảo mật CNTT...` | `NEEDS_HUMAN_REVIEW` |
| 5 | `CHK_IT_02` | Bảo mật CNTT & AI | Khối CNTT & Trung tâm Dữ liệu | Hệ thống AI RAG có lưu trữ Audit Log tối thiểu 12 ... | 🔴 **HIGH** | `[600/QC-NHNO-CNTT - Quy chế bảo mật CNTT...` | `NEEDS_HUMAN_REVIEW` |

## 2. Chi tiết Từng Hạng mục Kiểm toán
### 📋 Hạng mục 1: [CHK_KHO_01] - An toàn Kho quỹ & Vận chuyển
- **Phạm vi đơn vị:** Chi nhánh loại I & Phòng Giao dịch
- **Mức độ rủi ro:** `HIGH`
- **Câu hỏi kiểm toán:** "Chi nhánh/Phòng giao dịch có bố trí xe ô tô bọc thép chuyên dùng và 02 bảo vệ chuyên trách khi vận chuyển tiền mặt từ 3 tỷ đồng trở lên hoặc đi liên tỉnh không?"
- **Mô tả rủi ro:** Thất thoát tiền mặt, rủi ro an ninh cướp bóc trên đường vận chuyển.
- **Căn cứ pháp lý/Quy định:** [100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-NHNO-AT | Điều 12]
- **Trạng thái phê duyệt:** `NEEDS_HUMAN_REVIEW` (Yêu cầu Trưởng đoàn kiểm toán phê duyệt trước khi đi thực địa)

### 📋 Hạng mục 2: [CHK_KHO_02] - An toàn Kho quỹ & Vận chuyển
- **Phạm vi đơn vị:** Chi nhánh loại I & Phòng Giao dịch
- **Mức độ rủi ro:** `HIGH`
- **Câu hỏi kiểm toán:** "Đơn vị có tuân thủ nghiêm ngặt quy định không mang chìa khóa kho tiền ra khỏi trụ sở làm việc trong mọi trường hợp không?"
- **Mô tả rủi ro:** Lạm dụng chìa khóa, chiếm đoạt tài sản, thất thoát tiền mặt trong kho.
- **Căn cứ pháp lý/Quy định:** [100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-NHNO-AT | Điều 1]
- **Trạng thái phê duyệt:** `NEEDS_HUMAN_REVIEW` (Yêu cầu Trưởng đoàn kiểm toán phê duyệt trước khi đi thực địa)

### 📋 Hạng mục 3: [CHK_KHO_03] - An toàn Kho quỹ & Vận chuyển
- **Phạm vi đơn vị:** Chi nhánh loại I & Phòng Giao dịch
- **Mức độ rủi ro:** `MEDIUM`
- **Câu hỏi kiểm toán:** "Đơn vị có mua bảo hiểm rủi ro tiền mặt tại kho và tiền mặt trên đường vận chuyển (BBB Insurance) với định mức bồi thường 100% không?"
- **Mô tả rủi ro:** Tự chịu tổn thất tài chính khi xảy ra sự cố bất khả kháng hoặc thảm họa thiên tai.
- **Căn cứ pháp lý/Quy định:** [180/QĐ-NHNO-BH - Quy định nội bộ số 180/QĐ-NHNO-BH | Điều 5]
- **Trạng thái phê duyệt:** `NEEDS_HUMAN_REVIEW` (Yêu cầu Trưởng đoàn kiểm toán phê duyệt trước khi đi thực địa)

### 📋 Hạng mục 4: [CHK_IT_01] - Bảo mật CNTT & AI
- **Phạm vi đơn vị:** Khối CNTT & Trung tâm Dữ liệu
- **Mức độ rủi ro:** `HIGH`
- **Câu hỏi kiểm toán:** "Khối CNTT có áp dụng chuẩn mã hóa AES-128 trở lên đối với dữ liệu tri thức RAG và dữ liệu cá nhân khách hàng trên ứng dụng AI không?"
- **Mô tả rủi ro:** Rò rỉ dữ liệu tài chính nhạy cảm và thông tin riêng tư của khách hàng ngân hàng.
- **Căn cứ pháp lý/Quy định:** [600/QC-NHNO-CNTT - Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT | Điều 9]
- **Trạng thái phê duyệt:** `NEEDS_HUMAN_REVIEW` (Yêu cầu Trưởng đoàn kiểm toán phê duyệt trước khi đi thực địa)

### 📋 Hạng mục 5: [CHK_IT_02] - Bảo mật CNTT & AI
- **Phạm vi đơn vị:** Khối CNTT & Trung tâm Dữ liệu
- **Mức độ rủi ro:** `HIGH`
- **Câu hỏi kiểm toán:** "Hệ thống AI RAG có lưu trữ Audit Log tối thiểu 12 tháng bao gồm user_id, action, timestamp, document_id và citation_id không?"
- **Mô tả rủi ro:** Vi phạm quy định quản trị an ninh thông tin, không thể truy vết vi phạm khi xảy ra sự cố.
- **Căn cứ pháp lý/Quy định:** [600/QC-NHNO-CNTT - Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT | Điều 16]
- **Trạng thái phê duyệt:** `NEEDS_HUMAN_REVIEW` (Yêu cầu Trưởng đoàn kiểm toán phê duyệt trước khi đi thực địa)

---

## 3. Kết luận Nghiệm thu Engine
AUDIT CHECKLIST ENGINE: PASS
TOTAL CHECKLIST ITEMS GENERATED: 5
HUMAN REVIEW GUARDRAIL: PASS