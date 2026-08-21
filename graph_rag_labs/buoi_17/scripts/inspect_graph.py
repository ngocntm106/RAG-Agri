"""
Script: inspect_graph.py
Purpose: Kiểm tra Knowledge Graph hiện có (Neo4j & CSV Data) cho Compliance Gap Checker.
"""

import os
import sys
import glob
import pandas as pd
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent


def inspect_graph():
    print("==================================================")
    print("KIỂM TRA KNOWLEDGE GRAPH VÀ CÁC MỐI QUAN HỆ (GRAPH INSPECTION)")
    print("==================================================\n")

    # 1. Kiểm tra các tệp CSV chứa quan hệ
    rel_files = [
        "kb+hops/relationships.csv",
        "buoi_13/data/relationships_seed.csv",
        "ner_kb/relationships.csv"
    ]

    for rel_path in rel_files:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            df_rel = pd.read_csv(full_path)
            print(f"--- File: {rel_path} (Rows: {len(df_rel)}) ---")
            print(f"Columns: {list(df_rel.columns)}")
            print(df_rel.head(5).to_string())
            print()

    # 2. Kiểm tra kết nối Neo4j Live DB (nếu có)
    print("--- Kiềm tra Neo4j Live Database ---")
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        pwd = os.getenv("NEO4J_PASSWORD", "password")
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            res = session.run("MATCH ()-[r]->() RETURN count(r) as cnt, type(r) as rel_type ORDER BY cnt DESC LIMIT 20")
            records = list(res)
            print(f"Kết nối thành công tới Neo4j tại {uri}!")
            for r in records:
                print(f"  - Relation [{r['rel_type']}]: {r['cnt']:,} edges")
        driver.close()
    except Exception as e:
        print(f"Neo4j Live DB Offline hoặc không có kết nối: {e}")


if __name__ == "__main__":
    inspect_graph()
