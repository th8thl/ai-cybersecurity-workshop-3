"""Keep inherited defenses and verify the current RAG exercise state."""
import argparse
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--secured',action='store_true')
parser.add_argument('--semantic',action='store_true',help='Also verify live Ollama embeddings and Qwen, plus inherited semantic NeMo.')
args=parser.parse_args()
secure=args.secured or root.name=='solution'
# All inherited Session 2 tests remain required in BOTH copies.
inherited=sorted('tests.'+p.stem for p in (root/'tests').glob('test_*.py') if not p.stem.startswith('test_rag_'))
labels=['tests'] if secure else inherited+['tests.test_rag_basics','tests.test_rag_interface','tests.test_rag_vectors','tests.test_rag_pdf']
commands=[
    [sys.executable,'manage.py','test',*labels],
    [sys.executable,'scripts/healthcheck.py','--secured',*(['--semantic'] if args.semantic else [])],
    [sys.executable,'scripts/rag_healthcheck.py',*(['--secured'] if secure else []),*(['--live'] if args.semantic else [])],
    [sys.executable,'scripts/verify_sast.py','--secured'],
    [sys.executable,'guardrails/compare.py','--configured'],
]
for command in commands:subprocess.run(command,cwd=root,check=True)
print('All requested workshop checks passed.')
