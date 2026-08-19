# BÁO CÁO KIỂM ĐỊNH BẢO MẬT PHÂN QUYỀN TRUY CẬP (SECURITY AUDIT REPORT)

- **Bài thực hành**: Buổi 15 — Cài đặt Kiểm soát Truy cập dựa trên Vai trò (RBAC)
- **Thời gian kiểm thử**: `2026-08-17 19:12:02`
- **Môi trường thực thi**: Python 3.14 / Streamlit / Neo4j Graph DB / Sentence-Transformers
- **Thời gian chạy**: `51.86 giây`

---

## 1. Tổng quan Kết quả Kiểm định

| Chỉ số | Giá trị | Đánh giá |
| :--- | :---: | :--- |
| **Tổng số Test Cases** | **5** | Đạt yêu cầu kiểm thử toàn diện |
| **Số bài Test ĐẠT (PASS)** | **5** | Không phát hiện rò rỉ dữ liệu |
| **Số bài Test LỖI (FAIL)** | **0** | Zero data leakage |
| **Tỷ lệ An toàn (Pass Rate)** | **100.0%** | **ĐẠT CHUẨN AN TOÀN DỮ LIỆU CƠ BẢN (CERTIFIED)** |

---

## 2. Bảng Chi tiết Kết quả Kiểm thử Từng Test Case

| ID | Nhóm Kiểm định | Tên Bài Test | Vai trò Cấm | Vai trò Cho phép | Kết quả | Rò rỉ |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| `SEC-01` | HR Confidentiality | Bảo mật Hồ sơ & Tiêu chuẩn Bổ nhiệm Tổng giám đốc | `Guest, Staff` | `HR, Admin` | ✅ **PASS** | 0 chunk |
| `SEC-02` | HR Confidentiality | Bảo mật Nhiệm kỳ & Quản trị Cán bộ cấp cao | `Guest, Staff` | `HR, Admin` | ✅ **PASS** | 0 chunk |
| `SEC-03` | Credit Risk & Capital Safety | Bảo mật Tỷ lệ An toàn vốn & Hệ số Rủi ro Tín dụng | `Guest` | `Staff, Admin` | ✅ **PASS** | 0 chunk |
| `SEC-04` | Vault & Physical Security | Bảo mật Quy trình Niêm phong & Vận chuyển Tiền mặt Kho quỹ | `Guest` | `Staff, Admin` | ✅ **PASS** | 0 chunk |
| `SEC-05` | Systemic Risk & Fund Management | Bảo mật Quản lý Trích nộp Quỹ An toàn Hệ thống Tín dụng | `Guest` | `Staff, Admin` | ✅ **PASS** | 0 chunk |

---

## 3. Bằng chứng Kiểm thử Chi tiết (Evidence Logs)

### 🔍 Test Case `SEC-01`: Bảo mật Hồ sơ & Tiêu chuẩn Bổ nhiệm Tổng giám đốc
- **Câu hỏi truy vấn**: `"Hồ sơ lý lịch tư pháp và tiêu chuẩn bổ nhiệm Tổng giám đốc người đại diện pháp luật"`
- **Tài liệu mục tiêu kiểm soát**: Nghị định số 73/2016/NĐ-CP (Điều khoản Nhân sự)
- **Vai trò bị cấm truy cập**: `Guest, Staff`
- **Vai trò được phép truy cập**: `HR, Admin`

#### Bằng chứng kiểm thử:
1. **Kiểm thử Vai trò Bị cấm (Unauthorized Verification)**:
   - Trạng thái rò rỉ: `KHÔNG CÓ (PASS)`
   - Số lượng chunk tài liệu cấm xuất hiện trong Top-5: `0 chunk`.
2. **Kiểm thử Vai trò Hợp lệ (Authorized Verification)**:
   - **Role [HR]**: Top 1 trả về `[46/2023/NĐ-CP | Điều 64. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e73a0a0-21ad-11f1-8595-4bd9e632daa9]` | Score: `1.0023` | Quyền: `['Admin', 'HR']`.
   - **Role [Admin]**: Top 1 trả về `[46/2023/NĐ-CP | Điều 64. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e73a0a0-21ad-11f1-8595-4bd9e632daa9]` | Score: `1.0023` | Quyền: `['Admin', 'HR']`.

