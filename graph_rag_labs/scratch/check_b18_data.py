import sys
import os
import pandas as pd
from dotenv import load_dotenv

print("="*60)
print("BUỔI 18 — ENVIRONMENT & DATA VALIDATION REPORT")
print("="*60)

# 1. Environment & Venv check
print("\n[1] PYTHON & VIRTUAL ENVIRONMENT CHECK")
python_exec = sys.executable
in_venv = sys.prefix != sys.base_prefix
print(f"- Python Executable: {python_exec}")
print(f"- Virtual Environment Active: {in_venv}")

# 2. Check Directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
buoi_18_dir = os.path.join(base_dir, "buoi_18")
scripts_dir = os.path.join(buoi_18_dir, "scripts")
outputs_dir = os.path.join(buoi_18_dir, "outputs")
data_dir = os.path.join(buoi_18_dir, "data")

print("\n[2] DIRECTORY STRUCTURE CHECK")
print(f"- buoi_18/ directory: {'READY' if os.path.exists(buoi_18_dir) else 'MISSING'}")
print(f"- buoi_18/scripts/ directory: {'READY' if os.path.exists(scripts_dir) else 'MISSING'}")
print(f"- buoi_18/outputs/ directory: {'READY' if os.path.exists(outputs_dir) else 'MISSING'}")
print(f"- buoi_18/data/ directory: {'READY' if os.path.exists(data_dir) else 'MISSING'}")

# 3. Check API Key
env_path = os.path.join(buoi_18_dir, ".env")
load_dotenv(env_path)
gemini_key = os.getenv("GEMINI_API_KEY")
llm_key = os.getenv("LLM_API_KEY")
model_name = os.getenv("LLM_MODEL")

print("\n[3] .ENV & API KEY CHECK")
print(f"- File .env path: {env_path}")
print(f"- GEMINI_API_KEY valid: {bool(gemini_key and gemini_key != 'YOUR_GEMINI_API_KEY_FREE')}")
print(f"- LLM_API_KEY valid: {bool(llm_key and llm_key != 'YOUR_GEMINI_API_KEY_FREE')}")
print(f"- LLM_MODEL: {model_name}")

# 4. Check Internal Data (agribank_internal_policies.csv)
policy_path = os.path.join(data_dir, "agribank_internal_policies.csv")
print("\n[4] INTERNAL DATA CHECK (agribank_internal_policies.csv)")
internal_data_ready = False
if os.path.exists(policy_path):
    df_pol = pd.read_csv(policy_path)
    print(f"- File Path: {policy_path}")
    print(f"- Total Chunks (rows): {len(df_pol)}")
    print(f"- Total Columns: {len(df_pol.columns)}")
    expected_cols = [
        "chunk_id", "document_id", "text", "source_file", "title",
        "so_ky_hieu", "loai_van_ban", "co_quan_ban_hanh", "ngay_ban_hanh",
        "chapter", "section", "article", "citation", "allowed_roles"
    ]
    missing_cols = [col for col in expected_cols if col not in df_pol.columns]
    print(f"- 14 Metadata Columns Check: {'PASS (All 14 columns present)' if len(missing_cols) == 0 else f'FAIL (Missing: {missing_cols})'}")
    if len(missing_cols) == 0:
        internal_data_ready = True
        print("  14 Columns verified:")
        for idx, col in enumerate(expected_cols, 1):
            print(f"    {idx:2d}. {col}")

# 5. Check Combined Data (chunks_combined_secure.csv)
combined_path = os.path.join(data_dir, "chunks_combined_secure.csv")
print("\n[5] COMBINED DATA CHECK (chunks_combined_secure.csv)")
combined_data_ready = False
if os.path.exists(combined_path):
    df_comb = pd.read_csv(combined_path)
    print(f"- File Path: {combined_path}")
    print(f"- Total Chunks (rows): {len(df_comb)}")
    
    internal_mask = df_comb["source_file"] == "agribank_internal_policies.csv"
    legal_mask = df_comb["source_file"] != "agribank_internal_policies.csv"
    
    internal_df = df_comb[internal_mask]
    legal_df = df_comb[legal_mask]
    
    internal_docs_count = internal_df['document_id'].nunique()
    legal_docs_count = legal_df['document_id'].nunique()
    
    print(f"- Legal Documents Count: {legal_docs_count} văn bản ({len(legal_df)} chunks)")
    print(f"- Internal Documents Count: {internal_docs_count} văn bản ({len(internal_df)} chunks)")
    print(f"- Total Combined Documents: {legal_docs_count + internal_docs_count} văn bản ({len(df_comb)} chunks)")
    
    if len(legal_df) > 0 and len(internal_df) > 0:
        combined_data_ready = True

# Overall Status Summary
env_ready = in_venv and bool(gemini_key) and os.path.exists(scripts_dir) and os.path.exists(outputs_dir)

print("\n" + "="*60)
print("EXECUTIVE SUMMARY STATUS:")
print(f"ENVIRONMENT READY: {'YES' if env_ready else 'NO'}")
print(f"INTERNAL DATA READY: {'YES' if internal_data_ready else 'NO'}")
print(f"COMBINED DATA READY: {'YES' if combined_data_ready else 'NO'}")
print("="*60)
