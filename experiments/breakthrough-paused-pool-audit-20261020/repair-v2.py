"""Finish metadata preparation after the diff-capture API error; no source edit."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-paused-read-20261020'
assert(r/'run.exit').read_text().strip()=='1'
failed=r/'failed-diff-capture-api-v1';failed.mkdir(exist_ok=False)
for name in['prepare.py','prepare.log','run.exit','source.patch']:shutil.copyfile(r/name,failed/name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(t/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items()if p!='src/point_add/builder.rs')
script=(r/'prepare.py').read_text();middle=script[script.index("p=t/'src/point_add/builder.rs'"):script.index('assert all(sha(t/p)==h for p,h in f[')]
middle=middle.replace('raw=p.read_bytes()',"raw=(old/'observer/src/point_add/builder.rs').read_bytes()").replace('p.write_bytes(raw)','assert p.read_bytes()==raw')
exec(compile(middle,str(r/'prepare.py')+'-verify-metadata','exec'))
result=subprocess.run(['git','diff','--no-index',str(old/'observer/src/point_add/builder.rs'),str(p)],capture_output=True,check=False)
assert result.returncode==1;(r/'observer-only.patch').write_bytes(result.stdout)
exec(compile(script[script.index("(r/'SOURCE_FREEZE.json')"):],str(r/'prepare.py')+'-finish-freeze','exec'))
print('Exact expected metadata source verified; no source repair; freeze finished.')
