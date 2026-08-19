---
id: RR-010
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Sai lệch số liệu báo cáo quản trị

**Mô tả**: Dữ liệu nguồn không được đối chiếu
* **Phân loại**: Rui ro bao cao
* **Mức độ rủi ro tiềm tàng (Inherent)**: Trung binh
* **Mức độ rủi ro còn lại (Residual)**: Thap
* **Đơn vị sở hữu**: `DV-FINANCE`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Thay đổi dữ liệu không có kiểm soát
* **Sự kiện (Event)**: Báo cáo quản trị có số liệu sai
* **Hậu quả (Impact)**: Quyết định quản trị sai lệch

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Đối chiếu dữ liệu nguồn trước khi phát hành báo cáo]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: đối chiếu nguồn giảm sai lệch báo cáo"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Báo cáo quản trị sử dụng dữ liệu nguồn chưa đối chiếu]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện sai lệch báo cáo"
  * *Trạng thái xác minh*: `VERIFIED`