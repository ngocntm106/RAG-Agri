import importlib

modules = ['chromadb', 'google', 'dotenv']
for name in modules:
    try:
        importlib.import_module(name)
        print(f'{name}: OK')
    except Exception as exc:
        print(f'{name}: FAIL {type(exc).__name__} {exc}')
