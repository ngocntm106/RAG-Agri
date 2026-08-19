---
id: RR-001
type: RuiRo
verification_status: VERIFIED
data_origin: SYNTHETIC
---

# Giao dịch chuyển tiền bị hạch toán sai

**Mô tả**: Đối soát giao dịch cuối ngày không đầy đủ
* **Phân loại**: Rui ro van hanh
* **Mức độ rủi ro tiềm tàng (Inherent)**: Cao
* **Mức độ rủi ro còn lại (Residual)**: Trung binh
* **Đơn vị sở hữu**: `DV-OPS`

## Phân tích nguyên nhân & Hậu quả
* **Nguyên nhân (Cause)**: Thiếu đối chiếu giữa hệ thống thanh toán và sổ cái
* **Sự kiện (Event)**: Giao dịch được ghi nhận sai trạng thái
* **Hậu quả (Impact)**: Tổn thất tài chính và khiếu nại khách hàng

## Kiểm soát giảm thiểu (Mitigating Controls)
* [[Đối soát tự động giao dịch và sổ cái]]
  * *Loại quan hệ*: `MITIGATES`
  * *Bằng chứng*: "Dữ liệu mô phỏng: đối soát tự động giảm nguy cơ hạch toán sai"
  * *Trạng thái xác minh*: `VERIFIED`

## Sự kiện rủi ro đã ghi nhận (Observed Events)
* [[Sai lệch trạng thái giao dịch được phát hiện khi đối soát cuối ngày]]
  * *Loại quan hệ*: `OBSERVED_AS`
  * *Bằng chứng*: "Dữ liệu mô phỏng: sự kiện đối soát giao dịch"
  * *Trạng thái xác minh*: `VERIFIED`