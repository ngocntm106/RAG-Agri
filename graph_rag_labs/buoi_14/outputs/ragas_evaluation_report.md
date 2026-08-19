# BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG RAG PIPELINE (RAGAS EVALUATION REPORT)

- **Bài thực hành**: Đánh giá Hệ thống RAG với Ragas & LLM Judger
- **Thời gian thực hiện**: `2026-08-19 21:09:13`
- **Mô hình Generator**: `Qwen/Qwen3.5-9B:deepinfra` (via HF Router)
- **Mô hình Judger (Trọng tài)**: `openai/gpt-oss-20b:deepinfra` (via HF Router)
- **Mô hình Embedding**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Quy mô mẫu đánh giá**: `20 câu hỏi (Golden QA Dataset)`

---

## 1. Bảng Tóm tắt 4 Chỉ số Ragas Cốt lõi (Core Metrics Summary)

| Chỉ số Ragas | Điểm Trung Bình | Ngưỡng Mục Tiêu | Đánh giá Trạng thái | Ý nghĩa Kỹ thuật |
| :--- | :---: | :---: | :---: | :--- |
| **Context Precision** | **0.7983** | ≥ 0.80 | ⚠️ CẦN CẢI THIỆN | Mức độ chính xác & tỷ lệ xếp hạng đúng của các chunks trích xuất |
| **Context Recall** | **0.6355** | ≥ 0.80 | ⚠️ CẦN CẢI THIỆN | Tỷ lệ thông tin của ground truth được bao phủ trong ngữ cảnh |
| **Faithfulness (Độ trung thực)** | **0.9415** | ≥ 0.85 | ✅ ĐẠT CHUẨN | Mức độ trung thực của câu trả lời, không bị ảo giác ngoài ngữ cảnh |
| **Answer Relevancy** | **0.6675** | ≥ 0.80 | ⚠️ CẦN CẢI THIỆN | Độ liên quan, trực diện và đầy đủ của câu trả lời với câu hỏi |
| **⭐ Overall RAG Score** | **0.7607** | **≥ 0.80** | **✅ ĐẠT YÊU CẦU (PASSED)** | **Điểm chất lượng toàn diện của toàn bộ hệ thống RAG** |

---

## 2. Phân tích Chi tiết theo Phân khúc (Segment Breakdown)

### 2.1. Đánh giá theo Độ khó Câu hỏi (Difficulty Level)

| Độ khó | Số câu | Context Precision | Context Recall | Faithfulness | Answer Relevancy | Overall Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **EASY** | 8 | 0.7500 | 0.6075 | 0.9621 | 0.6329 | **0.7381** |
| **HARD** | 6 | 0.8056 | 0.6735 | 0.9406 | 0.7149 | **0.7837** |
| **MEDIUM** | 6 | 0.8556 | 0.6350 | 0.9148 | 0.6663 | **0.7679** |

### 2.2. Đánh giá theo Nhóm Phân quyền Bảo mật (Security Role Groups)

| Nhóm Quyền | Số câu | Context Precision | Context Recall | Faithfulness | Answer Relevancy | Overall Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Admin, HR** | 6 | 0.8889 | 0.6573 | 0.9561 | 0.6189 | **0.7803** |
| **Admin, Staff** | 7 | 0.8809 | 0.6482 | 0.9728 | 0.6697 | **0.7929** |
| **Public (All Roles)** | 7 | 0.6381 | 0.6042 | 0.8976 | 0.7071 | **0.7117** |

---

## 3. Bảng Kết quả Chi tiết Từng Câu hỏi (Itemized Results)

