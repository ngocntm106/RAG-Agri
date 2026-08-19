import importlib
packages = [
    ("streamlit","streamlit"),
    ("google-genai","google_genai"),
    ("chromadb","chromadb"),
    ("psycopg","psycopg"),
    ("python-dotenv","dotenv"),
]
for display,name in packages:
    try:
        importlib.import_module(name)
        print(f"{display}: PASS")
    except Exception as e:
        print(f"{display}: FAIL -> {type(e).__name__}")
