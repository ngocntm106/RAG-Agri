---
id: RR-007
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Chậm báo cáo giao dịch đáng ngờ

**Mô tả**: Theo dõi cảnh báo AML không kịp thời
* **Phân loại**: Rui ro tuan thu
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-COMPLIANCE`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Khối lượng cảnh báo vượt năng lực xử lý
* **Sự kiện (Event)**: Báo cáo giao dịch đáng ngờ nộp muộn
* **Hậu quả (Impact)**: Chế tài và rủi ro pháp lý

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Theo dõi SLA xử lý cảnh báo AML]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: theo dõi SLA giảm nguy cơ báo cáo muộn"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Báo cáo giao dịch đáng ngờ nộp quá hạn nội bộ]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện báo cáo AML muộn"
  * *Trạng thái xác minh*: `VERIFIED`