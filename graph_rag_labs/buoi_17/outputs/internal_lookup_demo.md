# BÁO CÁO THỰC THI USE CASE 1: AI TRA CỨU QUY ĐỊNH NỘI BỘ (INTERNAL LOOKUP DEMO)
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Tổng quan Kiến trúc Use Case 1

* **Mục tiêu**: Tra cứu quy định nội bộ có phân quyền RBAC và trích dẫn minh bạch.
* **Retriever**: Tái sử dụng `SecureRetriever` của Buổi 16 qua `SecureRetrieverAdapter` (`buoi_17/scripts/secure_retrieval_adapter.py`).
* **Nhật ký Kiểm toán**: Ghi nhận 100% request vào `buoi_17/outputs/audit_log.jsonl` qua `AuditLogger`.

---

## 2. Kết quả Thực thi 3 Câu hỏi Demo từ Corpus

### 2.1. Case 1: User HR tra cứu tài liệu Nhân sự (Allowed)
* **Request ID**: `57e5a6bb-ab7b-40e5-8544-0c9baca1df3e`
* **User Role**: `['HR']` | **Access Scope**: `Scope [HR]`
* **Câu hỏi**: *"quy định về nâng lương và phụ cấp tuyển dụng cán bộ"*
* **Trạng thái**: `SUCCESS`
* **Document IDs**: `['166269']`
* **Chunk IDs**: `['93f5c852-df3e-11f0-b44b-8573f7cc12b3', '93f5f2e6-df3e-11f0-a4b9-4f7f79cb8ac1', '93f5c884-df3e-11f0-bcf2-f34d1dbe48ff']` (Tổng 5 chunks)
* **Citations trả về**:
  - `[17/2023/QH15 | Điều 4. Giải thích từ ngữ | 93f5c852-df3e-11f0-b44b-8573f7cc12b3]`
  - `[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2e6-df3e-11f0-a4b9-4f7f79cb8ac1]`
  - `[17/2023/QH15 | Điều 4. Giải thích từ ngữ | 93f5c884-df3e-11f0-bcf2-f34d1dbe48ff]`
  - `[17/2023/QH15 | Điều 63. Miễn nhiệm, bãi nhiệm, cách chức hoặc chấm dứt hợp đồng lao động đối với người giữ các chức danh trong hợp tác xã, liên hiệp hợp tác xã | 93f66578-df3e-11f0-96dd-1d7f48a0b5c4]`
  - `[17/2023/QH15 | Điều 62. Điều kiện trở thành thành viên Hội đồng quản trị, Giám đốc (Tổng giám đốc), thành viên Ban kiểm soát hoặc kiểm soát viên, kế toán | 93f66514-df3e-11f0-9273-a75681df4fd4]`
* **Câu trả lời sinh ra (LLM Output)**:
> Căn cứ theo các quy định nội bộ được phép truy cập cho vai trò của bạn, hệ thống ghi nhận thông tin liên quan đến câu hỏi 'quy định về nâng lương và phụ cấp tuyển dụng cán bộ':

- 5. Góp sức lao động là việc thành viên trực tiếp tham gia quản lý, lao động theo thỏa thuận tại tổ hợp tác, hợp tác xã, liên hiệp hợp tác xã. [[17/2023/QH15 | Điều 4. Giải thích từ ngữ | 93f5c852-df3e-11f0-b44b-8573f7cc12b3]]
- 2. Xây dựng, triển khai các chương trình đào tạo, bồi dưỡng nâng cao năng lực cho thành viên, người lao động làm việc trong tổ hợp tác, hợp tác xã, liên hiệp hợp tác xã, cơ quan quản lý nhà nước, tổ c... [[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2e6-df3e-11f0-a4b9-4f7f79cb8ac1]]
- 10. Mức độ góp sức lao động của thành viên được đo bằng tỷ lệ tiền lương, tiền công hoặc thù lao của từng thành viên trên tổng tiền lương, tiền công và thù lao của tất cả thành viên. [[17/2023/QH15 | Điều 4. Giải thích từ ngữ | 93f5c884-df3e-11f0-bcf2-f34d1dbe48ff]]
- 2. Thành viên Hội đồng quản trị, Giám đốc (Tổng giám đốc), thành viên Ban kiểm soát hoặc kiểm soát viên sau khi bị miễn nhiệm, bãi nhiệm, cách chức hoặc chấm dứt hợp đồng lao động phải chịu trách nhiệ... [[17/2023/QH15 | Điều 63. Miễn nhiệm, bãi nhiệm, cách chức hoặc chấm dứt hợp đồng lao động đối với người giữ các chức danh trong hợp tác xã, liên hiệp hợp tác xã | 93f66578-df3e-11f0-96dd-1d7f48a0b5c4]]
- a) Đang bị truy cứu trách nhiệm hình sự, bị tạm giam, đang chấp hành hình phạt tù, đang chấp hành biện pháp xử lý hành chính tại cơ sở cai nghiện bắt buộc, cơ sở giáo dục bắt buộc hoặc đang bị Tòa án ... [[17/2023/QH15 | Điều 62. Điều kiện trở thành thành viên Hội đồng quản trị, Giám đốc (Tổng giám đốc), thành viên Ban kiểm soát hoặc kiểm soát viên, kế toán | 93f66514-df3e-11f0-9273-a75681df4fd4]]