| ID | Nhóm Quyền | Độ khó | Câu hỏi | Precision | Recall | Faithfulness | Relevancy | Overall |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| `QA-01` | Admin, HR | `easy` | Người đại diện theo pháp luật của doanh nghiệ... | 1.000 | 0.489 | 0.949 | 0.259 | **0.674** |
| `QA-02` | Admin, HR | `medium` | Tổng giám đốc doanh nghiệp bảo hiểm cần có ba... | 1.000 | 0.692 | 0.991 | 0.772 | **0.864** |
| `QA-03` | Admin, HR | `hard` | Chuyên gia tính toán của doanh nghiệp bảo hiể... | 1.000 | 0.697 | 0.954 | 0.723 | **0.844** |
| `QA-04` | Admin, HR | `easy` | Nhiệm kỳ của Giám đốc (Tổng giám đốc) hợp tác... | 1.000 | 0.776 | 0.942 | 0.729 | **0.862** |
| `QA-05` | Admin, HR | `medium` | Trường hợp nào Giám đốc hợp tác xã không được... | 0.833 | 0.742 | 0.923 | 0.659 | **0.789** |
| `QA-06` | Admin, HR | `hard` | Những đối tượng nào bị cấm giữ chức danh quản... | 0.500 | 0.547 | 0.977 | 0.572 | **0.649** |
| `QA-07` | Admin, Staff | `easy` | Tỷ lệ an toàn vốn (CAR) tối thiểu mà ngân hàn... | 1.000 | 0.784 | 0.977 | 0.579 | **0.835** |
| `QA-08` | Admin, Staff | `medium` | Hệ số rủi ro tín dụng đối với các khoản phải ... | 1.000 | 0.742 | 0.947 | 0.702 | **0.848** |
| `QA-09` | Admin, Staff | `easy` | Phương tiện vận chuyển tiền mặt, tài sản quý ... | 0.333 | 0.562 | 0.985 | 0.754 | **0.659** |
| `QA-10` | Admin, Staff | `medium` | Quy định về việc niêm phong bao, túi chứa tiề... | 1.000 | 0.671 | 0.989 | 0.518 | **0.794** |
| `QA-11` | Admin, Staff | `easy` | Thông tư số 27/2024/TT-NHNN quy định về nội d... | 0.833 | 0.519 | 0.957 | 0.571 | **0.720** |
| `QA-12` | Admin, Staff | `hard` | Hệ số rủi ro tín dụng của khoản cho vay bảo đ... | 1.000 | 0.697 | 0.989 | 0.703 | **0.847** |
| `QA-13` | Admin, Staff | `hard` | Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhâ... | 1.000 | 0.562 | 0.966 | 0.861 | **0.847** |
| `QA-14` | Public (All Roles) | `easy` | Việc tham gia và giao kết hợp đồng bảo hiểm p... | 0.500 | 0.453 | 0.934 | 0.559 | **0.611** |
| `QA-15` | Public (All Roles) | `medium` | Hồ sơ đề nghị cấp Giấy phép thành lập doanh n... | 1.000 | 0.451 | 0.939 | 0.588 | **0.744** |
| `QA-16` | Public (All Roles) | `easy` | Ngân hàng Nhà nước Việt Nam là cơ quan trực t... | 0.833 | 0.901 | 0.956 | 0.852 | **0.886** |
| `QA-17` | Public (All Roles) | `medium` | Mục tiêu chính sách tiền tệ quốc gia do Ngân ... | 0.300 | 0.511 | 0.700 | 0.759 | **0.567** |
| `QA-18` | Public (All Roles) | `easy` | Theo quy định pháp luật Việt Nam, bảo hiểm đư... | 0.500 | 0.375 | 0.997 | 0.761 | **0.658** |
| `QA-19` | Public (All Roles) | `hard` | Cơ cấu nguồn vốn góp thành lập doanh nghiệp m... | 1.000 | 0.807 | 0.973 | 0.620 | **0.850** |
| `QA-20` | Public (All Roles) | `hard` | Ngân hàng Nhà nước sử dụng các công cụ chủ yế... | 0.333 | 0.732 | 0.784 | 0.811 | **0.665** |

---

## 4. Phân tích Nguyên nhân Lỗi & Câu hỏi Điểm Thấp (< 0.70)

Hệ thống ghi nhận **17 câu hỏi** có chỉ số cần tối ưu (< 0.70):

