# BÁO CÁO TOÀN DIỆN: BM25 vs DENSE vs HYBRID vs HYBRID + RERANK

Báo cáo này đối chiếu chi tiết 4 giai đoạn tiến hóa của hệ thống Retrieval trên cùng tập corpus chuẩn hóa.

- **Embedding Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Reranker Model**: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (Chế độ: `Neural Cross-Encoder`)
- **Candidate Pool Size**: `k=20`

## 1. Exact Keyword (Số hiệu / Điều khoản cụ thể)
**Câu hỏi**: `Thông tư số 01/2014/TT-NHNN Điều 4 quy định đóng gói niêm phong tiền mặt`

### 1. BM25 RESULTS
| Rank | Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|
| 1 | 45.6128 | `[01/2014/TT-NHNN | Điều 6. Đóng gói, niêm phong tài sản quý, giấy tờ có giá | ab1a5b90-3369-11f1-ae12-49e2c6405655]` | `ab1a5b90-3369-11f1-ae12-49e2c6405655` | 1. Việc đóng gói, niêm phong ngoại tệ, giấy tờ có giá thực hiện như đóng gói, niêm phong tiền mặt.... |
| 2 | 43.8646 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fdca8d0-2d53-11f1-839b-d1bcb9053bea]` | `9fdca8d0-2d53-11f1-839b-d1bcb9053bea` | a) Trên giấy niêm phong gói tiền mới in (10 bó) gồm các nội dung: cơ sở in, đúc tiền; loại tiền; số ... |
| 3 | 43.6427 | `[01/2014/TT-NHNN | Mục 1 QUY ĐỊNH VỀ ĐÓNG GÓI NIÊM PHONG TIỀN MẶT, | 9fd88a84-2d53-11f1-a638-856f28930928]` | `9fd88a84-2d53-11f1-a638-856f28930928` | Mục 1 QUY ĐỊNH VỀ ĐÓNG GÓI NIÊM PHONG TIỀN MẶT,... |
| 4 | 42.0563 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fdbe580-2d53-11f1-96ea-ef7310251bfc]` | `9fdbe580-2d53-11f1-96ea-ef7310251bfc` | 2. Trên giấy niêm phong bó, túi, hộp, bao, thùng tiền phải có đầy đủ, rõ ràng các nội dung sau: tên ... |
| 5 | 40.4209 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fd88a8e-2d53-11f1-a687-91599fc7370e]` | `9fd88a8e-2d53-11f1-a687-91599fc7370e` | Điều 4. Đóng gói tiền mặt... |

### 2. DENSE RESULTS
| Rank | Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|
| 1 | 0.8838 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fd88a8e-2d53-11f1-a687-91599fc7370e]` | `9fd88a8e-2d53-11f1-a687-91599fc7370e` | Điều 4. Đóng gói tiền mặt... |
| 2 | 0.8646 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fda8636-2d53-11f1-93c0-b927d170e4bb]` | `9fda8636-2d53-11f1-93c0-b927d170e4bb` | 6. Cục trưởng Cục Phát hành và Kho quỹ hướng dẫn quy cách đóng gói tiền mặt.... |
| 3 | 0.8158 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fdc5aba-2d53-11f1-8202-39d25e163c85]` | `9fdc5aba-2d53-11f1-8202-39d25e163c85` | 5. Niêm phong tiền mới in:... |
| 4 | 0.8038 | `[01/2014/TT-NHNN | Chương VI TỔ CHỨC THỰC HIỆN | a0091000-2d53-11f1-b348-d16e20c5a43e]` | `a0091000-2d53-11f1-b348-d16e20c5a43e` | Chương VI TỔ CHỨC THỰC HIỆN... |
| 5 | 0.8036 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fdc33aa-2d53-11f1-99fa-8bc8d4ae1bc6]` | `9fdc33aa-2d53-11f1-99fa-8bc8d4ae1bc6` | a) Kẹp chì đối với tiền mới in;... |

### 3. HYBRID RESULTS (RRF)
| Rank | BM25 Rank | Dense Rank | RRF Score | Citation | Chunk ID |
|---|---|---|---|---|---|
| 1 | 5 | 1 | 0.031778 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fd88a8e-2d53-11f1-a687-91599fc7370e]` | `9fd88a8e-2d53-11f1-a687-91599fc7370e` |
| 2 | 9 | 2 | 0.030622 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fda8636-2d53-11f1-93c0-b927d170e4bb]` | `9fda8636-2d53-11f1-93c0-b927d170e4bb` |
| 3 | 10 | 3 | 0.030159 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fdc5aba-2d53-11f1-8202-39d25e163c85]` | `9fdc5aba-2d53-11f1-8202-39d25e163c85` |
| 4 | 8 | 6 | 0.029857 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fda8640-2d53-11f1-9e5f-05c153eb0a23]` | `9fda8640-2d53-11f1-9e5f-05c153eb0a23` |
| 5 | 2 | 15 | 0.029462 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fdca8d0-2d53-11f1-839b-d1bcb9053bea]` | `9fdca8d0-2d53-11f1-839b-d1bcb9053bea` |

