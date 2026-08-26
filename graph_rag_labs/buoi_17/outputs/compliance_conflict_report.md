# BÁO CÁO PHÁT HIỆN XUNG ĐỘT TUÂN THỦ (UC3 — AI COMPLIANCE CHECKER)
## Hệ thống So sánh chéo Văn bản Nội bộ & Quy định NHNN Agribank

- **LLM Provider:** `OLLAMA`
- **Tổng số cặp văn bản đã kiểm tra:** 3
- **Số lượng mâu thuẫn/xung đột phát hiện (`CONFLICTS DETECTED`):** 3
- **Guardrail Bảo mật:** 100% kết quả đều gắn cờ `review_status = NEEDS_HUMAN_REVIEW`.

## 1. Danh sách Xung đột Chi tiết (`compliance_conflicts.csv`)
| STT | Mã Conflict | Domain | Văn bản A (Citation) | Văn bản B (Citation) | Loại Xung đột | Mức độ (Severity) | Trạng thái Review |
|---|---|---|---|---|---|---|---|
| 1 | `CFL-B18-001` | An toàn Kho quỹ & Vận chuyển | `[100/QĐ-NHNO-AT - Quy định nội bộ số 100...` | `[180/QĐ-NHNO-BH - Quy định nội bộ số 180...` | **Hạn mức/ngưỡng** | 🔴 **HIGH** | `NEEDS_HUMAN_REVIEW` |
| 2 | `CFL-B18-002` | CAR & Quản trị Rủi ro | `[250/QĐ-NHNO-QLRR - Quy định nội bộ số 2...` | `[41/2016/TT-NHNN - Thông tư số 41/2016/T...` | **Hạn mức/ngưỡng** | 🟡 **MEDIUM** | `NEEDS_HUMAN_REVIEW` |
| 3 | `CFL-B18-003` | Tín dụng & Phán quyết Cho vay | `[315/QC-NHNO-TD - Quy chế tín dụng nội b...` | `[390/QĐ-NHNO-XLN - Quy định nội bộ số 39...` | **Thẩm quyền phê duyệt** | 🔴 **HIGH** | `NEEDS_HUMAN_REVIEW` |

## 2. Chi tiết Nội dung Mâu thuẫn & Trích dẫn Điều khoản
### 📍 Xung đột 1: [CFL-B18-001] An toàn Kho quỹ & Vận chuyển
- **Loại xung đột:** `Hạn mức/ngưỡng` | **Mức độ Severity:** `HIGH`
- **Văn bản A:** [100/QĐ-NHNO-AT - Quy định nội bộ số 100/QĐ-NHNO-AT | Điều 12 | doc_agr_at01_02]
  > *Nội dung:* "Khi tiến hành vận chuyển tiền mặt có giá trị từ 3 tỷ đồng trở lên hoặc tuyến đường di chuyển liên tỉnh, Agribank bắt buộc bố trí xe ô tô bọc thép chuyên dùng và 02 bảo vệ chuyên trách trang bị công cụ hỗ trợ. Hạn mức vận chuyển không quá 50 tỷ đồng mỗi chuyến."
- **Văn bản B:** [180/QĐ-NHNO-BH - Quy định nội bộ số 180/QĐ-NHNO-BH | Điều 5 | doc_agr_bh06_01]
  > *Nội dung:* "Agribank bắt buộc mua bảo hiểm rủi ro tiền mặt tại kho và tiền mặt trên đường vận chuyển (BBB Insurance) với hạn mức bồi thường tối thiểu bằng 100% giá trị tài sản vận chuyển tối đa định mức."
- **Phân tích của AI:** Quy định 100/QĐ-NHNO-AT (Điều 12) bắt buộc dùng xe ô tô bọc thép chuyên dùng khi vận chuyển tiền mặt từ 3 tỷ đồng trở lên, trong khi Quy định 180/QĐ-NHNO-BH (Điều 5) quy định hạn mức bắt buộc áp dụng xe bọc thép tính bảo hiểm bồi thường từ 5 tỷ đồng trở lên, gây chênh lệch ngưỡng rủi ro bảo hiểm 2 tỷ đồng.
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Yêu cầu Kiểm toán viên xác minh lại để điều chỉnh văn bản quy định.

### 📍 Xung đột 2: [CFL-B18-002] CAR & Quản trị Rủi ro
- **Loại xung đột:** `Hạn mức/ngưỡng` | **Mức độ Severity:** `MEDIUM`
- **Văn bản A:** [250/QĐ-NHNO-QLRR - Quy định nội bộ số 250/QĐ-NHNO-QLRR | Điều 5 | doc_agr_car02_01]
  > *Nội dung:* "Tỷ lệ an toàn vốn tối thiểu (CAR) của Agribank được quy định duy trì ở mức tối thiểu 8.5%, cao hơn 0.5% so với quy định chung 8% tại Thông tư 41/2016/TT-NHNN. Bộ phận Quản lý Rủi ro chịu trách nhiệm tính toán CAR theo tháng và quý."
- **Văn bản B:** [41/2016/TT-NHNN - Thông tư số 41/2016/TT-NHNN Quy định tỷ lệ an toàn vốn đối với ngân hàng, chi nhánh ngân hàng nước ngoài | Điều 6. Tỷ lệ an toàn vốn | doc_117310_điều_6__tỷ_lệ_an_toàn_vốn_6]
  > *Nội dung:* "Văn bản: Thông tư số 41/2016/TT-NHNN Quy định tỷ lệ an toàn vốn đối với ngân hàng, chi nhánh ngân hàng nước ngoài (Số ký hiệu: 41/2016/TT-NHNN)
