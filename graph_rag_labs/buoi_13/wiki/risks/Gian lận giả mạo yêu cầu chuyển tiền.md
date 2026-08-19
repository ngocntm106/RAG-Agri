---
id: RR-006
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Gian lận giả mạo yêu cầu chuyển tiền

**Mô tả**: Nhận diện và xác thực yêu cầu chưa đủ mạnh
* **Phân loại**: Rui ro gian lan
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-OPS`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Nhân viên không xác minh kênh liên lạc
* **Sự kiện (Event)**: Yêu cầu chuyển tiền giả mạo được xử lý
* **Hậu quả (Impact)**: Tổn thất tài chính

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Xác thực hai kênh với lệnh chuyển tiền ngoại lệ]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: xác thực hai kênh giảm gian lận chuyển tiền"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Yêu cầu chuyển tiền giả mạo được xử lý trước khi bị thu hồi]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện giả mạo chuyển tiền"
  * *Trạng thái xác minh*: `VERIFIED`