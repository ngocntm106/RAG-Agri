# BÁO CÁO CATALOGING DỮ LIỆU BUỔI 18
## AI Compliance Checker & AI Audit Checklist Generator

## 1. Tổng quan Dữ liệu Đầu vào
- **Tệp quy định nội bộ (`agribank_internal_policies.csv`):** 24 chunks, 10 văn bản nội bộ Agribank.
- **Tệp dữ liệu tích hợp (`chunks_combined_secure.csv`):** 811 chunks tổng cộng (787 chunks văn bản pháp lý NHNN/Chính phủ + 24 chunks văn bản nội bộ).
- **Số lượng miền nghiệp vụ (Domains) đã phát hiện:** 10 miền nghiệp vụ chính.

## 2. Thống kê Chi tiết các Văn bản Nội bộ Agribank
| STT | mã VB | Số ký hiệu | Loại VB | Tên Văn bản | Domain | Chunks | Allowed Roles |
|---|---|---|---|---|---|---|---|
| 1 | `agr_at01` | `100/QĐ-NHNO-AT` | Quy định nội bộ | Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank | **An toàn Kho quỹ & Vận chuyển** | 4 | `["Admin", "Risk_Manager", "Staff"]` |
| 2 | `agr_bh06` | `180/QĐ-NHNO-BH` | Quy định nội bộ | Quy định nội bộ số 180/QĐ-NHNO-BH về Mua bảo hiểm rủi ro nghiệp vụ và tài sản Agribank | **An toàn & Bảo hiểm Kho tiền** | 2 | `["Admin", "Risk_Manager", "Staff"]` |
| 3 | `agr_car02` | `250/QĐ-NHNO-QLRR` | Quy định nội bộ | Quy định nội bộ số 250/QĐ-NHNO-QLRR về Quản lý tỷ lệ an toàn vốn và định mức rủi ro Agribank | **CAR & Quản trị Rủi ro** | 3 | `["Admin", "Risk_Manager"]` |
| 4 | `agr_fx04` | `410/QĐ-NHNO-TTNH` | Quy định nội bộ | Quy định nội bộ số 410/QĐ-NHNO-TTNH về Quản lý trạng thái ngoại tệ và giao dịch ngoại hối Agribank | **Ngoại tệ & Phái sinh** | 2 | `["Admin", "Risk_Manager"]` |
| 5 | `agr_gp05` | `520/QC-NHNO-MANGLUOI` | Quy chế nội bộ | Quy chế số 520/QC-NHNO-MANGLUOI về Mở rộng mạng lưới chi nhánh và phòng giao dịch Agribank | **Cấp phép & Mạng lưới Chi nhánh** | 2 | `["Admin", "Risk_Manager", "Staff"]` |
| 6 | `agr_hr08` | `88/QĐ-NHNO-NS` | Quy định nội bộ | Quy định nội bộ số 88/QĐ-NHNO-NS về Quy hoạch, bổ nhiệm và quản lý nhân sự Agribank | **Nhân sự & Đào tạo** | 2 | `["Admin", "HR"]` |
| 7 | `agr_it07` | `600/QC-NHNO-CNTT` | Quy chế nội bộ | Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT về An toàn thông tin và Quản trị dữ liệu AI Agribank | **Bảo mật CNTT & AI** | 2 | `["Admin", "Risk_Manager"]` |
| 8 | `agr_tc09` | `720/QC-NHNO-TC` | Quy chế nội bộ | Quy chế tài chính số 720/QC-NHNO-TC về Chế độ chi tiêu và mua sắm tài sản nội bộ Agribank | **Tài chính & Mua sắm** | 2 | `["Admin", "Risk_Manager", "Staff"]` |
| 9 | `agr_td03` | `315/QC-NHNO-TD` | Quy chế nội bộ | Quy chế tín dụng nội bộ số 315/QC-NHNO-TD về Phán quyết và Phân cấp ủy quyền cho vay tại Agribank | **Tín dụng & Phán quyết Cho vay** | 3 | `["Admin", "Risk_Manager", "Staff"]` |
| 10 | `agr_xln10` | `390/QĐ-NHNO-XLN` | Quy định nội bộ | Quy định nội bộ số 390/QĐ-NHNO-XLN về Phân loại nợ và Xử lý nợ xấu tại Agribank | **Phân loại Nợ & Xử lý Nợ xấu** | 2 | `["Admin", "Risk_Manager"]` |

## 3. Phân loại Văn bản theo Domain / Miền Nghiệp vụ
Phân loại chi tiết các quy định nội bộ Agribank kết hợp với các văn bản pháp lý đối chiếu (Thông tư, Nghị định) phục vụ UC3 & UC4:

