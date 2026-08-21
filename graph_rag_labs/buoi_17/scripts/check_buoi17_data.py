"""
Script: check_buoi17_data.py
Purpose: Kiểm tra chi tiết dữ liệu trong buoi_17/data và so sánh với buoi_14/data.
"""

import os
import sys
import pandas as pd
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

DATA_14_SECURE = PROJECT_ROOT / "buoi_14" / "data" / "processed" / "chunks_secure.csv"
DATA_17_POLICIES = CURRENT_DIR.parent / "data" / "agribank_internal_policies.csv"
DATA_17_COMBINED = CURRENT_DIR.parent / "data" / "chunks_combined_secure.csv"


def check_data():
    print("==================================================")
    print("KIỂM TRA DỮ LIỆU TRONG BUỔI 17 & BỔ SUNG SO VỚI BUỔI 14")
    print("==================================================\n")

    # 1. Dữ liệu gốc Buổi 14
    if DATA_14_SECURE.exists():
        df14 = pd.read_csv(DATA_14_SECURE)
        print(f"--- [Buổi 14 Data] {DATA_14_SECURE.name} ---")
        print(f"  - Số dòng (chunks): {len(df14):,}")
        print(f"  - Số văn bản duy nhất (unique docs): {df14['document_id'].nunique()}")
        print(f"  - Các loại văn bản: {df14['document_type'].unique().tolist()}")
        print()

    # 2. File agribank_internal_policies.csv trong Buổi 17
    if DATA_17_POLICIES.exists():
        df_pol = pd.read_csv(DATA_17_POLICIES)
        print(f"--- [Buổi 17 Data] {DATA_17_POLICIES.name} ---")
        print(f"  - Số dòng: {len(df_pol):,}")
        print(f"  - Các cột: {list(df_pol.columns)}")
        print("  - Mẫu dữ liệu:")
        print(df_pol.head(5).to_string())
        print()

    # 3. File chunks_combined_secure.csv trong Buổi 17
    if DATA_17_COMBINED.exists():
        df_comb = pd.read_csv(DATA_17_COMBINED)
        print(f"--- [Buổi 17 Data] {DATA_17_COMBINED.name} ---")
        print(f"  - Số dòng (chunks): {len(df_comb):,}")
        print(f"  - Số văn bản duy nhất: {df_comb['document_id'].nunique()}")
        print(f"  - Phân loại vai tròallowed_roles:")
        print(df_comb['allowed_roles'].value_counts())
        print("\n  - Danh sách các văn bản duy nhất trong tệp combined:")
        unique_docs = df_comb.groupby("document_id").first().reset_index()
        for idx, r in unique_docs.iterrows():
            doc_id = r['document_id']
            doc_type = r.get('document_type', '')
            title = str(r.get('title', ''))[:70]
            cnt = len(df_comb[df_comb['document_id'] == doc_id])
            print(f"    {idx+1}. Doc ID: {doc_id} | Chunks: {cnt} | Type: {doc_type} | Title: {title}")


if __name__ == "__main__":
    check_data()
