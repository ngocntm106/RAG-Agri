from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
OUT = BASE / 'command_probe_out.txt'
PY = Path(r'c:/Users/minhn/OneDrive/Desktop/Học AI/05_mẫu/Rag_thuchanh/RAG/rag_foundation/buoi_05/.venv/Scripts/python.exe')

commands = [
    [str(PY), '-m', 'pip', 'show', 'chromadb'],
    [str(PY), '-m', 'pip', 'show', 'google-genai'],
    [str(PY), '-m', 'pip', 'show', 'python-dotenv'],
]

lines = []
for cmd in commands:
    proc = subprocess.run(cmd, capture_output=True)
    lines.append(f'CMD: {cmd!r}')
    lines.append(f'RC: {proc.returncode}')
    lines.append('STDOUT:')
    lines.append(proc.stdout.decode('utf-8', errors='backslashreplace'))
    lines.append('STDERR:')
    lines.append(proc.stderr.decode('utf-8', errors='backslashreplace'))
    lines.append('---')

OUT.write_text('\n'.join(lines), encoding='utf-8')
