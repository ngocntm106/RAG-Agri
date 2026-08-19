# BÁO CÁO KIỂM TRA PROJECT VÀ DỮ LIỆU (INSPECTION REPORT)

## 1. Môi trường hệ thống
- **Working Root**: C:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\buoi_14
- **Python Interpreter**: `C:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\buoi_14\.venv\Scripts\python.exe`
- **Python Version**: `3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)]`
- **Pandas Version**: `3.0.5`

## 2. Cấu trúc thư mục hiện tại (buoi_14/)
Các file đã quét được:
- `.\buoi14.md`
- `.\requirements.txt`
- `.\outputs\inspection_report.md`
- `.\scripts\inspect_project.py`

## 3. Phân tích Dữ liệu Nguồn (kb+hops/)
### File: `metadata.csv`
- **Đường dẫn**: `..\kb+hops\metadata.csv`
- **Số dòng**: 15
- **Bảng mã (Encoding)**: `utf-8`
- **Các cột**: `id, title, so_ky_hieu, ngay_ban_hanh, loai_van_ban, ngay_co_hieu_luc, ngay_het_hieu_luc, nguon_thu_thap, ngay_dang_cong_bao, nganh, linh_vuc, co_quan_ban_hanh, chuc_danh, nguoi_ky, pham_vi, thong_tin_ap_dung, tinh_trang_hieu_luc`
- **Số dòng trùng lặp**: 0
- **Giá trị Null**:
  - `id`: 0 dòng null
  - `title`: 0 dòng null
  - `so_ky_hieu`: 0 dòng null
  - `ngay_ban_hanh`: 0 dòng null
  - `loai_van_ban`: 0 dòng null
  - `ngay_co_hieu_luc`: 1 dòng null
  - `ngay_het_hieu_luc`: 14 dòng null
  - `nguon_thu_thap`: 5 dòng null
  - `ngay_dang_cong_bao`: 11 dòng null
  - `nganh`: 3 dòng null
  - `linh_vuc`: 2 dòng null
  - `co_quan_ban_hanh`: 0 dòng null
  - `chuc_danh`: 0 dòng null
  - `nguoi_ky`: 0 dòng null
  - `pham_vi`: 0 dòng null
  - `thong_tin_ap_dung`: 15 dòng null
  - `tinh_trang_hieu_luc`: 0 dòng null
- **Khóa đề xuất (Candidate Key)**: `document_id` (mã định danh văn bản)
- **Trường Metadata phù hợp Citation**: `title`, `document_type`, `effective_date`, `status`

- **Mẫu dữ liệu (3 dòng đầu)**:
```json
[
  {
    "id": "112025",
    "title": "Nghị định số 73/2016/NĐ-CP Quy định chi tiết thi hành Luật kinh doanh bảo hiểm và Luật sửa đổi, bổ sung một số điều của Luật kinh doanh bảo hiểm",
    "so_ky_hieu": "73/2016/NĐ-CP",
    "ngay_ban_hanh": "01/07/2016",
    "loai_van_ban": "Nghị định",
    "ngay_co_hieu_luc": "01/07/2016",
    "ngay_het_hieu_luc": NaN,
    "nguon_thu_thap": NaN,
    "ngay_dang_cong_bao": NaN,
    "nganh": "Tài chính",
    "linh_vuc": "Chưa phân loại",
    "co_quan_ban_hanh": "Chính phủ",
    "chuc_danh": "Thủ tướng",
    "nguoi_ky": "Nguyễn Xuân Phúc",
    "pham_vi": "Trung ương",
    "thong_tin_ap_dung": NaN,
    "tinh_trang_hieu_luc": "Hết hiệu lực một phần"
  },
  {
    "id": "163441",
    "title": "Nghị định số 46/2023/NĐ-CP Quy định chi tiết thi hành một số điều của Luật Kinh doanh bảo hiểm",
    "so_ky_hieu": "46/2023/NĐ-CP",
    "ngay_ban_hanh": "01/07/2023",
    "loai_van_ban": "Nghị định",
    "ngay_co_hieu_luc": "01/07/2023",
    "ngay_het_hieu_luc": NaN,
    "nguon_thu_thap": NaN,
    "ngay_dang_cong_bao": "13/03/2026",
    "nganh": "Tài chính",
    "linh_vuc": "Bảo hiểm",
    "co_quan_ban_hanh": "Chính phủ",
    "chuc_danh": "Phó Thủ tướng Chính phủ",
    "nguoi_ky": "Lê Minh Khái",
    "pham_vi": "Trung ương",
    "thong_tin_ap_dung": NaN,
    "tinh_trang_hieu_luc": "Hết hiệu lực một phần"
  },
  {
    "id": "168220",
    "title": "Thông tư số 27/2024/TT-NHNN Quy định về việc ngân hàng hợp tác xã, việc trích nộp, quản lý và sử dụng Quỹ bảo đảm an toàn hệ thống quỹ tín dụng nhân dân",
    "so_ky_hieu": "27/2024/TT-NHNN",
    "ngay_ban_hanh": "28/06/2024",
    "loai_van_ban": "Thông tư",
    "ngay_co_hieu_luc": "01/07/2024",
    "ngay_het_hieu_luc": NaN,
    "nguon_thu_thap": "bản gốc",
    "ngay_dang_cong_bao": "03/07/2026",
    "nganh": "Ngân hàng",
    "linh_vuc": "Thanh tra, giám sát ngân hàng",
    "co_quan_ban_hanh": "Ngân hàng Nhà nước Việt Nam",
    "chuc_danh": "Phó Thống đốc",
    "nguoi_ky": "Đào Minh Tú",
    "pham_vi": "Trung ương",
    "thong_tin_ap_dung": NaN,
    "tinh_trang_hieu_luc": "Hết hiệu lực một phần"
  }
]
```