### 4. AFTER RERANK (Cross-Encoder)
| Rank | Orig (Hybrid) Rank | Rerank Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|---|
| 1 | 1 | 2.4746 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fd88a8e-2d53-11f1-a687-91599fc7370e]` | `9fd88a8e-2d53-11f1-a687-91599fc7370e` | Điều 4. Đóng gói tiền mặt... |
| 2 | 20 | -0.6041 | `[01/2014/TT-NHNN | Điều 52. Đảm bảo an toàn trên đường vận chuyển | 9ffe13b2-2d53-11f1-b25d-59f3dd12eee6]` | `9ffe13b2-2d53-11f1-b25d-59f3dd12eee6` | 1. Tiền mặt, tài sản quý, giấy tờ có giá khi vận chuyển phải được đóng gói, niêm phong và được bảo q... |
| 3 | 12 | -0.8189 | `[01/2014/TT-NHNN | Mục 1 QUY ĐỊNH VỀ ĐÓNG GÓI NIÊM PHONG TIỀN MẶT, | 9fd88a84-2d53-11f1-a638-856f28930928]` | `9fd88a84-2d53-11f1-a638-856f28930928` | Mục 1 QUY ĐỊNH VỀ ĐÓNG GÓI NIÊM PHONG TIỀN MẶT,... |
| 4 | 2 | -0.9677 | `[01/2014/TT-NHNN | Điều 4. Đóng gói tiền mặt | 9fda8636-2d53-11f1-93c0-b927d170e4bb]` | `9fda8636-2d53-11f1-93c0-b927d170e4bb` | 6. Cục trưởng Cục Phát hành và Kho quỹ hướng dẫn quy cách đóng gói tiền mặt.... |
| 5 | 4 | -1.0666 | `[01/2014/TT-NHNN | Điều 5. Niêm phong tiền mặt | 9fda8640-2d53-11f1-9e5f-05c153eb0a23]` | `9fda8640-2d53-11f1-9e5f-05c153eb0a23` | Điều 5. Niêm phong tiền mặt... |

**Nhận xét về sự thay đổi thứ hạng sau Rerank**: BM25 và Hybrid đưa các điều khoản liên quan tới đóng gói và niêm phong của Thông tư 01 lên top. Sau khi qua Cross-Encoder Reranker, các chunk mô tả trực tiếp quy cách đóng gói tiền mặt (Điều 4) và niêm phong (Điều 5) được củng cố với điểm liên quan cao nhất.

---

## 2. Semantic (Diễn đạt ngữ nghĩa, không dùng đúng từ khóa)
**Câu hỏi**: `Ai có quyền phê duyệt quản lý dự trữ ngoại hối nhà nước và trách nhiệm của Thống đốc?`

### 1. BM25 RESULTS
| Rank | Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|
| 1 | 27.8549 | `[43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 628d3a30-2c04-11f1-a8b4-77345ec251ef]` | `628d3a30-2c04-11f1-a8b4-77345ec251ef` | 13. Sửa đổi, bổ sung điểm a và điểm c khoản 2 Điều 30 (đã được sửa đổi, bổ sung bởi khoản 13 Điều 1 ... |
| 2 | 27.2191 | `[43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 628af040-2c04-11f1-81d5-6f079586698a]` | `628af040-2c04-11f1-81d5-6f079586698a` | 7. Sửa đổi, bổ sung khoản 1 và khoản 5 Điều 14 (đã được sửa đổi, bổ sung bởi khoản 11 Điều 1 Thông t... |
| 3 | 26.6295 | `[135/2015/NĐ-CP | Điều 26. Tổng hạn mức đầu tư gián tiếp ra nước ngoài hàng năm | d521916c-df57-11f0-8558-5525609ac052]` | `d521916c-df57-11f0-8558-5525609ac052` | b) Quy mô dự trữ ngoại hối Nhà nước;... |
| 4 | 25.4819 | `[135/2015/NĐ-CP | Điều 30. Trách nhiệm của Ngân hàng Nhà nước Việt Nam | d521b552-df57-11f0-bd81-7974db10cc45]` | `d521b552-df57-11f0-bd81-7974db10cc45` | 5. Thực hiện quản lý ngoại hối đối với hoạt động đầu tư gián tiếp ra nước ngoài.... |
| 5 | 24.2225 | `[01/2014/TT-NHNN | Điều 48. Trách nhiệm tổ chức vận chuyển | 9ffc8ce0-2d53-11f1-9c4b-533bd8647175]` | `9ffc8ce0-2d53-11f1-9c4b-533bd8647175` | 2. Ngân hàng Nhà nước vận chuyển ngoại tệ ra nước ngoài phải có Lệnh của Thống đốc.... |

### 2. DENSE RESULTS
| Rank | Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|
| 1 | 0.7269 | `[01/2014/TT-NHNN | Điều 48. Trách nhiệm tổ chức vận chuyển | 9ffc8ce0-2d53-11f1-9c4b-533bd8647175]` | `9ffc8ce0-2d53-11f1-9c4b-533bd8647175` | 2. Ngân hàng Nhà nước vận chuyển ngoại tệ ra nước ngoài phải có Lệnh của Thống đốc.... |
| 2 | 0.7015 | `[01/2014/TT-NHNN | Điều 70. Trách nhiệm của các đơn vị liên quan thuộc Ngân hàng Nhà nước | a0091032-2d53-11f1-b23b-a158bd32f23e]` | `a0091032-2d53-11f1-b23b-a158bd32f23e` | 2. Vụ trưởng Vụ Kiểm toán nội bộ chịu trách nhiệm hướng dẫn kiểm soát việc tổ chức thực hiện trong h... |
| 3 | 0.7008 | `[01/2014/TT-NHNN | Điều 70. Trách nhiệm của các đơn vị liên quan thuộc Ngân hàng Nhà nước | a009103c-2d53-11f1-975d-898b1e3829cb]` | `a009103c-2d53-11f1-975d-898b1e3829cb` | 3. Chánh Thanh tra, giám sát ngân hàng có trách nhiệm thanh tra việc tổ chức thực hiện Thông tư này ... |
| 4 | 0.6889 | `[01/2014/TT-NHNN | Điều 70. Trách nhiệm của các đơn vị liên quan thuộc Ngân hàng Nhà nước | a0091028-2d53-11f1-9a8b-9b0ee753b8a7]` | `a0091028-2d53-11f1-9a8b-9b0ee753b8a7` | 1. Cục trưởng Cục Phát hành và Kho quỹ có trách nhiệm hướng dẫn và kiểm tra việc thực hiện Thông tư ... |
| 5 | 0.6874 | `[56/2024/TT-NHNN | Điều 5. Thẩm quyền quyết định cấp Giấy phép | a5e24dd0-1e98-11f1-82fa-3dadcee2abe9]` | `a5e24dd0-1e98-11f1-82fa-3dadcee2abe9` | 1. Thống đốc Ngân hàng Nhà nước có thẩm quyền quyết định cấp Giấy phép đối với ngân hàng thương mại ... |

### 3. HYBRID RESULTS (RRF)
| Rank | BM25 Rank | Dense Rank | RRF Score | Citation | Chunk ID |
|---|---|---|---|---|---|
| 1 | 5 | 1 | 0.031778 | `[01/2014/TT-NHNN | Điều 48. Trách nhiệm tổ chức vận chuyển | 9ffc8ce0-2d53-11f1-9c4b-533bd8647175]` | `9ffc8ce0-2d53-11f1-9c4b-533bd8647175` |
| 2 | 1 | - | 0.016393 | `[43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 628d3a30-2c04-11f1-a8b4-77345ec251ef]` | `628d3a30-2c04-11f1-a8b4-77345ec251ef` |
| 3 | 2 | - | 0.016129 | `[43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 628af040-2c04-11f1-81d5-6f079586698a]` | `628af040-2c04-11f1-81d5-6f079586698a` |
| 4 | - | 2 | 0.016129 | `[01/2014/TT-NHNN | Điều 70. Trách nhiệm của các đơn vị liên quan thuộc Ngân hàng Nhà nước | a0091032-2d53-11f1-b23b-a158bd32f23e]` | `a0091032-2d53-11f1-b23b-a158bd32f23e` |
| 5 | 3 | - | 0.015873 | `[135/2015/NĐ-CP | Điều 26. Tổng hạn mức đầu tư gián tiếp ra nước ngoài hàng năm | d521916c-df57-11f0-8558-5525609ac052]` | `d521916c-df57-11f0-8558-5525609ac052` |

### 4. AFTER RERANK (Cross-Encoder)
| Rank | Orig (Hybrid) Rank | Rerank Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|---|
| 1 | 3 | -1.528 | `[43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 628af040-2c04-11f1-81d5-6f079586698a]` | `628af040-2c04-11f1-81d5-6f079586698a` | 7. Sửa đổi, bổ sung khoản 1 và khoản 5 Điều 14 (đã được sửa đổi, bổ sung bởi khoản 11 Điều 1 Thông t... |
| 2 | 2 | -1.752 | `[43/2024/TT-NHNN | Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 01/2014/TT-NHNN | 628d3a30-2c04-11f1-a8b4-77345ec251ef]` | `628d3a30-2c04-11f1-a8b4-77345ec251ef` | 13. Sửa đổi, bổ sung điểm a và điểm c khoản 2 Điều 30 (đã được sửa đổi, bổ sung bởi khoản 13 Điều 1 ... |
| 3 | 11 | -2.118 | `[135/2015/NĐ-CP | Điều 39. Trách nhiệm thi hành | d521b6b0-df57-11f0-8486-0f09d2dd2de3]` | `d521b6b0-df57-11f0-8486-0f09d2dd2de3` | 2. Các Bộ trưởng, Thủ trưởng cơ quan ngang Bộ, Thủ trưởng cơ quan thuộc Chính phủ, Chủ tịch Ủy ban n... |
| 4 | 9 | -2.1312 | `[56/2024/TT-NHNN | Điều 5. Thẩm quyền quyết định cấp Giấy phép | a5e24dd0-1e98-11f1-82fa-3dadcee2abe9]` | `a5e24dd0-1e98-11f1-82fa-3dadcee2abe9` | 1. Thống đốc Ngân hàng Nhà nước có thẩm quyền quyết định cấp Giấy phép đối với ngân hàng thương mại ... |
| 5 | 8 | -2.1762 | `[01/2014/TT-NHNN | Điều 70. Trách nhiệm của các đơn vị liên quan thuộc Ngân hàng Nhà nước | a0091028-2d53-11f1-9a8b-9b0ee753b8a7]` | `a0091028-2d53-11f1-9a8b-9b0ee753b8a7` | 1. Cục trưởng Cục Phát hành và Kho quỹ có trách nhiệm hướng dẫn và kiểm tra việc thực hiện Thông tư ... |

**Nhận xét về sự thay đổi thứ hạng sau Rerank**: Reranker đóng vai trò then chốt: đánh giá trực tiếp sự tương thích ngữ nghĩa sâu giữa câu hỏi về thẩm quyền phê duyệt và nội dung các điều khoản, đưa các chunk về 'Quyền hạn và Lệnh của Thống đốc trong vận chuyển ngoại tệ' lên vị trí số 1 rõ rệt.

---

## 3. Mixed (Kết hợp từ khóa văn bản và ngữ nghĩa nghiệp vụ)
**Câu hỏi**: `Điều kiện cấp Giấy phép thành lập doanh nghiệp bảo hiểm theo Nghị định 73/2016/NĐ-CP`

### 1. BM25 RESULTS
| Rank | Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|
| 1 | 23.3922 | `[73/2016/NĐ-CP | Điều 6. Điều kiện chung để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp bảo hiểm, chi nhánh nước ngoài, doanh nghiệp môi giới bảo hiểm | b60c20b0-3049-11f1-8a16-6d91b4f282ee]` | `b60c20b0-3049-11f1-8a16-6d91b4f282ee` | 3. Có hồ sơ đề nghị cấp Giấy phép theo quy định tại Nghị định này.... |
| 2 | 21.3886 | `[73/2016/NĐ-CP | Điều 6. Điều kiện chung để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp bảo hiểm, chi nhánh nước ngoài, doanh nghiệp môi giới bảo hiểm | b0cf2898-df4c-11f0-b764-49ed834c2fa9]` | `b0cf2898-df4c-11f0-b764-49ed834c2fa9` | Điều 6. Điều kiện chung để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp bảo hiểm, chi ... |
| 3 | 21.0448 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b631aa10-3049-11f1-b1a7-43b8ff01b9e4]` | `b631aa10-3049-11f1-b1a7-43b8ff01b9e4` | 11. Văn bản cam kết của tổ chức, cá nhân góp vốn đối với việc đáp ứng điều kiện để được cấp Giấy phé... |
| 4 | 20.6458 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2]` | `b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2` | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm... |
| 5 | 20.2646 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b62ec3e0-3049-11f1-9418-95764e8ea6f7]` | `b62ec3e0-3049-11f1-9418-95764e8ea6f7` | 1. Văn bản đề nghị cấp Giấy phép theo mẫu do Bộ Tài chính quy định.... |