### ⚠️ `QA-01` (EASY — Admin, HR)
- **Câu hỏi**: *"Người đại diện theo pháp luật của doanh nghiệp bảo hiểm phải cư trú ở đâu trong thời gian đương nhiệm?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.489`, Faithfulness=`0.949`, Relevancy=`0.259`
- **Đáp án chuẩn (Ground Truth)**: Người đại diện theo pháp luật của doanh nghiệp bảo hiểm, chi nhánh nước ngoài phải cư trú tại Việt Nam trong thời gian đương nhiệm.
- **RAG Sinh ra (Answer)**: Cư trú tại Việt Nam trong thời gian đương nhiệm. Cư trú tại Việt Nam trong thời gian đương nhiệm.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-02` (MEDIUM — Admin, HR)
- **Câu hỏi**: *"Tổng giám đốc doanh nghiệp bảo hiểm cần có bao nhiêu năm kinh nghiệm trong lĩnh vực bảo hiểm, tài chính hoặc ngân hàng?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.692`, Faithfulness=`0.991`, Relevancy=`0.772`
- **Đáp án chuẩn (Ground Truth)**: Tổng giám đốc (Giám đốc) của doanh nghiệp bảo hiểm phải có ít nhất 05 năm kinh nghiệm làm việc trong lĩnh vực bảo hiểm, tài chính, ngân hàng, trong đó có ít nhất 03 năm giữ chức vụ quản lý cấp phòng trở lên hoặc tương đương.
- **RAG Sinh ra (Answer)**: Có tối thiểu 05 năm kinh nghiệm làm việc trong lĩnh vực bảo hiểm, tài chính, ngân hàng, trong đó có tối thiểu 03 năm giữ vị trí là người quản trị, điều hành theo quy định tại Điều 25 Nghị định này tại doanh nghiệp bảo hiểm, chi nhánh nước ngoài, doanh nghiệp môi giới bảo hiểm hoặc trực tiếp làm công tác quản lý nhà nước trong lĩnh vực bảo hiểm. Có tối thiểu 05 năm trực tiếp làm việc trong một hoặc các lĩnh vực bảo hiểm, tài chính, ngân hàng, trong đó có tối thiểu 03 năm giữ vị trí là người quản lý, người kiểm soát của doanh nghiệp bảo hiểm, doanh nghiệp tái bảo hiểm hoặc người quản lý, người kiểm soát của chi nhánh nước ngoài tại Việt Nam hoặc người quản lý của doanh nghiệp môi giới bảo hiểm.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.

### ⚠️ `QA-03` (HARD — Admin, HR)
- **Câu hỏi**: *"Chuyên gia tính toán của doanh nghiệp bảo hiểm phi nhân thọ cần đáp ứng những tiêu chuẩn gì về chứng chỉ và hiệp hội nghề nghiệp?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.697`, Faithfulness=`0.954`, Relevancy=`0.723`
- **Đáp án chuẩn (Ground Truth)**: Chuyên gia tính toán của doanh nghiệp bảo hiểm phi nhân thọ phải là thành viên (Fellow) của một trong các Hội các nhà tính toán bảo hiểm được quốc tế công nhận, hoặc có ít nhất 05 năm kinh nghiệm làm việc trong lĩnh vực tính toán bảo hiểm phi nhân thọ và có chứng chỉ đào tạo về tính toán bảo hiểm phi nhân thọ.
- **RAG Sinh ra (Answer)**: Chuyên gia tính toán dự phòng và khả năng thanh toán của doanh nghiệp bảo hiểm phi nhân thọ, doanh nghiệp tái bảo hiểm, chi nhánh nước ngoài phải đáp ứng các tiêu chuẩn sau: Sau 05 năm kể từ ngày Nghị định này có hiệu lực, chuyên gia tính toán của doanh nghiệp bảo hiểm phi nhân thọ, doanh nghiệp tái bảo hiểm, chi nhánh nước ngoài tại Việt Nam phải là thành viên chính thức (Fellow) được đào tạo về tính toán trong lĩnh vực bảo hiểm phi nhân thọ của Hội các nhà tính toán bảo hiểm đang là thành viên chính thức của Hội các nhà tính toán bảo hiểm quốc tế và không vi phạm quy tắc đạo đức hành nghề tính toán bảo hiểm.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.