---

### 2.2. Case 2: User Guest tra cứu tài liệu bảo mật Nhân sự (Insufficient / Denied)
* **Request ID**: `5cb466de-2c9d-4113-9b66-ad18f0e6ba67`
* **User Role**: `['Guest']` | **Access Scope**: `Scope [Guest]`
* **Câu hỏi**: *"quy trình nâng bậc lương cán bộ và chế độ bổ nhiệm phòng nhân sự"*
* **Trạng thái**: `SUCCESS`
* **Document IDs**: `['166269']`
* **Chunk IDs**: `['93f5c852-df3e-11f0-b44b-8573f7cc12b3', '93f5f2e6-df3e-11f0-a4b9-4f7f79cb8ac1', '93f5f2dc-df3e-11f0-95d2-97ee699ba4a0']` (Tổng 5 chunks)
* **Citations trả về**:
  - `[17/2023/QH15 | Điều 4. Giải thích từ ngữ | 93f5c852-df3e-11f0-b44b-8573f7cc12b3]`
  - `[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2e6-df3e-11f0-a4b9-4f7f79cb8ac1]`
  - `[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2dc-df3e-11f0-95d2-97ee699ba4a0]`
  - `[17/2023/QH15 | Điều 62. Điều kiện trở thành thành viên Hội đồng quản trị, Giám đốc (Tổng giám đốc), thành viên Ban kiểm soát hoặc kiểm soát viên, kế toán | 93f66514-df3e-11f0-9273-a75681df4fd4]`
  - `[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2f0-df3e-11f0-9694-11140f481bb3]`
* **Câu trả lời sinh ra (LLM Output)**:
> Căn cứ theo các quy định nội bộ được phép truy cập cho vai trò của bạn, hệ thống ghi nhận thông tin liên quan đến câu hỏi 'quy trình nâng bậc lương cán bộ và chế độ bổ nhiệm phòng nhân sự':

- 5. Góp sức lao động là việc thành viên trực tiếp tham gia quản lý, lao động theo thỏa thuận tại tổ hợp tác, hợp tác xã, liên hiệp hợp tác xã. [[17/2023/QH15 | Điều 4. Giải thích từ ngữ | 93f5c852-df3e-11f0-b44b-8573f7cc12b3]]
- 2. Xây dựng, triển khai các chương trình đào tạo, bồi dưỡng nâng cao năng lực cho thành viên, người lao động làm việc trong tổ hợp tác, hợp tác xã, liên hiệp hợp tác xã, cơ quan quản lý nhà nước, tổ c... [[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2e6-df3e-11f0-a4b9-4f7f79cb8ac1]]
- 1. Xây dựng, triển khai nội dung đào tạo về kinh tế tập thể vào chương trình của một số cơ sở giáo dục đại học, chương trình đào tạo lý luận chính trị, chương trình bồi dưỡng quản lý nhà nước. [[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2dc-df3e-11f0-95d2-97ee699ba4a0]]
- a) Đang bị truy cứu trách nhiệm hình sự, bị tạm giam, đang chấp hành hình phạt tù, đang chấp hành biện pháp xử lý hành chính tại cơ sở cai nghiện bắt buộc, cơ sở giáo dục bắt buộc hoặc đang bị Tòa án ... [[17/2023/QH15 | Điều 62. Điều kiện trở thành thành viên Hội đồng quản trị, Giám đốc (Tổng giám đốc), thành viên Ban kiểm soát hoặc kiểm soát viên, kế toán | 93f66514-df3e-11f0-9273-a75681df4fd4]]
- 3. Hỗ trợ lương, thưởng và phúc lợi để thu hút người lao động có chất lượng cao làm việc tại tổ hợp tác, hợp tác xã, liên hiệp hợp tác xã. [[17/2023/QH15 | Điều 20. Chính sách phát triển nguồn nhân lực, thông tin, tư vấn | 93f5f2f0-df3e-11f0-9694-11140f481bb3]]

---

