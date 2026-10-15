"""Reuse proved-zero idle wires with larger immutable expression retention."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'analyzer'
assert not dest.exists()
shutil.copytree(root.parent/'cache-retention-20261015/analyzer',dest)
old=root.parent/'toffoli-readiness-20261015'
(dest/'src/lazy_cache.rs').write_bytes((old/'lazy_cache_audit.rs').read_bytes()+(old/'lazy_cache_tests.rs').read_bytes())
(root/'manifest.json').write_text(json.dumps({'status':'external-component-only','score':None,'source_revision':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7','source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
