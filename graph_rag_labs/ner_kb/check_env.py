import os
import sys
import subprocess

# Set encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("BƯỚC 0: KIỂM TRA MÔI TRƯỜNG HỆ THỐNG")
print("=" * 60)

# 1. Python version
python_ver = sys.version
print(f"Python Version: {python_ver}")
python_pass = sys.version_info >= (3, 8)
status_python = "PASS" if python_pass else "FAIL"

# 2. Virtual environment check
# In python, sys.prefix != sys.base_prefix indicates a venv is active
in_venv = (sys.prefix != sys.base_prefix) or ('VIRTUAL_ENV' in os.environ) or ('CONDA_PREFIX' in os.environ)
status_venv = "PASS" if in_venv else "FAIL"
if in_venv:
    venv_path = os.environ.get('VIRTUAL_ENV') or os.environ.get('CONDA_PREFIX') or sys.prefix
    print(f"Virtual environment active: {venv_path}")
else:
    print("Warning: Virtual environment is not active (running in global Python environment).")

# 3. Check input files
metadata_path = os.path.join("ner_kb", "metadata.csv")
content_path = os.path.join("ner_kb", "content.csv")

meta_exists = os.path.exists(metadata_path)
content_exists = os.path.exists(content_path)

status_metadata = "PASS" if meta_exists else "FAIL"
status_content = "PASS" if content_exists else "FAIL"

print(f"File ner_kb/metadata.csv: {'FOUND' if meta_exists else 'NOT FOUND'}")
print(f"File ner_kb/content.csv: {'FOUND' if content_exists else 'NOT FOUND'}")

# 4. Check Python packages and install if missing
packages = {
    "pandas": "pandas",
    "beautifulsoup4": "bs4",
    "python-dotenv": "dotenv",
    "google-genai": "google.genai",
    "neo4j": "neo4j"
}

missing_packages = []
for pkg_name, import_name in packages.items():
    try:
        __import__(import_name)
        print(f"Package '{pkg_name}': OK")
    except ImportError:
        print(f"Package '{pkg_name}': MISSING")
        missing_packages.append(pkg_name)

if missing_packages:
    print(f"Installing missing packages: {missing_packages}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
        # Double check
        still_missing = []
        for pkg_name in missing_packages:
            try:
                __import__(packages[pkg_name])
            except ImportError:
                still_missing.append(pkg_name)
        if still_missing:
            status_packages = "FAIL"
            print(f"Failed to install some packages: {still_missing}")
        else:
            status_packages = "PASS"
            print("All packages installed successfully.")
    except Exception as e:
        status_packages = "FAIL"
        print(f"Error during package installation: {e}")
else:
    status_packages = "PASS"

# 5. Check .env configuration
env_path = os.path.join("ner_kb", ".env")
env_exists = os.path.exists(env_path)

gemini_config_pass = False
neo4j_config_pass = False

if env_exists:
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "YOUR_KEY_HERE":
        gemini_config_pass = True
        # Print masked key
        masked_key = gemini_key[:4] + "..." + gemini_key[-4:] if len(gemini_key) > 8 else "..."
        print(f"Gemini API key found: {masked_key}")
    else:
        print("Error: GEMINI_API_KEY is missing or placeholder in .env")
        
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_database = os.getenv("NEO4J_DATABASE")
    
    if neo4j_uri and neo4j_user and neo4j_password:
        # Test Neo4j connectivity
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            driver.verify_connectivity()
            print("Successfully connected to Neo4j database!")
            neo4j_config_pass = True
            driver.close()
        except Exception as e:
            print(f"Error: Failed to connect to Neo4j. Details: {e}")
    else:
        print("Error: Neo4j connection details are incomplete in .env")
else:
    print("Error: .env file not found in ner_kb/")

status_gemini = "PASS" if gemini_config_pass else "FAIL"
status_neo4j = "PASS" if neo4j_config_pass else "FAIL"

print("\n" + "=" * 60)
print("BÁO CÁO KẾT QUẢ ĐIỀU KIỆN ĐẦU VÀO (PASS/FAIL):")
print("=" * 60)
print(f"[{status_python}] Python")
print(f"[{status_venv}] Virtual environment")
print(f"[{status_metadata}] metadata.csv")
print(f"[{status_content}] content.csv")
print(f"[{status_packages}] Python packages")
print(f"[{status_gemini}] Gemini configuration")
print(f"[{status_neo4j}] Neo4j configuration")
print("=" * 60)

if all(s == "PASS" for s in [status_python, status_venv, status_metadata, status_content, status_packages, status_gemini, status_neo4j]):
    print("Môi trường đã ĐẠT tất cả các yêu cầu. Sẵn sàng cho Bước 1.")
    sys.exit(0)
else:
    print("Môi trường chưa đạt yêu cầu. Vui lòng khắc phục các điểm FAIL.")
    sys.exit(1)
