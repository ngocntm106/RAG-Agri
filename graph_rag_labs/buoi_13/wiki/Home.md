# Wiki Risk Graph 🧠

Chào mừng bạn đến với hệ thống Wiki Risk Graph phục vụ đào tạo quản trị rủi ro.

## 📊 Thống kê đồ thị
| Loại thực thể (Node) | Số lượng |
| :--- | :---: |
| [[#Danh sách Rủi ro\|RuiRo (Rủi ro)]] | 12 |
| [[#Danh sách Kiểm soát\|KiemSoat (Kiểm soát)]] | 10 |
| [[#Danh sách Sự kiện rủi ro\|SuKienRuiRo (Sự kiện)]] | 12 |
| **Tổng cộng Nodes** | **34** |

| Loại mối quan hệ (Edge) | Số lượng |
| :--- | :---: |
| `MITIGATES` (Kiểm soát -> Rủi ro) | 10 |
| `OBSERVED_AS` (Rủi ro -> Sự kiện) | 12 |
| **Tổng cộng Edges** | **22** |

## 📁 Danh sách Rủi ro
* [[Giao dịch chuyển tiền bị hạch toán sai]] - `RR-001`
* [[Phê duyệt tín dụng vượt thẩm quyền]] - `RR-002`
* [[Giải ngân thiếu hồ sơ bảo đảm]] - `RR-003`
* [[Lộ thông tin khách hàng]] - `RR-004`
* [[Gián đoạn dịch vụ ngân hàng số]] - `RR-005`
* [[Gian lận giả mạo yêu cầu chuyển tiền]] - `RR-006`
* [[Chậm báo cáo giao dịch đáng ngờ]] - `RR-007`
* [[Định giá tài sản bảo đảm không chính xác]] - `RR-008`
* [[Không phát hiện giao dịch bất thường]] - `RR-009`
* [[Sai lệch số liệu báo cáo quản trị]] - `RR-010`
* [[Nhà cung cấp công nghệ không đáp ứng cam kết]] - `RR-011`
* [[Xung đột lợi ích trong mua sắm]] - `RR-012`

## 🛡️ Danh sách Kiểm soát
* [[Đối soát tự động giao dịch và sổ cái]] - `KS-001`
* [[Kiểm tra hạn mức phê duyệt trên hệ thống]] - `KS-002`
* [[Checklist điều kiện giải ngân bắt buộc]] - `KS-003`
* [[Rà soát quyền truy cập định kỳ]] - `KS-004`
* [[Kiểm thử khả năng chịu tải và chuyển đổi dự phòng]] - `KS-005`
* [[Xác thực hai kênh với lệnh chuyển tiền ngoại lệ]] - `KS-006`
* [[Theo dõi SLA xử lý cảnh báo AML]] - `KS-007`
* [[Rà soát độc lập định giá tài sản bảo đảm]] - `KS-008`
* [[Hiệu chỉnh luật phát hiện giao dịch gian lận]] - `KS-009`
* [[Đối chiếu dữ liệu nguồn trước khi phát hành báo cáo]] - `KS-010`

## 🚨 Danh sách Sự kiện rủi ro
* [[Sai lệch trạng thái giao dịch được phát hiện khi đối soát cuối ngày]] - `SK-001`
* [[Hồ sơ tín dụng được phê duyệt vượt hạn mức của người phê duyệt]] - `SK-002`
* [[Giải ngân trước khi hoàn thiện chứng từ bảo đảm]] - `SK-003`
* [[Tài khoản có quyền truy cập dữ liệu vượt phạm vi công việc]] - `SK-004`
* [[Dịch vụ ngân hàng số gián đoạn trong giờ cao điểm]] - `SK-005`
* [[Yêu cầu chuyển tiền giả mạo được xử lý trước khi bị thu hồi]] - `SK-006`
* [[Báo cáo giao dịch đáng ngờ nộp quá hạn nội bộ]] - `SK-007`
* [[Rà soát phát hiện giá trị tài sản bảo đảm đã hết hiệu lực]] - `SK-008`
* [[Giao dịch bất thường chỉ bị phát hiện sau khi khách hàng khiếu nại]] - `SK-009`
* [[Báo cáo quản trị sử dụng dữ liệu nguồn chưa đối chiếu]] - `SK-010`
* [[Nhà cung cấp chậm khôi phục dịch vụ so với SLA]] - `SK-011`
* [[Kiểm tra sau mua sắm phát hiện thiếu kê khai xung đột lợi ích]] - `SK-012`