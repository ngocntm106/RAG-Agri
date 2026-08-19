import importlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"
CHROMA_DIR = ROOT / "storage" / "chroma"

REQUIRED_PACKAGES = [
    ("streamlit", "streamlit"),
    ("google.genai", "google-genai"),
    ("chromadb", "chromadb"),
    ("psycopg", "psycopg"),
    ("dotenv", "python-dotenv"),
]

REQUIRED_ENV = {
    "GEMINI_API_KEY": "",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "rag_db",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "",
}


def ensure_env() -> None:
    if not ENV_PATH.exists():
        if ENV_EXAMPLE_PATH.exists():
            ENV_PATH.write_text(ENV_EXAMPLE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            ENV_PATH.write_text("", encoding="utf-8")

    existing = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                existing[key.strip()] = value.strip()

    lines = []
    for key in REQUIRED_ENV:
        if key in existing and existing[key] != "":
            lines.append(f"{key}={existing[key]}")
        else:
            lines.append(f"{key}={REQUIRED_ENV[key]}")

    if ENV_PATH.exists():
        content = ENV_PATH.read_text(encoding="utf-8")
        for key in REQUIRED_ENV:
            if f"{key}=" not in content:
                lines.append(f"{key}={REQUIRED_ENV[key]}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_packages() -> None:
    for module_name, package_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(module_name)
            print(f"PASS {package_name}")
        except Exception:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"INSTALLED {package_name}")


def ensure_chroma() -> None:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        from chromadb import PersistentClient

        client = PersistentClient(path=str(CHROMA_DIR))
        client.get_or_create_collection(name="demo_collection")
        print("CHROMA_MODE Embedded Local")
    except Exception as exc:
        print(f"CHROMA_MODE FAIL {exc.__class__.__name__}")


def ensure_postgres() -> None:
    try:
        import psycopg
    except Exception as exc:
        print(f"POSTGRES FAIL import: {exc}")
        return

    password = os.getenv("POSTGRES_PASSWORD", "")
    try:
        conn = psycopg.connect(host="localhost", port=5432, dbname="postgres", user="postgres", password=password)
        conn.close()
        print("POSTGRES_SERVER OK")
    except Exception as exc:
        print("POSTGRES_SERVER FAIL")
        print("HƯỚNG DẪN: cài PostgreSQL, ghi mật khẩu vào POSTGRES_PASSWORD trong .env")
        return

    try:
        conn = psycopg.connect(host="localhost", port=5432, dbname="postgres", user="postgres", password=password)
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("rag_db",))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute("CREATE DATABASE rag_db")
        conn.commit()
        conn.close()
        print("POSTGRES_DB rag_db OK")
    except Exception as exc:
        print(f"POSTGRES_DB FAIL {exc.__class__.__name__}")


def main() -> None:
    print("Python:", sys.executable)
    ensure_env()
    ensure_packages()
    ensure_chroma()
    ensure_postgres()


if __name__ == "__main__":
    main()
