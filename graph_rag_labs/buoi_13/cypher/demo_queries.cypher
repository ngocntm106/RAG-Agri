// =====================================================================
// DEMO QUERIES CHO WIKI RISK GRAPH
// =====================================================================

// A. Xem toàn bộ graph (Nodes & Edges)
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 200;

// B. Tìm kiểm soát giảm thiểu của một Rủi ro cụ thể (ví dụ: 'RR-001')
MATCH (k:KiemSoat)-[r:MITIGATES]->(rr:RuiRo {id: 'RR-001'})
RETURN k.id AS ControlID, k.name AS ControlName, r.verification_status AS RelStatus, rr.id AS RiskID, rr.name AS RiskName;

// C. Tìm tất cả Sự kiện của một Rủi ro cụ thể (ví dụ: 'RR-001')
MATCH (rr:RuiRo {id: 'RR-001'})-[r:OBSERVED_AS]->(sk:SuKienRuiRo)
RETURN rr.id AS RiskID, rr.name AS RiskName, r.evidence_quote AS Evidence, sk.id AS EventID, sk.description AS EventDesc;

// D. Tìm tất cả các đường đi: KiemSoat -> RuiRo -> SuKienRuiRo
MATCH path = (k:KiemSoat)-[:MITIGATES]->(rr:RuiRo)-[:OBSERVED_AS]->(sk:SuKienRuiRo)
RETURN path
LIMIT 50;

// E. Tìm các Rủi ro KHÔNG có bất kỳ Kiểm soát nào (Control Gaps)
MATCH (rr:RuiRo)
WHERE NOT (:KiemSoat)-[:MITIGATES]->(rr)
RETURN rr.id AS RiskID, rr.name AS RiskName, rr.category AS Category;

// F. Tìm các mối quan hệ (Edge) CHƯA được VERIFIED (Trạng thái khác 'VERIFIED')
MATCH (n)-[r]->(m)
WHERE r.verification_status <> 'VERIFIED'
RETURN labels(n)[0] AS SourceType, n.id AS SourceID, type(r) AS RelType, r.verification_status AS Status, labels(m)[0] AS TargetType, m.id AS TargetID;