### 2. DENSE RESULTS
| Rank | Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|
| 1 | 0.8771 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2]` | `b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2` | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm... |
| 2 | 0.8757 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b62fd550-3049-11f1-b30e-0d0198c13230]` | `b62fd550-3049-11f1-b30e-0d0198c13230` | b) Đối với tổ chức:... |
| 3 | 0.8754 | `[46/2023/NĐ-CP | Điều 64. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e6dfb50-21ad-11f1-a772-b1365d93779b]` | `3e6dfb50-21ad-11f1-a772-b1365d93779b` | Điều 64. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm... |
| 4 | 0.8747 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b62fae40-3049-11f1-ae62-a7bc69a581c1]` | `b62fae40-3049-11f1-ae62-a7bc69a581c1` | a) Đối với cá nhân:... |
| 5 | 0.8735 | `[46/2023/NĐ-CP | Điều 63. Điều kiện về tài chính để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e674490-21ad-11f1-8851-257467c30926]` | `3e674490-21ad-11f1-8851-257467c30926` | 1. Tổ chức tham gia góp vốn từ 10% vốn điều lệ trở lên phải hoạt động kinh doanh có lãi trong 03 năm... |

### 3. HYBRID RESULTS (RRF)
| Rank | BM25 Rank | Dense Rank | RRF Score | Citation | Chunk ID |
|---|---|---|---|---|---|
| 1 | 4 | 1 | 0.032018 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2]` | `b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2` |
| 2 | 5 | 7 | 0.03031 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b62ec3e0-3049-11f1-9418-95764e8ea6f7]` | `b62ec3e0-3049-11f1-9418-95764e8ea6f7` |
| 3 | 3 | 12 | 0.029762 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b631aa10-3049-11f1-b1a7-43b8ff01b9e4]` | `b631aa10-3049-11f1-b1a7-43b8ff01b9e4` |
| 4 | 7 | 15 | 0.028259 | `[46/2023/NĐ-CP | Điều 63. Điều kiện về tài chính để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e66f670-21ad-11f1-8b62-8912fd3748c1]` | `3e66f670-21ad-11f1-8b62-8912fd3748c1` |
| 5 | 1 | - | 0.016393 | `[73/2016/NĐ-CP | Điều 6. Điều kiện chung để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp bảo hiểm, chi nhánh nước ngoài, doanh nghiệp môi giới bảo hiểm | b60c20b0-3049-11f1-8a16-6d91b4f282ee]` | `b60c20b0-3049-11f1-8a16-6d91b4f282ee` |

