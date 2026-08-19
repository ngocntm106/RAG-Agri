import os
import csv
import sys

def main():
    # Reconfigure stdout to use UTF-8, preventing encoding errors on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for Python versions that don't support reconfigure
        pass

    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "outputs")
    
    # Ensure outputs directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Files paths
    risk_profiles_path = os.path.join(data_dir, "risk_profiles_seed.csv")
    controls_path = os.path.join(data_dir, "controls_seed.csv")
    risk_events_path = os.path.join(data_dir, "risk_events_seed.csv")
    relationships_path = os.path.join(data_dir, "relationships_seed.csv")
    
    entities_out_path = os.path.join(output_dir, "entities.csv")
    relations_out_path = os.path.join(output_dir, "relations.csv")
    
    # Master schema for entities.csv
    entity_columns = [
        "id", "type", "name", "description", "source_file", "data_origin", "verification_status",
        # RuiRo specific fields
        "category", "cause", "event", "impact", "inherent_level", "residual_level", "owner_unit_id",
        # KiemSoat specific fields
        "control_type", "frequency", "owner_role_id", "effectiveness",
        # SuKienRuiRo specific fields
        "risk_id", "occurred_at", "discovered_at", "severity", "loss_amount_vnd"
    ]
    
    entities = []
    entity_ids = set()
    
    # Helper to check for duplicates in ID
    def add_entity(entity_dict):
        ent_id = entity_dict["id"]
        if ent_id in entity_ids:
            print(f"[WARNING] Duplicate entity ID detected: {ent_id}")
        entity_ids.add(ent_id)
        entities.append(entity_dict)

    # 1. Process risk_profiles_seed.csv (type: RuiRo)
    if os.path.exists(risk_profiles_path):
        with open(risk_profiles_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("id"):
                    continue
                ent = {col: "" for col in entity_columns}
                # Core fields
                ent["id"] = row.get("id", "").strip()
                ent["type"] = "RuiRo"
                ent["name"] = row.get("name", "").strip()
                ent["description"] = row.get("description", "").strip()
                ent["source_file"] = "risk_profiles_seed.csv"
                ent["data_origin"] = row.get("data_origin", "").strip()
                ent["verification_status"] = row.get("verification_status", "").strip()
                
                # Business fields
                ent["category"] = row.get("category", "").strip()
                ent["cause"] = row.get("cause", "").strip()
                ent["event"] = row.get("event", "").strip()
                ent["impact"] = row.get("impact", "").strip()
                ent["inherent_level"] = row.get("inherent_level", "").strip()
                ent["residual_level"] = row.get("residual_level", "").strip()
                ent["owner_unit_id"] = row.get("owner_unit_id", "").strip()
                
                add_entity(ent)
    else:
        print(f"[ERROR] Source file not found: {risk_profiles_path}")

    # 2. Process controls_seed.csv (type: KiemSoat)
    if os.path.exists(controls_path):
        with open(controls_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("id"):
                    continue
                ent = {col: "" for col in entity_columns}
                # Core fields
                ent["id"] = row.get("id", "").strip()
                ent["type"] = "KiemSoat"
                ent["name"] = row.get("name", "").strip()
                # controls_seed.csv doesn't have a description field in CSV header, we'll map empty description
                ent["description"] = ""
                ent["source_file"] = "controls_seed.csv"
                ent["data_origin"] = row.get("data_origin", "").strip()
                ent["verification_status"] = row.get("verification_status", "").strip()
                
                # Business fields
                ent["control_type"] = row.get("control_type", "").strip()
                ent["frequency"] = row.get("frequency", "").strip()
                ent["owner_role_id"] = row.get("owner_role_id", "").strip()
                ent["effectiveness"] = row.get("effectiveness", "").strip()
                
                add_entity(ent)
    else:
        print(f"[ERROR] Source file not found: {controls_path}")

    # 3. Process risk_events_seed.csv (type: SuKienRuiRo)
    if os.path.exists(risk_events_path):
        with open(risk_events_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("id"):
                    continue
                ent = {col: "" for col in entity_columns}
                # Core fields
                ent["id"] = row.get("id", "").strip()
                ent["type"] = "SuKienRuiRo"
                ent["name"] = row.get("description", "").strip() # Use description as name since event name is descriptive
                ent["description"] = row.get("description", "").strip()
                ent["source_file"] = "risk_events_seed.csv"
                ent["data_origin"] = row.get("data_origin", "").strip()
                ent["verification_status"] = row.get("verification_status", "").strip()
                
                # Business fields
                ent["risk_id"] = row.get("risk_id", "").strip()
                ent["occurred_at"] = row.get("occurred_at", "").strip()
                ent["discovered_at"] = row.get("discovered_at", "").strip()
                ent["severity"] = row.get("severity", "").strip()
                ent["loss_amount_vnd"] = row.get("loss_amount_vnd", "").strip()
                
                add_entity(ent)
    else:
        print(f"[ERROR] Source file not found: {risk_events_path}")

    # Write entities.csv
    with open(entities_out_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=entity_columns)
        writer.writeheader()
        writer.writerows(entities)
        
    print(f"Successfully wrote {len(entities)} entities to {entities_out_path}")

    # 4. Process relationships_seed.csv -> relations.csv
    relation_columns = [
        "source_id", "relationship_type", "target_id", "source", 
        "evidence_quote", "confidence", "verification_status", "data_origin"
    ]
    relations = []
    orphan_references = []
    
    if os.path.exists(relationships_path):
        with open(relationships_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("source_id"):
                    continue
                
                src_id = row.get("source_id", "").strip()
                tgt_id = row.get("target_id", "").strip()
                rel_type = row.get("relationship_type", "").strip()
                
                # Check for referential integrity
                src_exists = src_id in entity_ids
                tgt_exists = tgt_id in entity_ids
                
                if not src_exists or not tgt_exists:
                    orphan_references.append({
                        "source_id": src_id,
                        "relationship_type": rel_type,
                        "target_id": tgt_id,
                        "source_exists": src_exists,
                        "target_exists": tgt_exists
                    })
                
                rel = {col: row.get(col, "").strip() for col in relation_columns}
                relations.append(rel)
    else:
        print(f"[ERROR] Source file not found: {relationships_path}")
        
    # Write relations.csv
    with open(relations_out_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=relation_columns)
        writer.writeheader()
        writer.writerows(relations)
        
    print(f"Successfully wrote {len(relations)} relations to {relations_out_path}")

    # Print statistics
    print("\n" + "=" * 50)
    print("STANDARDIZED DATA STATISTICS")
    print("=" * 50)
    
    # 1. Entity type statistics
    type_counts = {}
    for ent in entities:
        t = ent["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print("Entities by Type:")
    for t, count in type_counts.items():
        print(f"  - {t}: {count} entities")
        
    # 2. Relation type statistics
    rel_counts = {}
    for rel in relations:
        t = rel["relationship_type"]
        rel_counts[t] = rel_counts.get(t, 0) + 1
        
    print("\nRelations by Type:")
    for t, count in rel_counts.items():
        print(f"  - {t}: {count} relations")
        
    # 3. Orphan reference report
    print("\nOrphan References Integrity Check:")
    if orphan_references:
        print(f"  [FAIL] Found {len(orphan_references)} orphan reference(s):")
        for orphan in orphan_references:
            src_lbl = "OK" if orphan["source_exists"] else "MISSING"
            tgt_lbl = "OK" if orphan["target_exists"] else "MISSING"
            print(f"    * ({orphan['source_id']} [source: {src_lbl}]) -[:{orphan['relationship_type']}]-> ({orphan['target_id']} [target: {tgt_lbl}])")
    else:
        print("  [PASS] No orphan references found in relations.csv.")
    print("=" * 50)

if __name__ == "__main__":
    main()