### File: `content.csv`
- **Đường dẫn**: `..\kb+hops\content.csv`
- **Số dòng**: 15
- **Bảng mã (Encoding)**: `utf-8`
- **Các cột**: `id, content_html`
- **Số dòng trùng lặp**: 0
- **Giá trị Null**:
  - `id`: 0 dòng null
  - `content_html`: 0 dòng null
- **Khóa đề xuất (Candidate Key)**: `chunk_id` (định danh duy nhất cho từng chunk)
- **Trường Text phù hợp Retrieval**: `text` (nội dung chi tiết của điều khoản)
- **Trường Metadata phù hợp Citation**: `document_id`, `chapter`, `section`, `article`, `clause`

- **Mẫu dữ liệu (3 dòng đầu)**:
```json
[
  {
    "id": "44209",
    "content_html": "<html>\n <head></head>\n <body>\n  <table border=\"0\" style=\"width: 100%; border-collapse: collapse; table-layout: fixed; margin-top: 20px; border: none;\">\n   <tbody>\n    <tr>\n     <td style=\"vertical-align: top; text-align: center; border: none; padding: 5px; font-family: 'Times New Roman', serif;\">\n  ..."
  },
  {
    "id": "177271",
    "content_html": "<html>\n <head></head>\n <body>\n  <div style=\"width: 100%; font-family: 'Times New Roman', serif; font-size: 14px; color: #000;\">\n   <div style=\"width: 100%; display: table; table-layout: fixed;\">\n    <div style=\"display: table-cell; width: 50%; text-align: center; vertical-align: top; font-weight: bo..."
  },
  {
    "id": "112025",
    "content_html": "<html>\n <head></head>\n <body>\n  <div>\n   <div style=\"width: 100%; font-family: 'Times New Roman', serif; font-size: 14px; color: #000;\">\n    <div style=\"width: 100%; display: table; table-layout: fixed;\">\n     <div style=\"display: table-cell; width: 50%; text-align: center; vertical-align: top; font..."
  }
]
```

### File: `relationships.csv`
- **Đường dẫn**: `..\kb+hops\relationships.csv`
- **Số dòng**: 8
- **Bảng mã (Encoding)**: `utf-8`
- **Các cột**: `doc_id, other_doc_id, relationship, relationship_type`
- **Số dòng trùng lặp**: 0
- **Giá trị Null**:
  - `doc_id`: 0 dòng null
  - `other_doc_id`: 0 dòng null
  - `relationship`: 0 dòng null
  - `relationship_type`: 0 dòng null
- **Khóa liên kết**: `source_id`, `target_id`
- **Loại quan hệ (Relationship Types)**: Xem mẫu dữ liệu để trích xuất thêm.

- **Mẫu dữ liệu (3 dòng đầu)**:
```json
[
  {
    "doc_id": "169221",
    "other_doc_id": 44209,
    "relationship": "Sửa đổi, bổ sung",
    "relationship_type": "SUA_DOI_BO_SUNG"
  },
  {
    "doc_id": "112924",
    "other_doc_id": 95652,
    "relationship": "Căn cứ",
    "relationship_type": "CAN_CU"
  },
  {
    "doc_id": "174218",
    "other_doc_id": 25692,
    "relationship": "Căn cứ",
    "relationship_type": "CAN_CU"
  }
]
```

## 4. Kiểm tra rủi ro mã nguồn cũ (Kiểm tra lệnh phá hủy/ghi đè dữ liệu)
Không phát hiện lệnh nguy hại nào (`os.remove`, `shutil.rmtree`, `DELETE`, `DROP`...) trong code hiện có.
