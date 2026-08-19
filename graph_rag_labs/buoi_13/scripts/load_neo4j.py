import os
import csv
import sys

def parse_env_file(env_path):
    env_vars = {}
    if not os.path.exists(env_path):
        return env_vars
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                # Strip spaces and optional quotes
                key = key.strip()
                val = val.strip().strip("'").strip('"')
                env_vars[key] = val
    return env_vars

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    entities_csv = os.path.join(output_dir, "entities.csv")
    relations_csv = os.path.join(output_dir, "relations.csv")
    env_path = os.path.join(base_dir, ".env")
    
    # 1. Check if neo4j driver is installed
    try:
        from neo4j import GraphDatabase
        from neo4j.exceptions import ServiceUnavailable, AuthError
    except ImportError:
        print("\n" + "!" * 60)
        print("CẢNH BÁO: Thư viện 'neo4j' driver của Python chưa được cài đặt.")
        print("Để chạy script này, vui lòng cài đặt bằng lệnh:")
        print("  pip install neo4j")
        print("!" * 60 + "\n")
        print("Đã bỏ qua bước nạp dữ liệu vào Neo4j (không làm ảnh hưởng đến các file Wiki Markdown).")
        return

    # 2. Read environment variables from .env
    env = parse_env_file(env_path)
    
    uri = env.get("NEO4J_URI", "bolt://localhost:7687")
    user = env.get("NEO4J_USER", "neo4j")
    password = env.get("NEO4J_PASSWORD")
    database = env.get("NEO4J_DATABASE", "neo4j")
    
    if not password:
        print("\n" + "!" * 60)
        print("LỖI: Chưa cấu hình NEO4J_PASSWORD trong file .env")
        print(f"Vui lòng tạo file .env tại {env_path} với nội dung:")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=your_password")
        print("  NEO4J_DATABASE=neo4j")
        print("!" * 60 + "\n")
        return

    # 3. Check standardized csv files
    if not os.path.exists(entities_csv) or not os.path.exists(relations_csv):
        print(f"[ERROR] Required normalized csv files not found in outputs/.")
        print("Vui lòng chạy script build_entities.py trước.")
        return

    print("=" * 60)
    print("BẮT ĐẦU NẠP DỮ LIỆU VÀO NEO4J")
    print(f"Kết nối tới: {uri} (Database: {database})")
    print("=" * 60)

    # 4. Connect to Neo4j database
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        # Test connection
        driver.verify_connectivity()
    except (ServiceUnavailable, Exception) as e:
        print("\n" + "x" * 60)
        print("KHÔNG THỂ KẾT NỐI TỚI NEO4J DATABASE.")
        print("Chi tiết lỗi:", str(e))
        print("\nHƯỚNG DẪN KHẮC PHỤC:")
        print("1. Hãy chắc chắn rằng Neo4j của bạn đang chạy.")
        print("   Nếu dùng Docker, bạn có thể khởi động nhanh bằng lệnh:")
        print("   docker run --name neo4j-risk-graph -p 7474:7474 -p 7687:7687 -d -e NEO4J_AUTH=neo4j/your_password neo4j:latest")
        print("2. Đảm bảo cấu hình trong file .env chính xác.")
        print("x" * 60 + "\n")
        return

    # 5. Read data from CSV
    entities = []
    with open(entities_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row and row.get("id"):
                entities.append(row)
                
    relations = []
    with open(relations_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row and row.get("source_id"):
                relations.append(row)

    # 6. Load data using parameterized Cypher in a session
    try:
        with driver.session(database=database) as session:
            # Create Constraints (from schema.cypher equivalent)
            print("Đang cấu hình constraints...")
            session.run("CREATE CONSTRAINT unique_ruiro_id IF NOT EXISTS FOR (r:RuiRo) REQUIRE r.id IS UNIQUE")
            session.run("CREATE CONSTRAINT unique_kiemsoat_id IF NOT EXISTS FOR (k:KiemSoat) REQUIRE k.id IS UNIQUE")
            session.run("CREATE CONSTRAINT unique_sukienruiro_id IF NOT EXISTS FOR (s:SuKienRuiRo) REQUIRE s.id IS UNIQUE")
            
            # Load Nodes
            print(f"Đang nạp {len(entities)} nodes thực thể...")
            cnt_nodes = 0
            for ent in entities:
                ent_type = ent["type"]
                params = {
                    "id": ent["id"],
                    "name": ent["name"],
                    "description": ent["description"],
                    "data_origin": ent["data_origin"],
                    "verification_status": ent["verification_status"]
                }
                
                if ent_type == "RuiRo":
                    params.update({
                        "category": ent["category"],
                        "cause": ent["cause"],
                        "event": ent["event"],
                        "impact": ent["impact"],
                        "inherent_level": ent["inherent_level"],
                        "residual_level": ent["residual_level"],
                        "owner_unit_id": ent["owner_unit_id"]
                    })
                    query = """
                    MERGE (r:RuiRo {id: $id})
                    SET r.name = $name,
                        r.description = $description,
                        r.category = $category,
                        r.cause = $cause,
                        r.event = $event,
                        r.impact = $impact,
                        r.inherent_level = $inherent_level,
                        r.residual_level = $residual_level,
                        r.owner_unit_id = $owner_unit_id,
                        r.data_origin = $data_origin,
                        r.verification_status = $verification_status
                    """
                    
                elif ent_type == "KiemSoat":
                    params.update({
                        "control_type": ent["control_type"],
                        "frequency": ent["frequency"],
                        "owner_role_id": ent["owner_role_id"],
                        "effectiveness": ent["effectiveness"]
                    })
                    query = """
                    MERGE (k:KiemSoat {id: $id})
                    SET k.name = $name,
                        k.control_type = $control_type,
                        k.frequency = $frequency,
                        k.owner_role_id = $owner_role_id,
                        k.effectiveness = $effectiveness,
                        k.data_origin = $data_origin,
                        k.verification_status = $verification_status
                    """
                    
                elif ent_type == "SuKienRuiRo":
                    params.update({
                        "occurred_at": ent["occurred_at"],
                        "discovered_at": ent["discovered_at"],
                        "severity": ent["severity"],
                        "loss_amount_vnd": ent["loss_amount_vnd"]
                    })
                    query = """
                    MERGE (s:SuKienRuiRo {id: $id})
                    SET s.name = $name,
                        s.description = $description,
                        s.occurred_at = $occurred_at,
                        s.discovered_at = $discovered_at,
                        s.severity = $severity,
                        s.loss_amount_vnd = toInteger($loss_amount_vnd),
                        s.data_origin = $data_origin,
                        s.verification_status = $verification_status
                    """
                else:
                    continue
                
                session.run(query, params)
                cnt_nodes += 1
            
            # Load Edges
            print(f"Đang nạp {len(relations)} quan hệ edges...")
            cnt_edges = 0
            for rel in relations:
                rel_type = rel["relationship_type"]
                params = {
                    "source_id": rel["source_id"],
                    "target_id": rel["target_id"],
                    "source": rel["source"],
                    "evidence_quote": rel["evidence_quote"],
                    "confidence": float(rel["confidence"]) if rel["confidence"] else 1.0,
                    "verification_status": rel["verification_status"],
                    "data_origin": rel["data_origin"]
                }
                
                if rel_type == "MITIGATES":
                    query = """
                    MATCH (k:KiemSoat {id: $source_id})
                    MATCH (r:RuiRo {id: $target_id})
                    MERGE (k)-[rel:MITIGATES]->(r)
                    SET rel.source = $source,
                        rel.evidence_quote = $evidence_quote,
                        rel.confidence = $confidence,
                        rel.verification_status = $verification_status,
                        rel.data_origin = $data_origin
                    """
                elif rel_type == "OBSERVED_AS":
                    query = """
                    MATCH (r:RuiRo {id: $source_id})
                    MATCH (s:SuKienRuiRo {id: $target_id})
                    MERGE (r)-[rel:OBSERVED_AS]->(s)
                    SET rel.source = $source,
                        rel.evidence_quote = $evidence_quote,
                        rel.confidence = $confidence,
                        rel.verification_status = $verification_status,
                        rel.data_origin = $data_origin
                    """
                else:
                    continue
                
                session.run(query, params)
                cnt_edges += 1

        print("\n" + "=" * 60)
        print("NẠP DỮ LIỆU THÀNH CÔNG!")
        print(f"- Đã nạp/cập nhật: {cnt_nodes} Nodes")
        print(f"- Đã nạp/cập nhật: {cnt_edges} Edges")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] Quá trình nạp dữ liệu thất bại: {str(e)}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
