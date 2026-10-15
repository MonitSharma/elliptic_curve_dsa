"""Make observer ownership explicit without changing the symbolic recurrence."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'phase-context-v3';assert not dest.exists();shutil.copytree(root/'phase-context-v2',dest)
p=dest/'src/phase_kernel.rs';s=p.read_text();needle='stack.push(base); base = condition;';assert s.count(needle)==1
s=s.replace(needle,'stack.push(std::mem::replace(&mut base,condition));');p.write_text(s)
(root/'phase3-manifest.json').write_text(json.dumps({'score':None,'scope':'Ownership-only correction to ANF observer; same recurrence and limits. BDD kernel remains byte-identical to validated reference.','sources':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}},indent=2)+'\n')
