// 1. Tạo unique constraint cho rủi ro (RuiRo)
CREATE CONSTRAINT unique_ruiro_id IF NOT EXISTS
FOR (r:RuiRo) REQUIRE r.id IS UNIQUE;

// 2. Tạo unique constraint cho kiểm soát (KiemSoat)
CREATE CONSTRAINT unique_kiemsoat_id IF NOT EXISTS
FOR (k:KiemSoat) REQUIRE k.id IS UNIQUE;

// 3. Tạo unique constraint cho sự kiện rủi ro (SuKienRuiRo)
CREATE CONSTRAINT unique_sukienruiro_id IF NOT EXISTS
FOR (s:SuKienRuiRo) REQUIRE s.id IS UNIQUE;
