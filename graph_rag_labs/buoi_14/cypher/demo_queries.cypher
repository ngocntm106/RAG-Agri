// ==========================================
// BUỔI 14 — DEMO CYPHER QUERIES
// ==========================================

// Query A — Xem tổng quan đồ thị Buổi 14
MATCH (n {lab_session: "buoi_14"})-[r {lab_session: "buoi_14"}]->(m {lab_session: "buoi_14"})
RETURN n, r, m
LIMIT 100;

// Query B — Từ văn bản tới các điều khoản trực thuộc (CONTAINS)
MATCH (v:VanBan {lab_session: "buoi_14"})-[r:CONTAINS]->(d:DieuKhoan {lab_session: "buoi_14"})
RETURN v.source_file AS VanBan, v.title AS TieuDe, count(d) AS SoDieuKhoan
ORDER BY SoDieuKhoan DESC;

// Query C — Xem chuỗi điều khoản kế tiếp (NEXT)
MATCH path = (d1:DieuKhoan {lab_session: "buoi_14"})-[:NEXT*1..3]->(d2:DieuKhoan {lab_session: "buoi_14"})
WHERE d1.article CONTAINS "Điều 1" AND d1.document_id = "44209"
RETURN path
LIMIT 10;

// Query D — Quan hệ liên văn bản có trong dữ liệu thực tế
MATCH (v1:VanBan {lab_session: "buoi_14"})-[r:SUA_DOI_BO_SUNG|CAN_CU|VAN_BAN_BO_SUNG|THAY_THE|HOP_NHAT]->(v2:VanBan {lab_session: "buoi_14"})
RETURN v1.source_file AS SourceDoc, type(r) AS RelationshipType, r.relationship AS MoTa, v2.source_file AS TargetDoc;

// Query E — Kiểm tra node không có liên kết (Orphan Nodes)
MATCH (n {lab_session: "buoi_14"})
WHERE NOT (n)--()
RETURN labels(n) AS Label, n.id AS ID, n.title AS Title;

// Query F — Truy vấn ngữ cảnh đồ thị cho một Chunk được retrieve (Graph Hint)
MATCH (d:DieuKhoan {id: "9fde56b2-2d53-11f1-9cc6-2d0729d94efc", lab_session: "buoi_14"})
OPTIONAL MATCH (v:VanBan)-[:CONTAINS]->(d)
OPTIONAL MATCH (d)-[:NEXT]->(next_d:DieuKhoan)
OPTIONAL MATCH (prev_d:DieuKhoan)-[:NEXT]->(d)
OPTIONAL MATCH (v)-[rel:SUA_DOI_BO_SUNG|CAN_CU|THAY_THE]->(other_v:VanBan)
RETURN v.source_file AS VanBan, d.article AS Article, prev_d.chunk_id AS PrevChunk, next_d.chunk_id AS NextChunk, collect(type(rel)) AS Relations;
