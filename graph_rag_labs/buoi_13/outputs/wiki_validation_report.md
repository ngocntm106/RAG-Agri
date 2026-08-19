# Báo cáo Kiểm thử Wiki Risk Graph 🩺

Báo cáo tự động đánh giá tính toàn vẹn dữ liệu, các liên kết markdown và cấu trúc thực thể trong Wiki.

## 📊 Tổng quan kiểm tra
| Tiêu chí kiểm tra | Kết quả thống kê | Trạng thái |
| :--- | :---: | :---: |
| 1. Tổng số file Markdown | 35 | `INFO` |
| 2. Tổng số Wikilink (không gồm link nội bộ) | 78 | `INFO` |
| 3. Wikilink trỏ tới trang không tồn tại | 0 | 🟢 PASS |
| 4. Thực thể bị trùng ID trong Wiki | 0 | 🟢 PASS |
| 5. Trang có ID không khớp với `entities.csv` | 0 | 🟢 PASS |
| 6. Quan hệ trỏ tới thực thể không tồn tại | 0 | 🟢 PASS |
| 7. Rủi ro (`RuiRo`) không có Kiểm soát | 2 | ⚠️ WARN |
| 8. Rủi ro (`RuiRo`) không có Sự kiện | 0 | 🟢 PASS |
| 9. Trang bị cô lập (Orphan Page) | 0 | 🟢 PASS |

## 🔍 Chi tiết kết quả kiểm tra

### 3. Wikilink trỏ tới trang không tồn tại (Broken Links)
🟢 Không phát hiện broken wikilinks.

### 4. Thực thể bị trùng ID (Duplicate IDs)
🟢 Không phát hiện thực thể trùng ID.

### 5. Trang không khớp với `entities.csv` (Metadata Mismatch)
🟢 Toàn bộ các trang Wiki thực thể đều khớp ID với `entities.csv`.

### 6. Quan hệ chứa ID không tồn tại trong `entities.csv` (Broken Relations)
🟢 Không có quan hệ lỗi trong `relations.csv`.

### 7. Rủi ro không có kiểm soát giảm thiểu (Data Gap)
> [!WARNING]
> Phát hiện các rủi ro chưa được thiết lập chốt kiểm soát giảm thiểu:
* Rủi ro `RR-011`: **Nhà cung cấp công nghệ không đáp ứng cam kết**
* Rủi ro `RR-012`: **Xung đột lợi ích trong mua sắm**

### 8. Rủi ro chưa ghi nhận sự kiện phát sinh (No Observed Events)
🟢 Toàn bộ rủi ro đều đã ghi nhận sự kiện thực tế tương ứng.

### 9. Trang bị cô lập (Orphan Pages)
🟢 Không có trang nào bị cô lập khỏi mạng lưới rủi ro nghiệp vụ.

## 🎯 Kết luận phân loại lỗi (Lỗi Chương Trình vs Lỗi Dữ Liệu)

### 💻 Lỗi Chương Trình (Program/Code Errors)
* **Trạng thái**: `0 lỗi` - 🟢 **HỆ THỐNG HOẠT ĐỘNG HOÀN HẢO**.
* **Đánh giá**: Script `build_wiki.py` hoạt động chính xác. Không tạo ra bất kỳ broken link nào, định dạng file chuẩn Obsidian, Frontmatter khớp 100% với file chuẩn hóa dữ liệu.

### 📂 Lỗi Dữ Liệu Gốc (Data Gaps/Issues)
* **Trạng thái**: `Phát hiện 2 vấn đề về dữ liệu gốc`.
* **Chi tiết**:
  * **Thiếu Kiểm soát giảm thiểu**: Có 2 rủi ro (`RR-011`, `RR-012`) chưa được cấu hình kiểm soát giảm thiểu trong dữ liệu seed ban đầu (`relationships_seed.csv`). Đây là khoảng trống kiểm soát (Control Gap) thực tế cần bổ sung nghiệp vụ, không phải lỗi code.
* **Đánh giá**: Các cảnh báo trên hoàn toàn là do tính chất của bộ dữ liệu seed mô phỏng ban đầu (`relationships_seed.csv` thiếu quan hệ `MITIGATES` cho rủi ro `RR-011` và `RR-012`). Hệ thống hiển thị cảnh báo này để phục vụ mục đích đào tạo quản lý rủi ro.