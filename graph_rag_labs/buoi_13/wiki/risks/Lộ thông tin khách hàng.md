---
id: RR-004
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Lộ thông tin khách hàng

**Mô tả**: Quyền truy cập dữ liệu không được kiểm soát phù hợp
* **Phân loại**: Rui ro cong nghe thong tin
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-IT`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Cấp quyền vượt nhu cầu công việc
* **Sự kiện (Event)**: Dữ liệu khách hàng bị truy cập hoặc chia sẻ trái phép
* **Hậu quả (Impact)**: Vi phạm bảo mật và tổn hại uy tín

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Rà soát quyền truy cập định kỳ]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: rà soát quyền hạn giảm lộ dữ liệu"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Tài khoản có quyền truy cập dữ liệu vượt phạm vi công việc]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện quyền truy cập quá mức"
  * *Trạng thái xác minh*: `VERIFIED`