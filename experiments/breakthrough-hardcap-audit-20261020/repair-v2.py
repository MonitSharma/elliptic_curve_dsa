"""Observe all three allocator-entry paths; preserve failed two-path assertion."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fold-square-ripple-20261020'
assert(r/'run.exit').read_text().strip()=='1'
failed=r/'failed-two-path-assert-v1';failed.mkdir(exist_ok=False)
for name in['prepare.py','prepare.log','run.exit']:shutil.copyfile(r/name,failed/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
script=(r/'prepare.py').read_text();suffix=script[script.index("p=t/'src/point_add/builder.rs'"):]
assert suffix.count('assert raw.count(needle)==2')==1
suffix=suffix.replace('assert raw.count(needle)==2','assert raw.count(needle)==3')
exec(compile(suffix,str(r/'prepare.py')+'-repaired-suffix','exec'))
freeze=json.loads((r/'SOURCE_FREEZE.json').read_text());freeze['repair']='All three allocator-entry increment paths traced, rather than an incorrect asserted count of two. No gate changes.'
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