### 📂 Domain: An toàn Kho quỹ & Vận chuyển
- **Văn bản nội bộ:** `100/QĐ-NHNO-AT` — *Quy định nội bộ số 100/QĐ-NHNO-AT về Giao nhận, bảo quản, vận chuyển tiền mặt và tài sản quý Agribank*
  - **Mã VB:** `agr_at01` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager", "Staff"]`

### 📂 Domain: An toàn & Bảo hiểm Kho tiền
- **Văn bản nội bộ:** `180/QĐ-NHNO-BH` — *Quy định nội bộ số 180/QĐ-NHNO-BH về Mua bảo hiểm rủi ro nghiệp vụ và tài sản Agribank*
  - **Mã VB:** `agr_bh06` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager", "Staff"]`

### 📂 Domain: CAR & Quản trị Rủi ro
- **Văn bản nội bộ:** `250/QĐ-NHNO-QLRR` — *Quy định nội bộ số 250/QĐ-NHNO-QLRR về Quản lý tỷ lệ an toàn vốn và định mức rủi ro Agribank*
  - **Mã VB:** `agr_car02` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager"]`

### 📂 Domain: Ngoại tệ & Phái sinh
- **Văn bản nội bộ:** `410/QĐ-NHNO-TTNH` — *Quy định nội bộ số 410/QĐ-NHNO-TTNH về Quản lý trạng thái ngoại tệ và giao dịch ngoại hối Agribank*
  - **Mã VB:** `agr_fx04` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager"]`

### 📂 Domain: Cấp phép & Mạng lưới Chi nhánh
- **Văn bản nội bộ:** `520/QC-NHNO-MANGLUOI` — *Quy chế số 520/QC-NHNO-MANGLUOI về Mở rộng mạng lưới chi nhánh và phòng giao dịch Agribank*
  - **Mã VB:** `agr_gp05` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager", "Staff"]`

### 📂 Domain: Nhân sự & Đào tạo
- **Văn bản nội bộ:** `88/QĐ-NHNO-NS` — *Quy định nội bộ số 88/QĐ-NHNO-NS về Quy hoạch, bổ nhiệm và quản lý nhân sự Agribank*
  - **Mã VB:** `agr_hr08` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "HR"]`

### 📂 Domain: Bảo mật CNTT & AI
- **Văn bản nội bộ:** `600/QC-NHNO-CNTT` — *Quy chế bảo mật CNTT số 600/QC-NHNO-CNTT về An toàn thông tin và Quản trị dữ liệu AI Agribank*
  - **Mã VB:** `agr_it07` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager"]`

### 📂 Domain: Tài chính & Mua sắm
- **Văn bản nội bộ:** `720/QC-NHNO-TC` — *Quy chế tài chính số 720/QC-NHNO-TC về Chế độ chi tiêu và mua sắm tài sản nội bộ Agribank*
  - **Mã VB:** `agr_tc09` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager", "Staff"]`

### 📂 Domain: Tín dụng & Phán quyết Cho vay
- **Văn bản nội bộ:** `315/QC-NHNO-TD` — *Quy chế tín dụng nội bộ số 315/QC-NHNO-TD về Phán quyết và Phân cấp ủy quyền cho vay tại Agribank*
  - **Mã VB:** `agr_td03` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager", "Staff"]`

### 📂 Domain: Phân loại Nợ & Xử lý Nợ xấu
- **Văn bản nội bộ:** `390/QĐ-NHNO-XLN` — *Quy định nội bộ số 390/QĐ-NHNO-XLN về Phân loại nợ và Xử lý nợ xấu tại Agribank*
  - **Mã VB:** `agr_xln10` | **Cơ quan:** Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) | **Roles:** `["Admin", "Risk_Manager"]`

## 4. Kiểm tra Tính Đầy đủ của Trường Dữ liệu (Integrity Audit)
Kiểm tra 3 trường bắt buộc đối với tất cả các record trong dữ liệu:
- **Trường Điều/Khoản (`article`):**
  - `agribank_internal_policies.csv`: 24/24 valid (Null: 0)
  - `chunks_combined_secure.csv`: 811/811 valid (Null: 0)
- **Trường Trích dẫn (`citation`):**
  - `agribank_internal_policies.csv`: 24/24 valid (Null: 0)
  - `chunks_combined_secure.csv`: 811/811 valid (Null: 0)
- **Trường Phân quyền (`allowed_roles`):**
  - `agribank_internal_policies.csv`: 24/24 valid JSON string (Null: 0)
  - `chunks_combined_secure.csv`: 811/811 valid JSON string (Null: 0)

---

## 5. Kết luận Cataloging
DATA CATALOGING: PASS
DOMAINS DETECTED: 10
READY FOR UC3 & UC4: YES