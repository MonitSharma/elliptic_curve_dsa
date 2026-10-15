from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parent
prefix=root.parent/'prefilter-20261015/evidence/mr-mask-tip-v1'
binary=prefix.with_suffix('.bin');rows=Path(str(prefix)+'.sha256').read_text().splitlines()
matches=[row.split()[0] for row in rows if row.split()[-1].endswith('mr-mask-tip-v1.bin')];assert len(matches)==1
subprocess.run([sys.executable,str(root/'verify-export.py'),str(binary),matches[0]],check=True)