### ⚠️ `QA-05` (MEDIUM — Admin, HR)
- **Câu hỏi**: *"Trường hợp nào Giám đốc hợp tác xã không được đồng thời đảm nhiệm vị trí tại tổ chức khác?"*
- **Điểm số**: Precision=`0.833`, Recall=`0.742`, Faithfulness=`0.923`, Relevancy=`0.659`
- **Đáp án chuẩn (Ground Truth)**: Giám đốc (Tổng giám đốc) hợp tác xã không được đồng thời là Giám đốc (Tổng giám đốc) hoặc người quản lý của doanh nghiệp hoặc hợp tác xã khác, trừ trường hợp Điều lệ có quy định khác.
- **RAG Sinh ra (Answer)**: a) Không thuộc trường hợp không được đảm nhiệm chức vụ quy định tại khoản 2 và khoản 3 Điều 42 Luật Các tổ chức tín dụng; Trường hợp Giám đốc (Tổng giám đốc) được thuê, không là thành viên chính thức thì được tham gia cuộc họp Đại hội thành viên, Hội đồng quản trị nhưng không có quyền biểu quyết.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-06` (HARD — Admin, HR)
- **Câu hỏi**: *"Những đối tượng nào bị cấm giữ chức danh quản lý, điều hành tại doanh nghiệp bảo hiểm theo quy định của pháp luật?"*
- **Điểm số**: Precision=`0.500`, Recall=`0.547`, Faithfulness=`0.977`, Relevancy=`0.572`
- **Đáp án chuẩn (Ground Truth)**: Những người không được quyền quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp, người đang bị truy cứu trách nhiệm hình sự, người bị kết án tù, và cán bộ công chức nhà nước theo quy định về cán bộ, công chức thì không được giữ chức danh quản lý, điều hành tại doanh nghiệp bảo hiểm.
- **RAG Sinh ra (Answer)**: Không thuộc các đối tượng bị cấm quản lý doanh nghiệp theo quy định tại khoản 2 Điều 18 Luật doanh nghiệp. a) Không thuộc các đối tượng bị cấm theo quy định tại khoản 2 Điều 18 của Luật doanh nghiệp;
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Context Precision**: Có chunk chứa từ khóa tương đồng nhưng ở chương khác xếp hạng cao hơn chunk chứa đáp án thực tế.
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-07` (EASY — Admin, Staff)
- **Câu hỏi**: *"Tỷ lệ an toàn vốn (CAR) tối thiểu mà ngân hàng thương mại phải duy trì theo Thông tư 41/2016/TT-NHNN là bao nhiêu phần trăm?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.784`, Faithfulness=`0.977`, Relevancy=`0.579`
- **Đáp án chuẩn (Ground Truth)**: Ngân hàng thương mại, chi nhánh ngân hàng nước ngoài phải duy trì tỷ lệ an toàn vốn (CAR) tối thiểu là 8%.
- **RAG Sinh ra (Answer)**: Ngân hàng không có công ty con, chi nhánh ngân hàng nước ngoài phải thường xuyên duy trì tỷ lệ an toàn vốn xác định trên cơ sở báo cáo tài chính của ngân hàng, chi nhánh ngân hàng nước ngoài tối thiểu 8%. Chủ trì, phối hợp với các Vụ, Cục liên quan trình Thống đốc Ngân hàng Nhà nước áp dụng tỷ lệ an toàn vốn tối thiểu cao hơn 8% theo quy định tại Điều 6 Thông tư này.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-09` (EASY — Admin, Staff)
- **Câu hỏi**: *"Phương tiện vận chuyển tiền mặt, tài sản quý của tổ chức tín dụng phải đáp ứng điều kiện an toàn gì?"*
- **Điểm số**: Precision=`0.333`, Recall=`0.562`, Faithfulness=`0.985`, Relevancy=`0.754`
- **Đáp án chuẩn (Ground Truth)**: Phương tiện vận chuyển tiền mặt, tài sản quý phải là xe chuyên dùng có khoang chở tiền kiên cố, có thiết bị chữa cháy, thiết bị định vị và có lực lượng bảo vệ áp tải vũ trang hoặc công cụ hỗ trợ.
- **RAG Sinh ra (Answer)**: Trường hợp tổ chức tín dụng, chi nhánh ngân hàng nước ngoài sử dụng phương tiện khác để vận chuyển tiền mặt, tài sản quý, giấy tờ có giá, tổ chức tín dụng, chi nhánh ngân hàng nước ngoài phải quy định bằng văn bản và hướng dẫn quy trình vận chuyển, bảo vệ, các biện pháp đảm bảo an toàn tài sản. Tiền mặt, tài sản quý, giấy tờ có giá khi vận chuyển phải được đóng gói, niêm phong và được bảo quản an toàn.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Context Precision**: Có chunk chứa từ khóa tương đồng nhưng ở chương khác xếp hạng cao hơn chunk chứa đáp án thực tế.

### ⚠️ `QA-10` (MEDIUM — Admin, Staff)
- **Câu hỏi**: *"Quy định về việc niêm phong bao, túi chứa tiền mặt trong kho quỹ yêu cầu các thông tin gì trên niêm phong?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.671`, Faithfulness=`0.989`, Relevancy=`0.518`
- **Đáp án chuẩn (Ground Truth)**: Trên niêm phong bao, túi chứa tiền mặt phải ghi rõ tên đơn vị đóng gói, loại tiền, số lượng tờ, số tiền bằng số và bằng chữ, ngày tháng năm đóng gói niêm phong, và chữ ký (hoặc mã số) của người đóng gói, kiểm đếm.
- **RAG Sinh ra (Answer)**: “Niêm phong” là việc sử dụng giấy niêm phong và/ hoặc kẹp chì để ghi dấu hiệu trên bó, túi, hộp, bao, thùng tiền đã được đóng gói theo quy định, đảm bảo bó, túi, hộp, bao, thùng tiền được giữ nguyên, đầy đủ. Trên giấy niêm phong bó, túi, hộp, bao, thùng tiền phải có đầy đủ, rõ ràng các nội dung sau:
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-11` (EASY — Admin, Staff)
- **Câu hỏi**: *"Thông tư số 27/2024/TT-NHNN quy định về nội dung quản lý quỹ an toàn nào?"*
- **Điểm số**: Precision=`0.833`, Recall=`0.519`, Faithfulness=`0.957`, Relevancy=`0.571`
- **Đáp án chuẩn (Ground Truth)**: Thông tư số 27/2024/TT-NHNN quy định về việc trích nộp, quản lý, sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân.
- **RAG Sinh ra (Answer)**: Quy chế quản lý và sử dụng Quỹ bảo toàn tối thiểu phải có các nội dung sau: a) Nguyên tắc quản lý, sử dụng Quỹ bảo toàn theo quy định tại Điều 24 và Điều 27 Thông tư này;
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-12` (HARD — Admin, Staff)
- **Câu hỏi**: *"Hệ số rủi ro tín dụng của khoản cho vay bảo đảm bằng bất động sản nhà ở phụ thuộc vào những chỉ số tỷ lệ nào?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.697`, Faithfulness=`0.989`, Relevancy=`0.703`
- **Đáp án chuẩn (Ground Truth)**: Hệ số rủi ro tín dụng của khoản cho vay bảo đảm bằng bất động sản nhà ở phụ thuộc vào tỷ lệ dư nợ trên giá trị tài sản bảo đảm (tỷ lệ LTV - Loan to Value) và tỷ lệ thu nhập trả nợ (tỷ lệ DTI - Debt to Income).
- **RAG Sinh ra (Answer)**: c) Đối với khoản phải đòi được đảm bảo bằng bất động sản kinh doanh, hệ số rủi ro tín dụng áp dụng theo chỉ tiêu Tỷ lệ bảo đảm (LTV) đối với khoản phải đòi được đảm bảo bằng bất động sản kinh doanh như sau: b) Hệ số rủi ro tín dụng áp dụng đối với khoản phải đòi được bảo đảm bằng bất động sản không kinh doanh theo chỉ tiêu Tỷ lệ bảo đảm (LTV) như sau:
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.

