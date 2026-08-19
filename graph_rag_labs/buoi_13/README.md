# Wiki Risk Graph MVP 🧠

Dự án xây dựng Wiki tri thức quản trị rủi ro dạng đồ thị (Knowledge Graph) phục vụ đào tạo, hỗ trợ liên kết các thực thể Kiểm soát nghiệp vụ, Hồ sơ rủi ro và Sự cố/Sự kiện thực tế.

---

## 📁 Cấu trúc thư mục dự án

```text
buoi_13/
├── data/                       # Dữ liệu seed nguồn (.csv)
├── wiki/                       # Wiki Markdown tương thích Obsidian (tự động sinh)
│   ├── Home.md                 # Trang chủ Wiki điều hướng
│   ├── risks/                  # Thư mục hồ sơ Rủi ro
│   ├── controls/               # Thư mục hoạt động Kiểm soát
│   └── events/                 # Thư mục Sự kiện rủi ro
├── outputs/                    # Bảng dữ liệu chuẩn hóa và Báo cáo kiểm thử
│   ├── entities.csv            # Thực thể đã chuẩn hóa
│   ├── relations.csv           # Quan hệ đã chuẩn hóa
│   └── wiki_validation_report.md # Báo cáo kiểm thử chất lượng Wiki
├── scripts/                    # Các scripts Python xử lý
│   ├── inspect_data.py         # Kiểm tra cấu trúc & tính toàn vẹn dữ liệu gốc
│   ├── build_entities.py       # Chuẩn hóa dữ liệu nguồn thành Node & Edge
│   ├── build_wiki.py           # Sinh các trang Wiki Markdown tương thích Obsidian
│   ├── validate_wiki.py        # Kiểm thử tính toàn vẹn của Wiki
│   └── load_neo4j.py           # Nạp dữ liệu chuẩn hóa vào Neo4j Graph DB
├── cypher/                     # Các câu lệnh truy vấn đồ thị Neo4j
│   ├── schema.cypher           # Thiết lập unique constraints
│   └── demo_queries.cypher     # Các câu truy vấn đồ thị mẫu
└── .env                        # File cấu hình kết nối Neo4j (người dùng tự tạo)
```

---

## 🚀 Hướng dẫn chạy dự án theo thứ tự

Để xây dựng Wiki Risk Graph từ dữ liệu seed, vui lòng thực hiện tuần tự các lệnh sau từ thư mục gốc của project (`graph_rag_labs/`):

### Bước 1: Kiểm tra cấu trúc dữ liệu nguồn
Kiểm tra số dòng, cột, dữ liệu trống (null) và tính toàn vẹn tham chiếu của các file CSV nguồn:
```bash
python buoi_13/scripts/inspect_data.py
```

### Bước 2: Chuẩn hóa dữ liệu nguồn thành Node và Edge
Đọc các file dữ liệu seed nghiệp vụ và kết xuất ra các file dữ liệu graph chuẩn hóa tại thư mục `outputs/`:
```bash
python buoi_13/scripts/build_entities.py
```

### Bước 3: Sinh các trang Wiki Markdown
Chuyển đổi các thực thể và quan hệ đã chuẩn hóa thành cấu trúc trang Wiki Markdown tương thích Obsidian:
```bash
python buoi_13/scripts/build_wiki.py
```

### Bước 4: Kiểm thử và đánh giá Wiki
Tự động quét các trang Wiki để phát hiện broken link, thực thể trùng lặp, cô lập (orphan) và phân loại lỗi:
```bash
python buoi_13/scripts/validate_wiki.py
```
*Kết quả chi tiết được xuất tại file: `buoi_13/outputs/wiki_validation_report.md`.*

---

## 👁️ Trực quan hóa đồ thị bằng Obsidian
1. Khởi động ứng dụng **Obsidian**.
2. Chọn **Open folder as vault** (Mở thư mục dưới dạng vault).
3. Tìm và chọn thư mục: `buoi_13/wiki/`.
4. Mở trang bắt đầu `Home.md` để xem danh sách điều hướng.
5. Mở **Graph View** của Obsidian để chiêm ngưỡng mạng lưới liên kết rủi ro trực quan dạng đồ thị:
   `KiemSoat -[MITIGATES]-> RuiRo -[OBSERVED_AS]-> SuKienRuiRo`.

---

## 🗄️ Nạp dữ liệu vào Neo4j (Tùy chọn)

Nếu bạn có sẵn Neo4j Database và muốn thực hành viết truy vấn đồ thị Cypher:

### 1. Cài đặt neo4j driver cho Python
```bash
pip install neo4j
```

### 2. Cấu hình kết nối
Tạo file `.env` tại thư mục `buoi_13/.env` (cùng cấp với thư mục `scripts/`) và cấu hình thông tin kết nối Neo4j của bạn:
```properties
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=neo4j
```

### 3. Khởi chạy nạp dữ liệu
Chạy script để tự động tạo constraints, nạp thực thể và liên kết quan hệ bằng parameterized Cypher:
```bash
python buoi_13/scripts/load_neo4j.py
```

### 4. Truy vấn Graph trên Neo4j Browser
* Dùng các câu lệnh trong [`cypher/schema.cypher`](file:///c:/Users/minhn/OneDrive/Desktop/Học%20AI/RAG/graph_rag_labs/buoi_13/cypher/schema.cypher) để khai báo constraints thủ công nếu không chạy script Python.
* Thực hành chạy các câu truy vấn nghiệp vụ mẫu tại [`cypher/demo_queries.cypher`](file:///c:/Users/minhn/OneDrive/Desktop/Học%20AI/RAG/graph_rag_labs/buoi_13/cypher/demo_queries.cypher) (như tìm rủi ro chưa có kiểm soát, tìm đường đi liên kết, hoặc tìm mối quan hệ chưa được xác minh).
