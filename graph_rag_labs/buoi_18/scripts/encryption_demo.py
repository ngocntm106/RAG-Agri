"""
Module: encryption_demo.py
Purpose: Demo mã hóa dữ liệu at-rest (Data At-Rest Encryption) cho Buổi 17 bằng Cryptography (Fernet).
Minh họa bảo vệ tệp audit_log.jsonl khi lưu trữ trên đĩa.
"""

import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

KEY_FILE = PROJECT_ROOT / "secret.key"
INPUT_FILE = OUTPUTS_DIR / "audit_log.jsonl"
ENCRYPTED_FILE = OUTPUTS_DIR / "audit_log.jsonl.enc"
DECRYPTED_FILE = OUTPUTS_DIR / "audit_log_decrypted.jsonl"


def get_or_generate_key(key_path: Path = KEY_FILE) -> bytes:
    """Nạp hoặc tạo mới khóa Fernet ngẫu nhiên và lưu vào tệp (không hard-code key)."""
    if key_path.exists():
        key = key_path.read_bytes()
    else:
        key = Fernet.generate_key()
        key_path.write_bytes(key)
        print(f"[Encryption] Đã tạo khóa mã hóa ngẫu nhiên tại: {key_path.name}")
    return key


def run_encryption_demo():
    print("==================================================")
    print("DEMO MÃ HÓA DỮ LIỆU AT-REST (CRYPTOGRAPHY / FERNET)")
    print("==================================================\n")

    # 1. Nạp khóa từ tệp .key
    key = get_or_generate_key(KEY_FILE)
    cipher = Fernet(key)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp đầu vào: {INPUT_FILE}")

    # 2. Đọc file nguyên bản
    original_bytes = INPUT_FILE.read_bytes()
    print(f"1. Đọc tệp gốc: {INPUT_FILE.name} ({len(original_bytes):,} bytes)")

    # 3. Mã hóa dữ liệu (Encrypt)
    encrypted_bytes = cipher.encrypt(original_bytes)
    ENCRYPTED_FILE.write_bytes(encrypted_bytes)
    print(f"2. Mã hóa thành công -> {ENCRYPTED_FILE.name} ({len(encrypted_bytes):,} bytes)")

    # 4. Giải mã dữ liệu (Decrypt)
    read_encrypted = ENCRYPTED_FILE.read_bytes()
    decrypted_bytes = cipher.decrypt(read_encrypted)
    DECRYPTED_FILE.write_bytes(decrypted_bytes)
    print(f"3. Giải mã thành công -> {DECRYPTED_FILE.name} ({len(decrypted_bytes):,} bytes)")

    # 5. So sánh đối chiếu dữ liệu gốc vs sau giải mã
    is_match = (original_bytes == decrypted_bytes)
    print(f"\n4. Kết quả so sánh 100% byte-for-byte: {is_match}")

    if is_match:
        print("-> ENCRYPT & DECRYPT MATCH SUCCESSFUL!")
    else:
        print("-> LỖI: Dữ liệu sau giải mã không khớp với bản gốc!")

    print("\n==================================================")
    print("DEMO COMPLETED (Note: Production-Ready: NO)")
    print("==================================================")

    return {
        "encrypt_pass": True,
        "decrypt_match": is_match,
        "production_ready": "NO"
    }


if __name__ == "__main__":
    run_encryption_demo()
