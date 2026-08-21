# BÁO CÁO TÁI SỬ DỤNG VÀ THỰC THI PHÂN QUYỀN RBAC (RBAC REUSE & FILTERING REPORT)
## Dự án: Buổi 17 — RBAC, Audit Trail và AI Compliance Gap Checker

---

## 1. Phân tích Chi tiết Dữ liệu Phân quyền (`allowed_roles`)

Kiểm tra trên tệp dữ liệu `buoi_14/data/processed/chunks_secure.csv` (6,593 dòng):

### 1.1. Các Vai trò (Roles) Tồn tại trong Dữ liệu
Dữ liệu hiện tại đã được gán thẻ phân quyền đầy đủ cho 4 vai trò chính:
1. `Admin` (Quản trị viên)
2. `HR` (Nhân sự)
3. `Staff` (Nhân viên chính thức)
4. `Guest` (Khách / Thực tập sinh)

---

### 1.2. Thống kê Số lượng Chunk được Phép Truy cập theo Role

| Role | Số lượng Chunks được phép xem | Tỷ lệ trên tổng Corpus | Ghi chú quyền truy cập |
| :--- | :---: | :---: | :--- |
| **Admin** | **6,593** chunks | **100.0%** | Toàn quyền xem 100% dữ liệu hệ thống. |
| **Staff** | **6,329** chunks | **96.0%** | Xem tài liệu nghiệp vụ, quy chế chung và quy định nội bộ. |
| **HR** | **4,566** chunks | **69.3%** | Xem tài liệu nhân sự, lương thưởng, tuyển dụng và quy định chung. |
| **Guest** | **4,302** chunks | **65.3%** | Chỉ xem tài liệu công khai / quy định chung. |

---

### 1.3. Phân loại Chunks theo Phân nhóm Quyền (Restricted vs Multi-Role)

* **Tài liệu đa vai trò (Công khai - Multi-Role Public)**:
  * `["Admin", "HR", "Staff", "Guest"]`: **4,302** chunks (**65.3%**). Tất cả mọi người đều có quyền xem.
* **Tài liệu giới hạn nội bộ Nhân viên (Staff Restricted)**:
  * `["Admin", "Staff"]`: **2,027** chunks (**30.7%**). Giới hạn cho cán bộ nhân viên chính thức và Admin (Guest và HR không có quyền nếu không thuộc Staff).
* **Tài liệu giới hạn Nhân sự (HR Sensitive Restricted)**:
  * `["Admin", "HR"]`: **264** chunks (**4.0%**). Tài liệu nhạy cảm về lương thưởng, đánh giá, tuyển dụng, bổ nhiệm cán bộ. Chỉ HR và Admin được phép xem.

---

### 1.4. Đánh giá Format & Xử lý Unknown Role

* **Tính ổn định của định dạng Format**:
  * **100%** (`6,593` / `6,593` dòng) parse thành công dạng JSON List string không xảy ra bất kỳ lỗi nào (**0 parse errors**).
* **Xử lý Vai trò không xác định (Unknown Role)**:
  * Hàm `validate_roles()` lọc bỏ các vai trò lạ (như `Risk_Manager`, `Hacker`, `SuperUser`).
  * Nếu danh sách vai trò không hợp lệ, hệ thống tự động fallback về vai trò mặc định `['Guest']` (Quyền thấp nhất).
  * **Đạt nguyên tắc Default Deny (Cấm mặc định).**

---

## 2. Kết quả Thực nghiệm Truy xuất với 5 Vai trò trên `SecureRetriever`

Thực hiện cùng 1 câu hỏi truy vấn:
> *"quy định về nâng lương phụ cấp và tuyển dụng cán bộ nhân sự"*

chạy qua `SecureRetriever` với 5 vai trò người dùng:

```text
1. Admin         (Toàn quyền)
2. HR            (Nhân sự)
3. Risk_Manager  (Unknown Role -> Fallback Guest)
4. Staff         (Nhân viên)
5. Guest         (Khách)
```

### Kết quả Top-5 Chunks Trả về cho từng Role:

