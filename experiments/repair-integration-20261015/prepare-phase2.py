"""Preserve the failed observer; repair scope, then use the frozen BDD kernel."""
from pathlib import Path
import shutil,hashlib,json
root=Path(__file__).resolve().parent
dest=root/'phase-context-v2';assert not dest.exists();shutil.copytree(root/'phase-context',dest)
p=dest/'src/phase_kernel.rs';s=p.read_text();needle='        max_phase = max_phase.max(phase.0.len());';assert s.count(needle)==1
s=s.replace(needle,'        let (a,t) = (op.q_control1.0 as usize,op.q_target.0 as usize);\n'+needle);p.write_text(s)
bdd=root/'phase-bdd';assert not bdd.exists();shutil.copytree(root.parent/'rail-control-20261015/phase-audit-v3',bdd)
kernel=(root.parent/'arithmetic-repair-20261015/proof_kernel.rs').read_bytes()
assert hashlib.sha256(kernel).hexdigest()=='72ab93a2fa1fd20bb3aad370aca9f6016ea9069013eaaa34d6b02d911d859622'
(bdd/'src/phase_kernel.rs').write_bytes(kernel)
p=bdd/'src/main.rs';s=p.read_text();assert s.count('a.maximum_phase_terms')==1;s=s.replace('a.maximum_phase_terms','a.maximum_phase_size_bound').replace('max_terms={} measurements={}','max_size_bound={} measurements={}');p.write_text(s)
(root/'phase2-manifest.json').write_text(json.dumps({'score':None,'scope':'Same fixed single zero-slope input and complete square-room stream; ANF error-context scope repair and unchanged previously validated BDD kernel. Caps unchanged.','sources':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for d in [dest,bdd] for p in d.rglob('*') if p.is_file()}},indent=2)+'\n')
