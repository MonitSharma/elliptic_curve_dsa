"""Preserve the failed external build and fix its ambiguous index-vector type."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'phase-audit-v2';assert not dest.exists();shutil.copytree(root/'phase-audit',dest)
p=dest/'src/main.rs';s=p.read_text();needle='let mut selected=vec![];';assert s.count(needle)==1;p.write_text(s.replace(needle,'let mut selected:Vec<usize>=vec![];'))
assert (dest/'src/phase_kernel.rs').read_bytes()==(root/'phase-audit/src/phase_kernel.rs').read_bytes()
(root/'phase-v2-manifest.json').write_text(json.dumps({'score':None,'scope':'External runner type annotation only; original failed source and log preserved, frozen phase kernel unchanged.','source_sha256':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