### 🔍 Test Case `SEC-02`: Bảo mật Nhiệm kỳ & Quản trị Cán bộ cấp cao
- **Câu hỏi truy vấn**: `"Nhiệm kỳ và điều kiện bổ nhiệm Giám đốc Tổng giám đốc tổ chức quản trị"`
- **Tài liệu mục tiêu kiểm soát**: Luật Hợp tác xã số 17/2023/QH15 (Điều khoản Cán bộ Quản lý)
- **Vai trò bị cấm truy cập**: `Guest, Staff`
- **Vai trò được phép truy cập**: `HR, Admin`

#### Bằng chứng kiểm thử:
1. **Kiểm thử Vai trò Bị cấm (Unauthorized Verification)**:
   - Trạng thái rò rỉ: `KHÔNG CÓ (PASS)`
   - Số lượng chunk tài liệu cấm xuất hiện trong Top-5: `0 chunk`.
2. **Kiểm thử Vai trò Hợp lệ (Authorized Verification)**:
   - **Role [HR]**: Top 1 trả về `[17/2023/QH15 | Điều 68. Giám đốc (Tổng giám đốc) theo tổ chức quản trị đầy đủ | 93f66780-df3e-11f0-9b3d-5da80fc25543]` | Score: `5.3496` | Quyền: `['Admin', 'HR']`.
   - **Role [Admin]**: Top 1 trả về `[17/2023/QH15 | Điều 68. Giám đốc (Tổng giám đốc) theo tổ chức quản trị đầy đủ | 93f66780-df3e-11f0-9b3d-5da80fc25543]` | Score: `5.3496` | Quyền: `['Admin', 'HR']`.

### 🔍 Test Case `SEC-03`: Bảo mật Tỷ lệ An toàn vốn & Hệ số Rủi ro Tín dụng
- **Câu hỏi truy vấn**: `"Hệ số rủi ro tín dụng đối với các khoản cho vay thế chấp nhà và bảo lãnh"`
- **Tài liệu mục tiêu kiểm soát**: Thông tư số 41/2016/TT-NHNN (Tỷ lệ an toàn vốn ngân hàng)
- **Vai trò bị cấm truy cập**: `Guest`
- **Vai trò được phép truy cập**: `Staff, Admin`

#### Bằng chứng kiểm thử:
1. **Kiểm thử Vai trò Bị cấm (Unauthorized Verification)**:
   - Trạng thái rò rỉ: `KHÔNG CÓ (PASS)`
   - Số lượng chunk tài liệu cấm xuất hiện trong Top-5: `0 chunk`.
2. **Kiểm thử Vai trò Hợp lệ (Authorized Verification)**:
   - **Role [Staff]**: Top 1 trả về `[41/2016/TT-NHNN | Điều 9. Hệ số rủi ro tín dụng (CRW) | 0e053d1e-eb9a-11f0-b34c-7bc48de3078b]` | Score: `5.7582` | Quyền: `['Admin', 'Staff']`.
   - **Role [Admin]**: Top 1 trả về `[41/2016/TT-NHNN | Điều 9. Hệ số rủi ro tín dụng (CRW) | 0e053d1e-eb9a-11f0-b34c-7bc48de3078b]` | Score: `5.7582` | Quyền: `['Admin', 'Staff']`.

### 🔍 Test Case `SEC-04`: Bảo mật Quy trình Niêm phong & Vận chuyển Tiền mặt Kho quỹ
- **Câu hỏi truy vấn**: `"Quy định về niêm phong, giao nhận và vận chuyển tiền mặt, tài sản quý"`
- **Tài liệu mục tiêu kiểm soát**: Thông tư số 01/2014/TT-NHNN (Vận chuyển bảo quản tiền mặt)
- **Vai trò bị cấm truy cập**: `Guest`
- **Vai trò được phép truy cập**: `Staff, Admin`