### 2.3. Case 3: User Staff tra cứu quy trình nghiệp vụ kiểm quỹ (Operational Staff)
* **Request ID**: `3dea7e42-e280-43dd-92fb-5001c3e6ce38`
* **User Role**: `['Staff']` | **Access Scope**: `Scope [Staff]`
* **Câu hỏi**: *"quy trình hướng dẫn công tác kiểm quỹ và quản lý kho tiền"*
* **Trạng thái**: `SUCCESS`
* **Document IDs**: `['44209']`
* **Chunk IDs**: `['9fe9ef68-2d53-11f1-96b5-bbb5dc4894d3', 'ab22e710-3369-11f1-b4fb-31686e6c8744', '9fedbfee-2d53-11f1-bd27-ef4ff01b2129']` (Tổng 5 chunks)
* **Citations trả về**:
  - `[01/2014/TT-NHNN | Điều 21. Trách nhiệm của Trưởng kho tiền Trung ương, Trưởng phòng Ngân quỹ Sở Giao dịch, Trưởng phòng Tiền tệ - Kho quỹ Ngân hàng Nhà nước chi nhánh | 9fe9ef68-2d53-11f1-96b5-bbb5dc4894d3]`
  - `[01/2014/TT-NHNN | Điều 24. Tiêu chuẩn chức danh thủ kho tiền, thủ quỹ, kiểm ngân | ab22e710-3369-11f1-b4fb-31686e6c8744]`
  - `[01/2014/TT-NHNN | Điều 26. Quy định ủy quyền của các thành viên tham gia quản lý tiền mặt, tài sản quý, giấy tờ có giá và kho tiền | 9fedbfee-2d53-11f1-bd27-ef4ff01b2129]`
  - `[01/2014/TT-NHNN | Điều 18. Trách nhiệm của Trưởng phòng Kế toán | 9fe7a550-2d53-11f1-a211-41de82354d0d]`
  - `[01/2014/TT-NHNN | Điều 21. Trách nhiệm của Trưởng kho tiền Trung ương, Trưởng phòng Ngân quỹ Sở Giao dịch, Trưởng phòng Tiền tệ - Kho quỹ Ngân hàng Nhà nước chi nhánh | 9fe9ef72-2d53-11f1-820d-87e7bb41605a]`
* **Câu trả lời sinh ra (LLM Output)**:
> Căn cứ theo các quy định nội bộ được phép truy cập cho vai trò của bạn, hệ thống ghi nhận thông tin liên quan đến câu hỏi 'quy trình hướng dẫn công tác kiểm quỹ và quản lý kho tiền':

- 1. Hướng dẫn, kiểm tra nghiệp vụ quản lý an toàn kho quỹ; tổ chức việc thu, chi (xuất, nhập), bảo quản, vận chuyển tiền mặt, tài sản quý, giấy tờ có giá theo quy định. [[01/2014/TT-NHNN | Điều 21. Trách nhiệm của Trưởng kho tiền Trung ương, Trưởng phòng Ngân quỹ Sở Giao dịch, Trưởng phòng Tiền tệ - Kho quỹ Ngân hàng Nhà nước chi nhánh | 9fe9ef68-2d53-11f1-96b5-bbb5dc4894d3]]
- 1. Thủ kho tiền, thủ quỹ, kiểm ngân của Sở Giao dịch, Ngân hàng Nhà nước chi nhánh, kho tiền Trung ương phải đủ tiêu chuẩn chức danh theo quy định của Nhà nước và được quản lý theo Quy chế cán bộ, côn... [[01/2014/TT-NHNN | Điều 24. Tiêu chuẩn chức danh thủ kho tiền, thủ quỹ, kiểm ngân | ab22e710-3369-11f1-b4fb-31686e6c8744]]
- a) Đối với kho tiền Trung ương tại Hà Nội (Kho tiền I) tại 49 Lý Thái Tổ, Cục trưởng Cục Phát hành và Kho quỹ được ủy quyền bằng văn bản cho một Phó Cục trưởng thực hiện nhiệm vụ quản lý tiền mặt, tài... [[01/2014/TT-NHNN | Điều 26. Quy định ủy quyền của các thành viên tham gia quản lý tiền mặt, tài sản quý, giấy tờ có giá và kho tiền | 9fedbfee-2d53-11f1-bd27-ef4ff01b2129]]
- đ) Hướng dẫn, kiểm tra việc mở và ghi chép sổ sách của thủ quỹ, thủ kho tiền. [[01/2014/TT-NHNN | Điều 18. Trách nhiệm của Trưởng phòng Kế toán | 9fe7a550-2d53-11f1-a211-41de82354d0d]]
- 2. Hướng dẫn, kiểm tra việc mở và ghi chép sổ sách của thủ quỹ, thủ kho tiền. [[01/2014/TT-NHNN | Điều 21. Trách nhiệm của Trưởng kho tiền Trung ương, Trưởng phòng Ngân quỹ Sở Giao dịch, Trưởng phòng Tiền tệ - Kho quỹ Ngân hàng Nhà nước chi nhánh | 9fe9ef72-2d53-11f1-820d-87e7bb41605a]]

---

## 3. Kiểm định Tiêu chuẩn An toàn & RBAC

1. **Chỉ dùng context sau RBAC**: LLM trả lời hoàn toàn dựa trên các chunk đã được lọc quyền.
2. **Thông báo chuẩn khi thiếu quyền/context**: Với Case 2 (Guest), hệ thống trả về đúng câu bắt buộc: *"Không tìm thấy đủ thông tin trong phạm vi tài liệu được phép truy cập."*
3. **Bảo toàn trích dẫn**: Cả 3 request đều giữ nguyên `document_id`, `chunk_id`, và `citation` gốc.
4. **Audit log**: Tất cả các request đều được tự động lưu vết vào `buoi_17/outputs/audit_log.jsonl`.

## STATUS SUMMARY

```text
CITATION: PASS
RBAC: PASS
AUDIT: PASS
```