import os
import csv
import sys
import shutil

def sanitize_filename(name):
    # Replace characters that are forbidden in Windows/Linux filenames
    for c in r'\/:*?"<>|':
        name = name.replace(c, '')
    return name.strip()

def main():
    # Setup encoding for Windows console
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    wiki_dir = os.path.join(base_dir, "wiki")
    
    entities_csv = os.path.join(output_dir, "entities.csv")
    relations_csv = os.path.join(output_dir, "relations.csv")
    
    if not os.path.exists(entities_csv) or not os.path.exists(relations_csv):
        print("[ERROR] Normalized data files not found in outputs/. Please run build_entities.py first.")
        sys.exit(1)
        
    risks_dir = os.path.join(wiki_dir, "risks")
    controls_dir = os.path.join(wiki_dir, "controls")
    events_dir = os.path.join(wiki_dir, "events")
    
    os.makedirs(risks_dir, exist_ok=True)
    os.makedirs(controls_dir, exist_ok=True)
    os.makedirs(events_dir, exist_ok=True)

    # Clean up existing markdown files in these directories if possible
    # We do this file-by-file and ignore locked files to prevent PermissionError on Windows
    for folder in [risks_dir, controls_dir, events_dir]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                pass # Ignore files locked by other processes like Obsidian
    
    # 1. Read entities
    entities = {}
    with open(entities_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("id"):
                continue
            ent_id = row["id"].strip()
            ent_name = row["name"].strip()
            row["sanitized_name"] = sanitize_filename(ent_name)
            entities[ent_id] = row
            
    # 2. Read relations
    relations = []
    with open(relations_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("source_id"):
                continue
            relations.append({
                "source_id": row["source_id"].strip(),
                "relationship_type": row["relationship_type"].strip(),
                "target_id": row["target_id"].strip(),
                "source": row.get("source", "").strip(),
                "evidence_quote": row.get("evidence_quote", "").strip(),
                "confidence": row.get("confidence", "").strip(),
                "verification_status": row.get("verification_status", "").strip(),
                "data_origin": row.get("data_origin", "").strip()
            })

    total_wikipages = 0
    total_wikilinks = 0

    # Index relations for quick lookup
    # key: target_id, value: list of relations
    relations_by_target = {}
    # key: source_id, value: list of relations
    relations_by_source = {}
    for rel in relations:
        s_id = rel["source_id"]
        t_id = rel["target_id"]
        
        relations_by_target.setdefault(t_id, []).append(rel)
        relations_by_source.setdefault(s_id, []).append(rel)

    # 3. Create Risks Wiki Pages (RuiRo)
    for ent_id, ent in entities.items():
        if ent["type"] != "RuiRo":
            continue
            
        file_name = f"{ent['sanitized_name']}.md"
        file_path = os.path.join(risks_dir, file_name)
        
        # Gather relationships
        mitigated_by = relations_by_target.get(ent_id, [])
        observed_events = relations_by_source.get(ent_id, [])
        
        content = []
        content.append("---")
        content.append(f"id: {ent['id']}")
        content.append(f"type: RuiRo")
        content.append(f"verification_status: {ent['verification_status']}")
        content.append(f"data_origin: {ent['data_origin']}")
        content.append("---")
        content.append("")
        content.append(f"# {ent['name']}")
        content.append("")
        content.append(f"**Mô tả**: {ent['description']}")
        content.append(f"* **Phân loại**: {ent['category']}")
        content.append(f"* **Mức độ rủi ro tiềm tàng (Inherent)**: {ent['inherent_level']}")
        content.append(f"* **Mức độ rủi ro còn lại (Residual)**: {ent['residual_level']}")
        content.append(f"* **Đơn vị sở hữu**: `{ent['owner_unit_id']}`")
        content.append("")
        content.append("## Phân tích nguyên nhân & Hậu quả")
        content.append(f"* **Nguyên nhân (Cause)**: {ent['cause']}")
        content.append(f"* **Sự kiện (Event)**: {ent['event']}")
        content.append(f"* **Hậu quả (Impact)**: {ent['impact']}")
        content.append("")
        
        content.append("## Kiểm soát giảm thiểu (Mitigating Controls)")
        if mitigated_by:
            for rel in mitigated_by:
                ctrl_id = rel["source_id"]
                if ctrl_id in entities:
                    ctrl = entities[ctrl_id]
                    content.append(f"* [[{ctrl['sanitized_name']}]]")
                    content.append(f"  * *Loại quan hệ*: `{rel['relationship_type']}`")
                    content.append(f"  * *Bằng chứng*: \"{rel['evidence_quote']}\"")
                    content.append(f"  * *Trạng thái xác minh*: `{rel['verification_status']}`")
                    total_wikilinks += 1
                else:
                    content.append(f"* ID kiểm soát không tồn tại: `{ctrl_id}`")
        else:
            content.append("*Chưa cấu hình kiểm soát giảm thiểu cho rủi ro này.*")
        content.append("")
            
        content.append("## Sự kiện rủi ro đã ghi nhận (Observed Events)")
        if observed_events:
            for rel in observed_events:
                ev_id = rel["target_id"]
                if ev_id in entities:
                    ev = entities[ev_id]
                    content.append(f"* [[{ev['sanitized_name']}]]")
                    content.append(f"  * *Loại quan hệ*: `{rel['relationship_type']}`")
                    content.append(f"  * *Bằng chứng*: \"{rel['evidence_quote']}\"")
                    content.append(f"  * *Trạng thái xác minh*: `{rel['verification_status']}`")
                    total_wikilinks += 1
                else:
                    content.append(f"* ID sự kiện không tồn tại: `{ev_id}`")
        else:
            content.append("*Chưa ghi nhận sự kiện rủi ro liên quan.*")
            
        with open(file_path, mode='w', encoding='utf-8') as f_out:
            f_out.write("\n".join(content))
        total_wikipages += 1

    # 4. Create Controls Wiki Pages (KiemSoat)
    for ent_id, ent in entities.items():
        if ent["type"] != "KiemSoat":
            continue
            
        file_name = f"{ent['sanitized_name']}.md"
        file_path = os.path.join(controls_dir, file_name)
        
        mitigates_risks = relations_by_source.get(ent_id, [])
        
        content = []
        content.append("---")
        content.append(f"id: {ent['id']}")
        content.append(f"type: KiemSoat")
        content.append(f"verification_status: {ent['verification_status']}")
        content.append(f"data_origin: {ent['data_origin']}")
        content.append("---")
        content.append("")
        content.append(f"# {ent['name']}")
        content.append("")
        content.append(f"* **Loại kiểm soát**: {ent['control_type']}")
        content.append(f"* **Tần suất thực hiện**: {ent['frequency']}")
        content.append(f"* **Vai trò phụ trách**: `{ent['owner_role_id']}`")
        content.append(f"* **Hiệu quả đánh giá**: {ent['effectiveness']}")
        content.append("")
        
        content.append("## Rủi ro giảm thiểu (Mitigated Risks)")
        if mitigates_risks:
            for rel in mitigates_risks:
                r_id = rel["target_id"]
                if r_id in entities:
                    risk = entities[r_id]
                    content.append(f"* [[{risk['sanitized_name']}]]")
                    content.append(f"  * *Bằng chứng*: \"{rel['evidence_quote']}\"")
                    content.append(f"  * *Trạng thái xác minh*: `{rel['verification_status']}`")
                    total_wikilinks += 1
                else:
                    content.append(f"* ID rủi ro không tồn tại: `{r_id}`")
        else:
            content.append("*Chưa liên kết rủi ro giảm thiểu.*")
            
        with open(file_path, mode='w', encoding='utf-8') as f_out:
            f_out.write("\n".join(content))
        total_wikipages += 1

    # 5. Create Events Wiki Pages (SuKienRuiRo)
    for ent_id, ent in entities.items():
        if ent["type"] != "SuKienRuiRo":
            continue
            
        file_name = f"{ent['sanitized_name']}.md"
        file_path = os.path.join(events_dir, file_name)
        
        observed_from_risks = relations_by_target.get(ent_id, [])
        
        content = []
        content.append("---")
        content.append(f"id: {ent['id']}")
        content.append(f"type: SuKienRuiRo")
        content.append(f"verification_status: {ent['verification_status']}")
        content.append(f"data_origin: {ent['data_origin']}")
        content.append("---")
        content.append("")
        content.append(f"# {ent['name']}")
        content.append("")
        content.append(f"**Mô tả sự kiện**: {ent['description']}")
        content.append(f"* **Thời điểm xảy ra**: {ent['occurred_at']}")
        content.append(f"* **Thời điểm phát hiện**: {ent['discovered_at']}")
        content.append(f"* **Mức độ nghiêm trọng**: {ent['severity']}")
        
        # Display loss amount formatted if numeric
        loss = ent['loss_amount_vnd']
        try:
            loss_val = float(loss)
            loss_str = f"{loss_val:,.0f} VND" if loss_val > 0 else "0 VND"
        except ValueError:
            loss_str = loss + " VND"
            
        content.append(f"* **Tổn thất tài chính ước tính**: {loss_str}")
        content.append("")
        
        content.append("## Rủi ro phát sinh (Originating Risk)")
        if observed_from_risks:
            for rel in observed_from_risks:
                r_id = rel["source_id"]
                if r_id in entities:
                    risk = entities[r_id]
                    content.append(f"* [[{risk['sanitized_name']}]]")
                    content.append(f"  * *Bằng chứng*: \"{rel['evidence_quote']}\"")
                    content.append(f"  * *Trạng thái xác minh*: `{rel['verification_status']}`")
                    total_wikilinks += 1
                else:
                    content.append(f"* ID rủi ro không tồn tại: `{r_id}`")
        else:
            content.append("*Chưa liên kết rủi ro gốc.*")
            
        with open(file_path, mode='w', encoding='utf-8') as f_out:
            f_out.write("\n".join(content))
        total_wikipages += 1

    # 6. Create Home.md
    home_path = os.path.join(wiki_dir, "Home.md")
    
    # Calculate statistics
    risk_count = sum(1 for e in entities.values() if e["type"] == "RuiRo")
    control_count = sum(1 for e in entities.values() if e["type"] == "KiemSoat")
    event_count = sum(1 for e in entities.values() if e["type"] == "SuKienRuiRo")
    
    mitigate_count = sum(1 for r in relations if r["relationship_type"] == "MITIGATES")
    observed_count = sum(1 for r in relations if r["relationship_type"] == "OBSERVED_AS")
    
    home_content = []
    home_content.append("# Wiki Risk Graph 🧠")
    home_content.append("")
    home_content.append("Chào mừng bạn đến với hệ thống Wiki Risk Graph phục vụ đào tạo quản trị rủi ro.")
    home_content.append("")
    home_content.append("## 📊 Thống kê đồ thị")
    home_content.append("| Loại thực thể (Node) | Số lượng |")
    home_content.append("| :--- | :---: |")
    home_content.append(f"| [[#Danh sách Rủi ro\\|RuiRo (Rủi ro)]] | {risk_count} |")
    home_content.append(f"| [[#Danh sách Kiểm soát\\|KiemSoat (Kiểm soát)]] | {control_count} |")
    home_content.append(f"| [[#Danh sách Sự kiện rủi ro\\|SuKienRuiRo (Sự kiện)]] | {event_count} |")
    home_content.append(f"| **Tổng cộng Nodes** | **{len(entities)}** |")
    home_content.append("")
    home_content.append("| Loại mối quan hệ (Edge) | Số lượng |")
    home_content.append("| :--- | :---: |")
    home_content.append(f"| `MITIGATES` (Kiểm soát -> Rủi ro) | {mitigate_count} |")
    home_content.append(f"| `OBSERVED_AS` (Rủi ro -> Sự kiện) | {observed_count} |")
    home_content.append(f"| **Tổng cộng Edges** | **{len(relations)}** |")
    home_content.append("")
    
    # Add lists with wikilinks
    home_content.append("## 📁 Danh sách Rủi ro")
    for ent_id in sorted(entities.keys()):
        ent = entities[ent_id]
        if ent["type"] == "RuiRo":
            home_content.append(f"* [[{ent['sanitized_name']}]] - `{ent['id']}`")
            total_wikilinks += 1
            
    home_content.append("")
    home_content.append("## 🛡️ Danh sách Kiểm soát")
    for ent_id in sorted(entities.keys()):
        ent = entities[ent_id]
        if ent["type"] == "KiemSoat":
            home_content.append(f"* [[{ent['sanitized_name']}]] - `{ent['id']}`")
            total_wikilinks += 1
            
    home_content.append("")
    home_content.append("## 🚨 Danh sách Sự kiện rủi ro")
    for ent_id in sorted(entities.keys()):
        ent = entities[ent_id]
        if ent["type"] == "SuKienRuiRo":
            home_content.append(f"* [[{ent['sanitized_name']}]] - `{ent['id']}`")
            total_wikilinks += 1

    with open(home_path, mode='w', encoding='utf-8') as f_out:
        f_out.write("\n".join(home_content))
    total_wikipages += 1 # Home.md counted
    
    print("=" * 50)
    print("WIKI BUILD COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print(f"- Total Wiki Pages created: {total_wikipages}")
    print(f"- Total Obsidian Wikilinks generated: {total_wikilinks}")
    
    # Demonstrate example path
    print("\nExample Path: KiemSoat -> RuiRo -> SuKienRuiRo")
    # Let's find an active path
    example_path = None
    for rel_mit in relations:
        if rel_mit["relationship_type"] == "MITIGATES":
            ks_id = rel_mit["source_id"]
            rr_id = rel_mit["target_id"]
            for rel_obs in relations:
                if rel_obs["relationship_type"] == "OBSERVED_AS" and rel_obs["source_id"] == rr_id:
                    sk_id = rel_obs["target_id"]
                    
                    ks = entities.get(ks_id)
                    rr = entities.get(rr_id)
                    sk = entities.get(sk_id)
                    
                    if ks and rr and sk:
                        example_path = (ks, rr, sk)
                        break
            if example_path:
                break
                
    if example_path:
        ks, rr, sk = example_path
        print(f"  [{ks['id']}] [[{ks['sanitized_name']}]]")
        print("         │")
        print("         ▼  (MITIGATES)")
        print(f"  [{rr['id']}] [[{rr['sanitized_name']}]]")
        print("         │")
        print("         ▼  (OBSERVED_AS)")
        print(f"  [{sk['id']}] [[{sk['sanitized_name']}]]")
    else:
        print("  No full paths found in data.")
    print("=" * 50)

if __name__ == "__main__":
    main()
