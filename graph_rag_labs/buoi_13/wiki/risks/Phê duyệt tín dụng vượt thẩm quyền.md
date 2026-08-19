---
id: RR-002
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Phê duyệt tín dụng vượt thẩm quyền

**Mô tả**: Kiểm tra hạn mức phê duyệt không hiệu lực
* **Phân loại**: Rui ro tin dung
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-CREDIT`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Phân quyền trên hệ thống không cập nhật
* **Sự kiện (Event)**: Khoản vay được phê duyệt vượt thẩm quyền
* **Hậu quả (Impact)**: Tăng nợ xấu và vi phạm quy định

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Kiểm tra hạn mức phê duyệt trên hệ thống]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: kiểm tra hạn mức ngăn phê duyệt vượt thẩm quyền"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Hồ sơ tín dụng được phê duyệt vượt hạn mức của người phê duyệt]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện vượt thẩm quyền"
  * *Trạng thái xác minh*: `VERIFIED`