### 4. AFTER RERANK (Cross-Encoder)
| Rank | Orig (Hybrid) Rank | Rerank Score | Citation | Chunk ID | Snippet |
|---|---|---|---|---|---|
| 1 | 6 | 2.2298 | `[73/2016/NĐ-CP | Điều 6. Điều kiện chung để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp bảo hiểm, chi nhánh nước ngoài, doanh nghiệp môi giới bảo hiểm | b0cf2898-df4c-11f0-b764-49ed834c2fa9]` | `b0cf2898-df4c-11f0-b764-49ed834c2fa9` | Điều 6. Điều kiện chung để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp bảo hiểm, chi ... |
| 2 | 1 | -0.2401 | `[73/2016/NĐ-CP | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2]` | `b0cf2d5c-df4c-11f0-9332-8f9f22ad17c2` | Điều 14. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm... |
| 3 | 4 | -0.3627 | `[46/2023/NĐ-CP | Điều 63. Điều kiện về tài chính để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e66f670-21ad-11f1-8b62-8912fd3748c1]` | `3e66f670-21ad-11f1-8b62-8912fd3748c1` | Điều 63. Điều kiện về tài chính để được cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi gi... |
| 4 | 18 | -0.9547 | `[46/2023/NĐ-CP | Điều 64. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e724110-21ad-11f1-a7b7-9d8aafa8a9dc]` | `3e724110-21ad-11f1-a7b7-9d8aafa8a9dc` | 3. Phương án hoạt động 05 năm đầu phù hợp với lĩnh vực kinh doanh đề nghị cấp Giấy phép, trong đó nê... |
| 5 | 17 | -1.0152 | `[46/2023/NĐ-CP | Điều 64. Hồ sơ đề nghị cấp Giấy phép thành lập và hoạt động của doanh nghiệp môi giới bảo hiểm | 3e9c5e50-21ad-11f1-add9-0500172c96e2]` | `3e9c5e50-21ad-11f1-add9-0500172c96e2` | 14. Văn bản cam kết của tổ chức, cá nhân góp vốn đối với việc đáp ứng điều kiện để được cấp Giấy phé... |

**Nhận xét về sự thay đổi thứ hạng sau Rerank**: Cross-Encoder tái sắp xếp chính xác: đẩy Điều 6 (Điều kiện chung cấp phép) và Điều 14 (Hồ sơ đề nghị cấp phép) lên vị trí top đầu, lọc bỏ các chunk chỉ chứa từ khóa trùng tên mà không chứa nội dung điều kiện thực sự.

---

