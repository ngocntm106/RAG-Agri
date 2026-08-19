"""
Configuration Module for Buoi 15: RBAC on Data & Secure Retrieval Pipeline.
Loads database credentials from local .env and provides single-source-of-truth for RBAC Roles.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Define base directory (buoi_14)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env in buoi_14
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# ==========================================
# 1. RBAC ROLES CONFIGURATION
# ==========================================
ROLE_ADMIN = "Admin"
ROLE_HR = "HR"
ROLE_STAFF = "Staff"
ROLE_GUEST = "Guest"

VALID_ROLES = [ROLE_ADMIN, ROLE_HR, ROLE_STAFF, ROLE_GUEST]

ROLE_DESCRIPTIONS = {
    ROLE_ADMIN: "Quản trị viên toàn quyền hệ thống - truy cập toàn bộ tài liệu (HR, Risk, Staff, Public).",
    ROLE_HR: "Bộ phận Nhân sự - quản lý tài liệu nhân sự, lương thưởng, tuyển dụng, bổ nhiệm, nội quy.",
    ROLE_STAFF: "Nhân viên chính thức - truy cập các quy định nghiệp vụ thông thường, hướng dẫn công việc và quy chế chung.",
    ROLE_GUEST: "Khách vãng lai / Thực tập sinh - chỉ truy cập các tài liệu công khai, quy định chung."
}

def get_valid_roles() -> list[str]:
    """Return list of valid system roles."""
    return list(VALID_ROLES)

def validate_roles(user_roles: list[str] | set[str] | None) -> list[str]:
    """
    Validate and sanitize a list of user roles.
    Filters out invalid/typo roles and returns a validated list.
    If none provided, defaults to [ROLE_GUEST].
    """
    if not user_roles:
        return [ROLE_GUEST]
    
    valid_set = set(VALID_ROLES)
    cleaned = [r for r in user_roles if r in valid_set]
    return cleaned if cleaned else [ROLE_GUEST]

# ==========================================
# 2. DATABASE CONFIGURATION (Neo4j)
# ==========================================
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

def get_neo4j_config() -> dict:
    """Return database connection parameters as a dictionary."""
    return {
        "uri": NEO4J_URI,
        "user": NEO4J_USER,
        "password": NEO4J_PASSWORD,
        "database": NEO4J_DATABASE,
        "env_path": str(ENV_PATH) if ENV_PATH.exists() else ".env"
    }

# ==========================================
# 3. DIRECTORY & DATA PATHS
# ==========================================
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHUNKS_NORMALIZED_PATH = PROCESSED_DATA_DIR / "chunks_normalized.csv"
CHUNKS_SECURE_PATH = PROCESSED_DATA_DIR / "chunks_secure.csv"
CACHE_DIR = BASE_DIR / "cache"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure essential directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
