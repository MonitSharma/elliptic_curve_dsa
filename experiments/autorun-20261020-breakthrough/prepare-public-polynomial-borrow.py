from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-polynomial-rematerialization-20261021';r=ex/'breakthrough-public-polynomial-borrow-20261021';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir();sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());assert(old/'run.exit').read_text().strip()=='0'
for n,h in f['tool_source_files'].items():assert sha(old/'local-tool'/n)==h;shutil.copyfile(old/'local-tool'/n,t/n)
exe=ex/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/polynomial_rematerialization';shutil.copyfile(old/'tests.log',r/'original-qualified-tests.log');assert 'test result: ok. 10 passed; 0 failed;'in(r/'original-qualified-tests.log').read_text();f.update(declared_at_utc=datetime.now(timezone.utc).isoformat(),declared_caps=[1233],recipe_term_limit=8,input_streams={'public1829':'16567ee18910b8ee9f7aca60c33f0aa88df9679e6528fa5a7884e74e1a877baf'},original_qualified_source_freeze_sha256=sha(old/'SOURCE-FREEZE.json'),qualified_binary_sha256=sha(exe),scope='UNCHANGED native10-qualified bounded polynomial rematerialization planner on exact CURRENT publicproduct1829 source. Fixedcap1233/8terms before source-only run. No table/circuit/point/failure/nonce tuning, no emitted candidate or achieved qubit count. Native qualification reused byteexact; no new statistical gate or production filter.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
(r/'run.py').write_text('''import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/n)==h for n,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/n)==h for n,h in f['protected_files'].items());stream=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin';assert sha(stream)==f['input_streams']['public1829'];exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/polynomial_rematerialization';assert sha(exe)==f['qualified_binary_sha256'];start=time.monotonic()
def limits():resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
with(r/'audit.log').open('xb')as log:subprocess.run(['timeout','900',str(exe),str(stream),str(r/'cap1233'),'1233','8'],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits,check=True)
v=json.loads((r/'cap1233.json').read_text());v.update(native_controls=10,qualification_reused=True,seconds=time.monotonic()-start);(r/'RESULT.json').write_text(json.dumps(v,indent=2)+'\\n')
''')
base='/mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments';(r/'run-local.sh').write_bytes(f'''#!/bin/sh
set -eu
cd {base}/{r.name}
export OMP_NUM_THREADS=1
trap 's=$?; printf "%s\\n" "$s" > run.exit' EXIT
python3 run.py
'''.encode());(r/'.gitignore').write_text('local-tool/\n__pycache__/\n*.ops.bin\n');(r/'.gitattributes').write_text('* -text\n');(r/'PLAN.md').write_text('# Test one-qubit polynomial borrowing on the exact product record\n\n'+f['scope']+'\n\nWide-parent polynomial plans cover32fewer slots but add too many Toffolis to compete at those caps. This independent exactpublic-cap1233 port tests whether masked Clifford/XOR recipes can cover its many short peaks at less than the approximately612T product allowance. All original failures/partial bounds retained. Any actual candidate must still have an emitted source-bound allocator, complete protected phase/RNG/guard qualification, fresh development and its own sole statistical gate before unchanged benchmark/official submission.\n');print(r.name)