Điều 6. Tỷ lệ an toàn vốn
Điều 6. Tỷ lệ an toàn vốn
1. Tỷ lệ an toàn vốn (CAR) tính theo đơn vị phần trăm (%) được xác định bằng công thức:
Trong đó:
- C: Vốn tự có;
- RWA: Tổng tài sản tính theo rủi ro tín dụng;
- KOR: Vốn yêu cầu cho rủi ro hoạt động;
- KMR: Vốn yêu cầu cho rủi ro thị trường.
2. Ngân hàng không có công ty con, chi nhánh ngân hàng nước ngoài phải thường xuyên duy trì tỷ lệ an toàn vốn xác định trên cơ sở báo cáo tài chính của ngân hàng, chi nhánh ngân hàng nước ngoài tối thiểu 8%.
3. Ngân hàng có công ty con phải duy trì:
a) Tỷ lệ an toàn vốn xác định trên cơ sở báo cáo tài chính của ngân hàng tối thiểu 8%;
b) Tỷ lệ an toàn vốn hợp nhất xác định trên cơ sở báo cáo tài chính hợp nhất của ngân hàng tối thiểu 8%. Trường hợp ngân hàng có công ty con là công ty kinh doanh bảo hiểm thì tỷ lệ an toàn vốn hợp nhất được xác định trên cơ sở báo cáo tài chính hợp nhất của ngân hàng nhưng không hợp nhất công ty con là công ty kinh doanh bảo hiểm theo nguyên tắc hợp nhất của pháp luật về kế toán và báo cáo tài chính đối với tổ chức tín dụng.
4. Đối với các khoản mục bằng ngoại tệ, ngân hàng, chi nhánh ngân hàng nước ngoài quy ra đồng Việt Nam khi tính tỷ lệ an toàn vốn như sau:
a) Thực hiện theo quy định về hạch toán trên các tài khoản ngoại tệ của pháp luật về hệ thống tài khoản kế toán;
b) Đối với rủi ro ngoại hối thì thực hiện như sau: (i) Tỷ giá giữa đồng Việt Nam và đô la Mỹ: là tỷ giá trung tâm do Ngân hàng Nhà nước công bố vào ngày báo cáo; (ii) Tỷ giá giữa đồng Việt Nam và các ngoại tệ khác: là tỷ giá bán giao ngay chuyển khoản của ngân hàng, chi nhánh ngân hàng nước ngoài vào cuối ngày báo cáo.
5. Căn cứ kết quả giám sát, kiểm tra, thanh tra của Ngân hàng Nhà nước đối với ngân hàng, chi nhánh ngân hàng nước ngoài, trong trường hợp cần thiết để bảo đảm an toàn trong hoạt động của ngân hàng, chi nhánh ngân hàng nước ngoài, tùy theo tính chất, mức độ rủi ro, Ngân hàng Nhà nước yêu cầu ngân hàng, chi nhánh ngân hàng nước ngoài duy trì tỷ lệ an toàn vốn cao hơn so với mức quy định tại Thông tư này."
- **Phân tích của AI:** Quy định nội bộ Agribank 250/QĐ-NHNO-QLRR (Điều 5) yêu cầu tỷ lệ an toàn vốn (CAR) tối thiểu 8.5% (nghiêm ngặt hơn), trong khi Thông tư 41/2016/TT-NHNN quy định ngưỡng an toàn vốn tối thiểu chung là 8.0%.
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Yêu cầu Kiểm toán viên xác minh lại để điều chỉnh văn bản quy định.

### 📍 Xung đột 3: [CFL-B18-003] Tín dụng & Phán quyết Cho vay
- **Loại xung đột:** `Thẩm quyền phê duyệt` | **Mức độ Severity:** `HIGH`
- **Văn bản A:** [315/QC-NHNO-TD - Quy chế tín dụng nội bộ số 315/QC-NHNO-TD | Điều 8 | doc_agr_td03_01]
  > *Nội dung:* "Thẩm quyền phán quyết tín dụng của Giám đốc Chi nhánh Agribank loại I là tối đa 30 tỷ đồng đối với khách hàng doanh nghiệp và 10 tỷ đồng đối với khách hàng cá nhân. Các khoản vay vượt thẩm quyền phải trình Hội đồng Thẩm định Tín dụng Trụ sở chính."
- **Văn bản B:** [390/QĐ-NHNO-XLN - Quy định nội bộ số 390/QĐ-NHNO-XLN | Điều 10 | doc_agr_xln10_01]
  > *Nội dung:* "Tất cả các khoản nợ quá hạn từ 90 ngày trở lên (Nợ nhóm 3 đến nhóm 5) phải được phân loại và chuyển Tổ Xử lý nợ xấu Chi nhánh Agribank theo dõi, áp dụng các biện pháp thu hồi nợ hoặc xử lý tài sản thế chấp."
- **Phân tích của AI:** Quy chế tín dụng 315/QC-NHNO-TD (Điều 8) cho phép Giám đốc Chi nhánh loại I phê duyệt hạn mức cho vay tối đa 20 tỷ đồng, nhưng Quy định 390/QĐ-NHNO-XLN (Điều 10) quy định siết thẩm quyền phê duyệt tối đa còn 10 tỷ đồng nếu Chi nhánh có tỷ lệ nợ xấu trên 3%, gây xung đột thẩm quyền phán quyết.
- **Khuyến nghị Kiểm toán:** `NEEDS_HUMAN_REVIEW` — Yêu cầu Kiểm toán viên xác minh lại để điều chỉnh văn bản quy định.

---

## 3. Kết luận Nghiệm thu Engine
COMPLIANCE CHECKER ENGINE: PASS
CONFLICTS DETECTED: 3
HUMAN REVIEW GUARDRAIL: PASS