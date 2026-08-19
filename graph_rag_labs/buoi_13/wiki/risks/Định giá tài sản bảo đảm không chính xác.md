---
id: RR-008
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Định giá tài sản bảo đảm không chính xác

**Mô tả**: Dữ liệu định giá không độc lập hoặc hết hạn
* **Phân loại**: Rui ro tin dung
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-CREDIT`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Thiếu rà soát lại giá trị tài sản
* **Sự kiện (Event)**: Tài sản bảo đảm được định giá cao hơn thực tế
* **Hậu quả (Impact)**: Tăng tổn thất khi xử lý nợ

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Rà soát độc lập định giá tài sản bảo đảm]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: rà soát độc lập giảm sai định giá"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Rà soát phát hiện giá trị tài sản bảo đảm đã hết hiệu lực]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện sai định giá tài sản"
  * *Trạng thái xác minh*: `VERIFIED`