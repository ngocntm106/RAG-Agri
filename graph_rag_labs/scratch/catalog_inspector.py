import os
import pandas as pd
import json

base_dir = r"c:\Users\minhn\OneDrive\Desktop\Học AI\RAG\graph_rag_labs\buoi_17"
pol_path = os.path.join(base_dir, "data", "agribank_internal_policies.csv")
comb_path = os.path.join(base_dir, "data", "chunks_combined_secure.csv")

df_pol = pd.read_csv(pol_path)
df_comb = pd.read_csv(comb_path)

print("=== INTERNAL POLICIES (agribank_internal_policies.csv) ===")
print("Total rows:", len(df_pol))
print("Unique document_id:", df_pol["document_id"].nunique())

grouped = df_pol.groupby("document_id")

for doc_id, group in grouped:
    first = group.iloc[0]
    print(f"\nDocument ID: {doc_id}")
    print(f"  Title: {first['title']}")
    print(f"  Số ký hiệu: {first['so_ky_hieu']}")
    print(f"  Loại VB: {first['loai_van_ban']}")
    print(f"  Cơ quan ban hành: {first['co_quan_ban_hanh']}")
    print(f"  Ngày ban hành: {first['ngay_ban_hanh']}")
    print(f"  Chunks count: {len(group)}")
    print(f"  Allowed roles: {first['allowed_roles']}")
    print(f"  Articles sample: {group['article'].tolist()}")
    print(f"  Null articles: {group['article'].isna().sum()}")
    print(f"  Null citations: {group['citation'].isna().sum()}")
    print(f"  Null allowed_roles: {group['allowed_roles'].isna().sum()}")

print("\n" + "="*60)
print("=== LEGAL DOCUMENTS IN COMBINED (chunks_combined_secure.csv) ===")
legal_df = df_comb[df_comb["source_file"] != "agribank_internal_policies.csv"]
print("Total legal chunks:", len(legal_df))
print("Unique legal document_id:", legal_df["document_id"].nunique())

for doc_id, group in legal_df.groupby("document_id"):
    first = group.iloc[0]
    print(f"\nLegal Doc ID: {doc_id}")
    print(f"  Title: {first['title']}")
    print(f"  Số ký hiệu: {first['so_ky_hieu']}")
    print(f"  Loại VB: {first['loai_van_ban']}")
    print(f"  Cơ quan ban hành: {first['co_quan_ban_hanh']}")
    print(f"  Chunks count: {len(group)}")
