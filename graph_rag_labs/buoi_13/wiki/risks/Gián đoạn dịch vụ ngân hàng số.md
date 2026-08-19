---
id: RR-005
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Gián đoạn dịch vụ ngân hàng số

**Mô tả**: Hệ thống thanh toán trực tuyến không sẵn sàng
* **Phân loại**: Rui ro cong nghe thong tin
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-IT`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Kế hoạch năng lực và dự phòng chưa đầy đủ
* **Sự kiện (Event)**: Dịch vụ ngân hàng số bị gián đoạn
* **Hậu quả (Impact)**: Mất doanh thu và khiếu nại khách hàng

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Kiểm thử khả năng chịu tải và chuyển đổi dự phòng]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: kiểm thử dự phòng giảm gián đoạn dịch vụ"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Dịch vụ ngân hàng số gián đoạn trong giờ cao điểm]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện gián đoạn dịch vụ"
  * *Trạng thái xác minh*: `VERIFIED`