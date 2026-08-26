import sys
import os
import pandas as pd
from dotenv import load_dotenv

def main():
    print("="*60)
    print("BUỔI 18 — KIỂM TRA MÔI TRƯỜNG & DỮ LIỆU (TRONG BUOI_17)")
    print("="*60)

    # 1. Python & Virtual Environment Check
    print("\n[1] PYTHON & VIRTUAL ENVIRONMENT CHECK")
    python_exec = sys.executable
    in_venv = sys.prefix != sys.base_prefix
    print(f"- Python Executable: {python_exec}")
    print(f"- Virtual Environment Active: {in_venv}")

    # 2. Paths inside buoi_17
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    buoi17_dir = os.path.dirname(scripts_dir)
    data_dir = os.path.join(buoi17_dir, "data")
    outputs_dir = os.path.join(buoi17_dir, "outputs")
    env_path = os.path.join(buoi17_dir, ".env")

    print("\n[2] DIRECTORIES & ENV CHECK")
    print(f"- Base buoi_17 path: {buoi17_dir}")
    print(f"- scripts/ ready: {os.path.exists(scripts_dir)}")
    print(f"- outputs/ ready: {os.path.exists(outputs_dir)}")
    print(f"- data/ ready: {os.path.exists(data_dir)}")

    # 3. Check .env API Key
    load_dotenv(env_path)
    gemini_key = os.getenv("GEMINI_API_KEY")
    llm_key = os.getenv("LLM_API_KEY")
    model_name = os.getenv("LLM_MODEL")

    print("\n[3] API KEY CHECK")
    has_gemini = bool(gemini_key and gemini_key != "YOUR_GEMINI_API_KEY_FREE")
    has_llm = bool(llm_key and llm_key != "YOUR_GEMINI_API_KEY_FREE")
    print(f"- GEMINI_API_KEY valid: {has_gemini}")
    print(f"- LLM_API_KEY valid: {has_llm}")
    print(f"- LLM_MODEL: {model_name}")

    # 4. Check agribank_internal_policies.csv
    policy_path = os.path.join(data_dir, "agribank_internal_policies.csv")
    print("\n[4] INTERNAL POLICIES DATA CHECK")
    internal_ready = False
    if os.path.exists(policy_path):
        df_pol = pd.read_csv(policy_path)
        print(f"- File: {policy_path}")
        print(f"- Total rows (chunks): {len(df_pol)}")
        print(f"- Total columns: {len(df_pol.columns)}")
        
        expected_cols = [
            "so_ky_hieu", "article", "title", "allowed_roles",
            "chunk_id", "document_id", "text", "source_file",
            "loai_van_ban", "co_quan_ban_hanh", "ngay_ban_hanh",
            "chapter", "section", "citation"
        ]
        missing_cols = [c for c in expected_cols if c not in df_pol.columns]
        
        if len(missing_cols) == 0 and len(df_pol.columns) == 14:
            internal_ready = True
            print("- 14 Metadata Columns Check: PASS (Tất cả 14 cột tồn tại đầy đủ)")
            print("  Danh sách 14 cột:")
            for idx, col in enumerate(df_pol.columns, 1):
                print(f"    {idx:2d}. {col}")
        else:
            print(f"- 14 Metadata Columns Check: FAIL (Thiếu: {missing_cols})")
    else:
        print(f"- File NOT FOUND at: {policy_path}")

    # 5. Check chunks_combined_secure.csv
    combined_path = os.path.join(data_dir, "chunks_combined_secure.csv")
    print("\n[5] COMBINED SECURE DATA CHECK")
    combined_ready = False
    if os.path.exists(combined_path):
        df_comb = pd.read_csv(combined_path)
        print(f"- File: {combined_path}")
        print(f"- Total chunks: {len(df_comb)}")
        
        internal_mask = df_comb["source_file"] == "agribank_internal_policies.csv"
        legal_mask = df_comb["source_file"] != "agribank_internal_policies.csv"
        
        internal_df = df_comb[internal_mask]
        legal_df = df_comb[legal_mask]
        
        legal_docs = legal_df['document_id'].nunique()
        internal_docs = internal_df['document_id'].nunique()
        
        print(f"- Số lượng Văn bản Pháp lý (Nghị định/Thông tư/Luật): {legal_docs} văn bản ({len(legal_df)} chunks)")
        print(f"- Số lượng Văn bản Nội bộ (Agribank): {internal_docs} văn bản ({len(internal_df)} chunks)")
        print(f"- Tổng số văn bản kết hợp: {legal_docs + internal_docs} văn bản")
        
        if len(legal_df) > 0 and len(internal_df) > 0:
            combined_ready = True
    else:
        print(f"- File NOT FOUND at: {combined_path}")

    # Final Status Summary
    env_ready = in_venv and has_gemini and os.path.exists(scripts_dir) and os.path.exists(outputs_dir)

    print("\n" + "="*60)
    print("BÁO KẾT QUẢ:")
    print(f"ENVIRONMENT READY: {'YES' if env_ready else 'NO'}")
    print(f"INTERNAL DATA READY: {'YES' if internal_ready else 'NO'}")
    print(f"COMBINED DATA READY: {'YES' if combined_ready else 'NO'}")
    print("="*60)

if __name__ == "__main__":
    main()
