"""Restore the unchanged reproduction/attribution tail omitted by a section edit."""
from pathlib import Path
import difflib,subprocess
r=Path(__file__).resolve().parents[2];d=Path(__file__).resolve().parent
old=subprocess.check_output(['git','show','HEAD^:README.md'],cwd=r).decode()
tail=old[old.index('Only `src/point_add/` may change in a contestant submission.'):]
base=subprocess.check_output(['git','show','HEAD:README.md'],cwd=r).decode()
assert '## Reproduce and explore' not in base
owned=base.rstrip()+'\n\n'+tail
working=(r/'README.md').read_text(encoding='utf-8');assert '## Reproduce and explore' not in working
(r/'README.md').write_bytes((working.rstrip()+'\n\n'+tail).encode('utf-8'))
(d/'README-tail-restoration.patch').write_bytes(''.join(difflib.unified_diff(base.splitlines(True),owned.splitlines(True),fromfile='a/README.md',tofile='b/README.md')).encode('utf-8'))
assert '[Upload receipt and fresh verification]' in (r/'README.md').read_text(encoding='utf-8')
print('Restored all unchanged submission rules, reproduction, directory map and attribution; foreign note preserved')