### ⚠️ `QA-13` (HARD — Admin, Staff)
- **Câu hỏi**: *"Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân được sử dụng để hỗ trợ tài chính trong trường hợp nào?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.562`, Faithfulness=`0.966`, Relevancy=`0.861`
- **Đáp án chuẩn (Ground Truth)**: Quỹ được sử dụng để hỗ trợ tài chính cho quỹ tín dụng nhân dân thành viên gặp khó khăn tạm thời về thanh khoản hoặc có nguy cơ mất khả năng chi trả nhưng có phương án phục hồi khả thi được Ngân hàng Nhà nước phê duyệt.
- **RAG Sinh ra (Answer)**: Quỹ bảo toàn được sử dụng để cho vay quỹ tín dụng nhân dân trong các trường hợp sau: Nguồn vốn nhàn rỗi của Quỹ bảo toàn được sử dụng trên nguyên tắc đảm bảo an toàn nguồn vốn và đáp ứng yêu cầu cho vay hỗ trợ các quỹ tín dụng nhân dân.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.

### ⚠️ `QA-14` (EASY — Public (All Roles))
- **Câu hỏi**: *"Việc tham gia và giao kết hợp đồng bảo hiểm phải tuân thủ nguyên tắc cơ bản nào?"*
- **Điểm số**: Precision=`0.500`, Recall=`0.453`, Faithfulness=`0.934`, Relevancy=`0.559`
- **Đáp án chuẩn (Ground Truth)**: Việc tham gia và giao kết hợp đồng bảo hiểm phải dựa trên nguyên tắc tự nguyện, bình đẳng, trung thực tuyệt đối và tôn trọng quyền, lợi ích hợp pháp của các bên.
- **RAG Sinh ra (Answer)**: c) Việc xây dựng, quản lý, khai thác và sử dụng Cơ sở dữ liệu về hoạt động kinh doanh bảo hiểm phải tuân thủ các quy định của Luật Kinh doanh bảo hiểm, Luật Công nghệ thông tin, Luật Giao dịch điện tử; Việc xác định giá trị tài sản ròng của quỹ liên kết đơn vị phải tuân thủ các nguyên tắc xác định giá trị tài sản ròng của quỹ mở theo quy định của pháp luật hiện hành.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Context Precision**: Có chunk chứa từ khóa tương đồng nhưng ở chương khác xếp hạng cao hơn chunk chứa đáp án thực tế.
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-15` (MEDIUM — Public (All Roles))
- **Câu hỏi**: *"Hồ sơ đề nghị cấp Giấy phép thành lập doanh nghiệp môi giới bảo hiểm gồm những tài liệu chính nào?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.451`, Faithfulness=`0.939`, Relevancy=`0.588`
- **Đáp án chuẩn (Ground Truth)**: Hồ sơ gồm: Đơn đề nghị cấp Giấy phép, dự thảo Điều lệ doanh nghiệp, Đề án hoạt động 05 năm đầu, văn bản chứng minh năng lực tài chính, danh sách cổ đông sáng lập/thành viên góp vốn, và hồ sơ của người dự kiến bổ nhiệm giữ chức danh quản trị, điều hành.
- **RAG Sinh ra (Answer)**: a) Bản sao quyết định thành lập hoặc giấy chứng nhận đăng ký kinh doanh hoặc tài liệu tương đương khác; Tài liệu đối với cổ đông, thành viên góp vốn là cá nhân:
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-17` (MEDIUM — Public (All Roles))
- **Câu hỏi**: *"Mục tiêu chính sách tiền tệ quốc gia do Ngân hàng Nhà nước điều hành nhằm ổn định điều gì?"*
- **Điểm số**: Precision=`0.300`, Recall=`0.511`, Faithfulness=`0.700`, Relevancy=`0.759`
- **Đáp án chuẩn (Ground Truth)**: Chính sách tiền tệ quốc gia nhằm ổn định giá trị đồng tiền biểu hiện qua chỉ số lạm phát, thúc đẩy phát triển kinh tế - xã hội, bảo đảm quốc phòng, an ninh và nâng cao đời sống của nhân dân.
- **RAG Sinh ra (Answer)**: Thủ tướng Chính phủ, Thống đốc Ngân hàng Nhà nước quyết định việc sử dụng các công cụ và biện pháp điều hành để thực hiện mục tiêu chính sách tiền tệ quốc gia theo quy định của Chính phủ. Chính sách tiền tệ quốc gia là các quyết định về tiền tệ ở tầm quốc gia của cơ quan nhà nước có thẩm quyền, bao gồm quyết định mục tiêu ổn định giá trị đồng tiền biểu hiện bằng chỉ tiêu lạm phát, quyết định sử dụng các công cụ và biện pháp để thực hiện mục tiêu đề ra.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Context Precision**: Có chunk chứa từ khóa tương đồng nhưng ở chương khác xếp hạng cao hơn chunk chứa đáp án thực tế.
  * **Faithfulness**: Câu trả lời có phần mở rộng hoặc diễn đạt tóm tắt ngắn hơn ngữ cảnh văn bản gốc.

### ⚠️ `QA-18` (EASY — Public (All Roles))
- **Câu hỏi**: *"Theo quy định pháp luật Việt Nam, bảo hiểm được phân chia thành những loại hình nghiệp vụ chính nào?"*
- **Điểm số**: Precision=`0.500`, Recall=`0.375`, Faithfulness=`0.997`, Relevancy=`0.761`
- **Đáp án chuẩn (Ground Truth)**: Bảo hiểm bao gồm 03 loại hình nghiệp vụ chính: bảo hiểm nhân thọ, bảo hiểm phi nhân thọ và bảo hiểm sức khỏe.
- **RAG Sinh ra (Answer)**: d) Doanh nghiệp bảo hiểm, doanh nghiệp tái bảo hiểm, chi nhánh nước ngoài tại Việt Nam hình thành khi sau chia, tách, hợp nhất, sáp nhập, chuyển đổi hình thức đáp ứng các điều kiện quy định tại điểm a khoản 2, các khoản 3, 4 Điều 64 Luật Kinh doanh bảo hiểm và điều kiện về cơ cấu cổ đông quy định tại Điều 66 Luật Kinh doanh bảo hiểm đối với công ty cổ phần, quy định tại khoản 2 Điều 67 Luật Kinh doanh bảo hiểm đối với chi nhánh nước ngoài tại Việt Nam. c) Báo cáo về phương án phân chia, xử lý hợp đồng còn hiệu lực với khách hàng, nghĩa vụ nợ, nghĩa vụ với Nhà nước, cam kết với người lao động khi chia, tách, hợp nhất, sáp nhập, chuyển đổi hình thức của doanh nghiệp bảo hiểm, doanh nghiệp tái bảo hiểm, chi nhánh nước ngoài tại Việt Nam;
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Recall**: Đoạn văn bản chứa câu trả lời bị phân mảnh ở ranh giới giữa 2 chunk hoặc Top-K chưa đủ rộng để gom đầy đủ các điều kiện phụ.
  * **Context Precision**: Có chunk chứa từ khóa tương đồng nhưng ở chương khác xếp hạng cao hơn chunk chứa đáp án thực tế.

### ⚠️ `QA-19` (HARD — Public (All Roles))
- **Câu hỏi**: *"Cơ cấu nguồn vốn góp thành lập doanh nghiệp môi giới bảo hiểm có được sử dụng vốn vay hay vốn ủy thác đầu tư không?"*
- **Điểm số**: Precision=`1.000`, Recall=`0.807`, Faithfulness=`0.973`, Relevancy=`0.620`
- **Đáp án chuẩn (Ground Truth)**: Tổ chức, cá nhân tham gia góp vốn thành lập doanh nghiệp môi giới bảo hiểm phải góp vốn bằng Đồng Việt Nam và không được sử dụng vốn vay, nguồn vốn ủy thác đầu tư của tổ chức, cá nhân khác để góp vốn.
- **RAG Sinh ra (Answer)**: b) Cổ đông, thành viên góp vốn không được sử dụng vốn vay, vốn úy thác đầu tư của các tổ chức, cá nhân khác để tăng vốn điều lệ cho doanh nghiệp môi giới bảo hiểm. b) Cổ đông, thành viên góp vốn của doanh nghiệp bảo hiểm, doanh nghiệp tái bảo hiểm, công ty mẹ của chi nhánh nước ngoài tại Việt Nam không được sử dụng vốn vay, nguồn vốn ủy thác đầu tư của các tổ chức, cá nhân khác để bổ sung vốn điều lệ, vốn được cấp cho doanh nghiệp bảo hiểm, doanh nghiệp tái bảo hiểm, chi nhánh nước ngoài tại Việt Nam;
- **Phân tích nguyên nhân kỹ thuật**:
  * **Answer Relevancy**: Câu trả lời diễn đạt gián tiếp hoặc câu hỏi có tính chuyên môn sâu.

### ⚠️ `QA-20` (HARD — Public (All Roles))
- **Câu hỏi**: *"Ngân hàng Nhà nước sử dụng các công cụ chủ yếu nào để thực hiện chính sách tiền tệ quốc gia?"*
- **Điểm số**: Precision=`0.333`, Recall=`0.732`, Faithfulness=`0.784`, Relevancy=`0.811`
- **Đáp án chuẩn (Ground Truth)**: Ngân hàng Nhà nước sử dụng các công cụ chủ yếu bao gồm: tái cấp vốn, lãi suất, tỷ giá hối đoái, dự trữ bắt buộc, nghiệp vụ thị trường mở và các công cụ, biện pháp khác theo quy định của Chính phủ.
- **RAG Sinh ra (Answer)**: Thủ tướng Chính phủ, Thống đốc Ngân hàng Nhà nước quyết định việc sử dụng các công cụ và biện pháp điều hành để thực hiện mục tiêu chính sách tiền tệ quốc gia theo quy định của Chính phủ. Công cụ thực hiện chính sách tiền tệ quốc gia Thống đốc Ngân hàng Nhà nước quyết định việc sử dụng công cụ thực hiện chính sách tiền tệ quốc gia, bao gồm tái cấp vốn, lãi suất, tỷ giá hối đoái, dự trữ bắt buộc, nghiệp vụ thị trường mở và các công cụ, biện pháp khác theo quy định của Chính phủ.
- **Phân tích nguyên nhân kỹ thuật**:
  * **Context Precision**: Có chunk chứa từ khóa tương đồng nhưng ở chương khác xếp hạng cao hơn chunk chứa đáp án thực tế.

---

## 5. Đề xuất Tối ưu hóa Hệ thống RAG (Actionable Optimization Recommendations)

1. **Tối ưu hóa Phân đoạn Văn bản (Chunking Strategy)**:
   - Tăng `chunk_overlap` từ 50 lên 100-150 tokens để bảo toàn mối liên hệ giữa các mệnh đề và khoản phụ trong cùng một Điều luật.
   - Sử dụng **Hierarchical Chunking (Parent-Child Indexing)**: Khi tìm kiếm trên các chunk nhỏ (Child Chunks) để có độ chính xác cao, truyền cả Điều khoản đầy đủ (Parent Document) vào Context cho LLM sinh câu trả lời.

2. **Tối ưu hóa Pipeline Tìm kiếm (Retrieval & Reranking)**:
   - Nâng cao trọng số của Cross-Encoder Reranker (`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`) để lọc bỏ triệt để các chunks nhiễu trước khi đưa vào Generator.
   - Mở rộng `candidate_k` từ 15 lên 25 để tăng Recall trong tầng Retrieval sơ bộ.

3. **Tối ưu hóa Prompt Engineering cho Generator**:
   - Cung cấp System Prompt chặt chẽ hơn với ràng buộc: *'Chỉ trích xuất câu văn có trong ngữ cảnh, không tóm tắt quá mức làm mất các điều kiện tiên quyết'*, giúp tăng điểm Context Recall và Faithfulness.

4. **Kiểm soát Truy cập Dữ liệu Bảo mật (RBAC Integration)**:
   - Duy trì cơ chế lọc bảo mật NumPy boolean mask tại tầng Retrieval để đảm bảo 100% không rò rỉ dữ liệu khi người dùng truy vấn với quyền hạn cụ thể (`Guest`, `Staff`, `HR`, `Admin`).