import os
import sys
from pathlib import Path

# Ensure UTF-8 output encoding and project root in sys.path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import neo4j
import sentence_transformers
import streamlit
from src.config import VALID_ROLES, get_neo4j_config, validate_roles

print("=== RBAC SETUP VERIFICATION ===")
print(f"Working Directory: {os.path.basename(os.getcwd())}/")
print(f"Selected Roles: {VALID_ROLES}")
print(f"Database Env Path: {get_neo4j_config()['env_path']}")
print(f"Neo4j URI: {get_neo4j_config()['uri']}")
print(f"Role sanitization check: {validate_roles(['Admin', 'HR', 'Guest', 'InvalidRole'])}")
print("Installed Dependencies:")
print(f" - pandas: {pd.__version__}")
print(f" - neo4j: {neo4j.__version__}")
print(f" - sentence-transformers: {sentence_transformers.__version__}")
print(f" - streamlit: {streamlit.__version__}")
print("Status: Ready to proceed")

