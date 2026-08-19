import importlib
packages = [
    ("streamlit","streamlit"),
    ("google-genai","google_genai"),
    ("chromadb","chromadb"),
    ("psycopg","psycopg"),
    ("python-dotenv","dotenv"),
]
out = []
for display,name in packages:
    try:
        importlib.import_module(name)
        out.append(f"{display}: PASS")
    except Exception as e:
        out.append(f"{display}: FAIL -> {type(e).__name__}")
with open('c:/Users/minhn/OneDrive/Desktop/Học AI/05_mẫu/Rag_thuchanh/RAG/rag_foundation/buoi_06/check_imports.out','w',encoding='utf-8') as f:
    f.write('\n'.join(out))
print('DONE')