#### 🟢 Role: `Admin` (Trả về 5 chunks)
* Top 1: Chunk `ab3a66b0` | Score: `20.1202` | Allowed: `['Admin', 'HR']`
* Top 2: Chunk `a008c1ea` | Score: `14.6291` | Allowed: `['Admin', 'HR']`
* Top 3: Chunk `3dab6ea0` | Score: `14.3661` | Allowed: `['Admin', 'HR']`
* Top 4: Chunk `7e303036` | Score: `14.2613` | Allowed: `['Admin', 'HR']`
* Top 5: Chunk `9ff36548` | Score: `13.0674` | Allowed: `['Admin', 'Staff']`
> **Nhận xét**: Admin thấy toàn bộ tài liệu có điểm phù hợp nhất bao gồm cả tài liệu bảo mật HR và Staff.

#### 🟢 Role: `HR` (Trả về 5 chunks)
* Top 1: Chunk `ab3a66b0` | Score: `20.1202` | Allowed: `['Admin', 'HR']`
* Top 2: Chunk `a008c1ea` | Score: `14.6291` | Allowed: `['Admin', 'HR']`
* Top 3: Chunk `3dab6ea0` | Score: `14.3661` | Allowed: `['Admin', 'HR']`
* Top 4: Chunk `7e303036` | Score: `14.2613` | Allowed: `['Admin', 'HR']`
* Top 5: Chunk `7e30311c` | Score: `12.7472` | Allowed: `['Admin', 'HR']`
> **Nhận xét**: HR tiếp cận đúng các tài liệu bảo mật về chế độ lương thưởng và tuyển dụng cán bộ (Rank 1-5 đều chứa 'HR').

#### 🟡 Role: `Staff` (Trả về 5 chunks)
* Top 1: Chunk `9ff36548` | Score: `13.0674` | Allowed: `['Admin', 'Staff']`
* Top 2: Chunk `a009100a` | Score: `12.7506` | Allowed: `['Admin', 'Staff']`
* Top 3: Chunk `9ff6c08a` | Score: `12.3569` | Allowed: `['Admin', 'Staff']`
* Top 4: Chunk `b71f3e60` | Score: `12.2170` | Allowed: `['Admin', 'HR', 'Staff', 'Guest']`
* Top 5: Chunk `ab39ca70` | Score: `11.8735` | Allowed: `['Admin', 'Staff']`
> **Nhận xét**: Các tài liệu bảo mật HR (Chunk `ab3a66b0` có score cao 20.12) đã bị **LOẠI BỎ HOÀN TOÀN TRƯỚC RETRIEVAL**. Staff chỉ xem được các tài liệu thuộc quyền Staff/Guest.

#### 🔴 Role: `Guest` (Trả về 5 chunks)
* Top 1: Chunk `b71f3e60` | Score: `12.2170` | Allowed: `['Admin', 'HR', 'Staff', 'Guest']`
* Top 2: Chunk `16d909e5` | Score: `11.5920` | Allowed: `['Admin', 'HR', 'Staff', 'Guest']`
* Top 3: Chunk `4572c19b` | Score: `11.5262` | Allowed: `['Admin', 'HR', 'Staff', 'Guest']`
* Top 4: Chunk `6fc4e5f0` | Score: `11.5121` | Allowed: `['Admin', 'HR', 'Staff', 'Guest']`
* Top 5: Chunk `b633f400` | Score: `10.7653` | Allowed: `['Admin', 'HR', 'Staff', 'Guest']`
> **Nhận xét**: Guest chỉ xem được 100% các tài liệu công khai có gắn thẻ 'Guest'. Tất cả tài liệu giới hạn Staff và HR bị chặn hoàn toàn.

#### 🔵 Role: `Risk_Manager` (Unknown Role -> Trả về 5 chunks)
* Kết quả trả về **TRÙNG KHỚP 100% VỚI ROLE `Guest`** (Chunk `b71f3e60`, `16d909e5`, `4572c19b`, `6fc4e5f0`, `b633f400`).
> **Nhận xét**: Xử lý role chưa xác định hoạt động chính xác theo chuẩn **Default Deny**.

---

## 3. Kết luận Tái sử dụng Code & Adapter

* **Thiết kế Adapter**: Đã tạo file `buoi_17/scripts/secure_retrieval.py` làm Adapter bọc `SecureRetriever` của Buổi 16.
* **Không sao chép hay sửa đổi**: Giữ nguyên vẹn 100% mã nguồn và dữ liệu của Buổi 16.

---

## STATUS SUMMARY

```text
RBAC REUSED: YES
FILTER BEFORE RETRIEVAL: PASS
UNKNOWN ROLE DEFAULT DENY: PASS
```