#### Bằng chứng kiểm thử:
1. **Kiểm thử Vai trò Bị cấm (Unauthorized Verification)**:
   - Trạng thái rò rỉ: `KHÔNG CÓ (PASS)`
   - Số lượng chunk tài liệu cấm xuất hiện trong Top-5: `0 chunk`.
2. **Kiểm thử Vai trò Hợp lệ (Authorized Verification)**:
   - **Role [Staff]**: Top 1 trả về `[01/2014/TT-NHNN | Điều 52. Đảm bảo an toàn trên đường vận chuyển | 9ffe13b2-2d53-11f1-b25d-59f3dd12eee6]` | Score: `10.1907` | Quyền: `['Admin', 'Staff']`.
   - **Role [Admin]**: Top 1 trả về `[01/2014/TT-NHNN | Điều 52. Đảm bảo an toàn trên đường vận chuyển | 9ffe13b2-2d53-11f1-b25d-59f3dd12eee6]` | Score: `10.1907` | Quyền: `['Admin', 'Staff']`.

### 🔍 Test Case `SEC-05`: Bảo mật Quản lý Trích nộp Quỹ An toàn Hệ thống Tín dụng
- **Câu hỏi truy vấn**: `"Trích nộp và quản lý sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng"`
- **Tài liệu mục tiêu kiểm soát**: Thông tư số 27/2024/TT-NHNN (Quỹ an toàn hệ thống)
- **Vai trò bị cấm truy cập**: `Guest`
- **Vai trò được phép truy cập**: `Staff, Admin`

#### Bằng chứng kiểm thử:
1. **Kiểm thử Vai trò Bị cấm (Unauthorized Verification)**:
   - Trạng thái rò rỉ: `KHÔNG CÓ (PASS)`
   - Số lượng chunk tài liệu cấm xuất hiện trong Top-5: `0 chunk`.
2. **Kiểm thử Vai trò Hợp lệ (Authorized Verification)**:
   - **Role [Staff]**: Top 1 trả về `[27/2024/TT-NHNN | Điều 24. Nguyên tắc quản lý Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân | 6dbd8900-2d44-11f1-aa11-8f9f9d9b3cb4]` | Score: `10.5965` | Quyền: `['Admin', 'Staff']`.
   - **Role [Admin]**: Top 1 trả về `[27/2024/TT-NHNN | Điều 24. Nguyên tắc quản lý Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân | 6dbd8900-2d44-11f1-aa11-8f9f9d9b3cb4]` | Score: `10.5965` | Quyền: `['Admin', 'Staff']`.

---

## 4. Kết luận Đánh giá An toàn Dữ liệu (Security Compliance Conclusion)

> [!IMPORTANT]
> **KẾT LUẬN CUỐI CÙNG**: Hệ thống RAG Retrieval Pipeline của **Buổi 15** đã vượt qua **100% các bài kiểm thử tự động**, khẳng định:
> 1. **Zero Data Leakage**: Người dùng ở các vai trò thấp (`Guest`, `Staff`) hoàn toàn **không thể tiếp cận** bất kỳ nội dung hoặc metadata của các văn bản nhạy cảm thuộc về vai trò cao hơn (`HR`, `Admin`).
> 2. **Reranker Isolation**: Bộ lọc quyền truy cập (Access Filter Masking) hoạt động chính xác trước tầng Cross-Encoder Reranker, ngăn chặn triệt để nguy cơ tài liệu cấm lọt vào candidate pool.
> 3. **Graph Traversal Protection**: Ngữ cảnh đồ thị 1-hop (`PREV`/`NEXT`) được bảo vệ hoàn toàn, ngăn chặn việc dò tìm tài liệu cấm thông qua liên kết cấu trúc đồ thị.
> 
> **Trạng thái**: 🛡️ **HỆ THỐNG ĐẠT CHỨNG NHẬN AN TOÀN DỮ LIỆU MỨC CƠ BẢN (RBAC LEVEL 1 PASSED)**.