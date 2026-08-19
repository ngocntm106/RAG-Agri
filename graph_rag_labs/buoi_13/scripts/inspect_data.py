import os
import csv

def inspect_csv(file_path, primary_key=None):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return None

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return {
                "num_rows": 0,
                "columns": [],
                "null_counts": {},
                "duplicates": 0,
                "ids": set()
            }
        
        columns = header
        null_counts = {col: 0 for col in columns}
        ids = []
        rows = []
        
        for row in reader:
            if not row: # Skip empty lines
                continue
            rows.append(row)
            
            # Pad row with empty strings if it has fewer elements than columns
            padded_row = row + [''] * (len(columns) - len(row))
            
            for col_idx, value in enumerate(padded_row[:len(columns)]):
                val_str = value.strip()
                if val_str == "" or val_str.lower() in ["null", "none"]:
                    null_counts[columns[col_idx]] += 1
            
            if primary_key in columns:
                pk_idx = columns.index(primary_key)
                if pk_idx < len(row):
                    ids.append(row[pk_idx].strip())

        # Check duplicates
        pk_duplicates = len(ids) - len(set(ids)) if primary_key else 0

        return {
            "num_rows": len(rows),
            "columns": columns,
            "null_counts": null_counts,
            "duplicates": pk_duplicates,
            "ids": set(ids),
            "rows": rows,
            "header": columns
        }

def main():
    # Base path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    files = {
        "risk_profiles": ("risk_profiles_seed.csv", "id"),
        "controls": ("controls_seed.csv", "id"),
        "risk_events": ("risk_events_seed.csv", "id"),
        "relationships": ("relationships_seed.csv", None)
    }
    
    results = {}
    print("=" * 60)
    print("INSPECTING DATA SEED FILES")
    print("=" * 60)
    
    for key, (filename, pk) in files.items():
        file_path = os.path.join(data_dir, filename)
        print(f"\nAnalyzing {filename}...")
        res = inspect_csv(file_path, pk)
        if res:
            results[key] = res
            print(f"  - Number of rows: {res['num_rows']}")
            print(f"  - Columns: {', '.join(res['columns'])}")
            print(f"  - Primary Key: {pk if pk else 'None'}")
            print(f"  - Duplicates (on PK): {res['duplicates']}")
            print("  - Null values per column:")
            for col, val in res['null_counts'].items():
                print(f"    * {col}: {val}")
        else:
            print(f"  - Failed to read {filename}")
            
    # Reference Integrity Check
    print("\n" + "=" * 60)
    print("REFERENTIAL INTEGRITY CHECK")
    print("=" * 60)
    
    if "risk_profiles" in results and "risk_events" in results:
        # Check risk_events -> risk_profiles
        events_data = results["risk_events"]
        profile_ids = results["risk_profiles"]["ids"]
        risk_id_idx = events_data["columns"].index("risk_id")
        
        missing_risks = []
        for r in events_data["rows"]:
            event_id = r[0]
            risk_id = r[risk_id_idx].strip()
            if risk_id not in profile_ids:
                missing_risks.append((event_id, risk_id))
                
        print(f"\nChecking risk_events.risk_id -> risk_profiles.id:")
        if missing_risks:
            print(f"  [WARNING] Found {len(missing_risks)} missing references:")
            for ev_id, r_id in missing_risks:
                print(f"    * Event {ev_id} references non-existent Risk {r_id}")
        else:
            print("  [OK] All risk_events.risk_id references are valid.")

    if "relationships" in results:
        relations_data = results["relationships"]
        columns = relations_data["columns"]
        src_idx = columns.index("source_id")
        tgt_idx = columns.index("target_id")
        type_idx = columns.index("relationship_type")
        
        # Collect all valid entity IDs
        all_entity_ids = set()
        if "risk_profiles" in results:
            all_entity_ids.update(results["risk_profiles"]["ids"])
        if "controls" in results:
            all_entity_ids.update(results["controls"]["ids"])
        if "risk_events" in results:
            all_entity_ids.update(results["risk_events"]["ids"])
            
        print(f"\nChecking relationship_types distribution:")
        rel_types = {}
        for r in relations_data["rows"]:
            rel_type = r[type_idx].strip()
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        for rel_type, count in rel_types.items():
            print(f"  - {rel_type}: {count} relations")
            
        # Check source and target existence
        missing_sources = []
        missing_targets = []
        for r in relations_data["rows"]:
            src_id = r[src_idx].strip()
            tgt_id = r[tgt_idx].strip()
            rel_type = r[type_idx].strip()
            
            if src_id not in all_entity_ids:
                missing_sources.append((src_id, rel_type, tgt_id))
            if tgt_id not in all_entity_ids:
                missing_targets.append((src_id, rel_type, tgt_id))
                
        print(f"\nChecking relationship references (source_id and target_id existence):")
        if missing_sources:
            print(f"  [WARNING] Found {len(missing_sources)} missing source references:")
            for s, t, o in missing_sources:
                print(f"    * Source ID {s} in relationship ({s})-[:{t}]->({o}) does not exist in any entity file.")
        else:
            print("  [OK] All source_id references exist.")
            
        if missing_targets:
            print(f"  [WARNING] Found {len(missing_targets)} missing target references:")
            for s, t, o in missing_targets:
                print(f"    * Target ID {o} in relationship ({s})-[:{t}]->({o}) does not exist in any entity file.")
        else:
            print("  [OK] All target_id references exist.")

    # Master Data gaps
    print("\n" + "=" * 60)
    print("MASTER DATA GAPS IDENTIFIED")
    print("=" * 60)
    
    if "risk_profiles" in results:
        profiles_data = results["risk_profiles"]
        unit_idx = profiles_data["columns"].index("owner_unit_id")
        units = set(r[unit_idx].strip() for r in profiles_data["rows"] if r[unit_idx].strip())
        print(f"\nRisk profiles reference the following owner_unit_ids (but no master data unit file exists):")
        print(f"  - Unit IDs: {', '.join(sorted(units))}")
        
    if "controls" in results:
        controls_data = results["controls"]
        role_idx = controls_data["columns"].index("owner_role_id")
        roles = set(r[role_idx].strip() for r in controls_data["rows"] if r[role_idx].strip())
        print(f"\nControls reference the following owner_role_ids (but no master data role file exists):")
        print(f"  - Role IDs: {', '.join(sorted(roles))}")

if __name__ == "__main__":
    main()
