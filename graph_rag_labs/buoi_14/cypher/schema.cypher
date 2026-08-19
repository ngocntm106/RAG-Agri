// ==========================================
// BUỔI 14 — MINI KNOWLEDGE GRAPH SCHEMA
// ==========================================

// 1. Constraints tính duy nhất theo ID
CREATE CONSTRAINT vanban_id_unique IF NOT EXISTS
FOR (v:VanBan) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT dieukhoan_id_unique IF NOT EXISTS
FOR (d:DieuKhoan) REQUIRE d.id IS UNIQUE;

// 2. Indexes phục vụ truy vấn và lọc dữ liệu an toàn theo lab_session
CREATE INDEX vanban_lab_session IF NOT EXISTS
FOR (v:VanBan) ON (v.lab_session);

CREATE INDEX dieukhoan_lab_session IF NOT EXISTS
FOR (d:DieuKhoan) ON (d.lab_session);

CREATE INDEX dieukhoan_doc_id IF NOT EXISTS
FOR (d:DieuKhoan) ON (d.document_id);
