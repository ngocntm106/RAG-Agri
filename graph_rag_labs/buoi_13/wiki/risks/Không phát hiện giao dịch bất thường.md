---
id: RR-009
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Không phát hiện giao dịch bất thường

**Mô tả**: Luật phát hiện gian lận không được cập nhật
* **Phân loại**: Rui ro gian lan
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-OPS`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Ngưỡng cảnh báo không phù hợp
* **Sự kiện (Event)**: Giao dịch nghi ngờ không bị chặn kịp thời
* **Hậu quả (Impact)**: Tổn thất tài chính và uy tín

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Hiệu chỉnh luật phát hiện giao dịch gian lận]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: hiệu chỉnh luật giảm bỏ sót giao dịch bất thường"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Giao dịch bất thường chỉ bị phát hiện sau khi khách hàng khiếu nại]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện không phát hiện bất thường"
  * *Trạng thái xác minh*: `VERIFIED`