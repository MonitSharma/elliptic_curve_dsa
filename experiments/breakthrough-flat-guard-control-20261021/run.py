import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/n)==h for n,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/n)==h for n,h in f['protected_files'].items());stream=r/'official-ffe20.ops.bin';assert sha(stream)==f['input_streams']['official_ffe20'];exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/flat_guard_control';start=time.monotonic()
def limits():resource.setrlimit(resource.RLIMIT_AS,(8*1024**3,8*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
with(r/'qualification.log').open('xb')as log:subprocess.run(['timeout','1200',str(exe),str(stream),str(r/'flat')],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits,check=True)
v=json.loads((r/'flat.json').read_text());v.update(output_sha256=sha(r/'flat.ops.bin'),native_controls=5,seconds=time.monotonic()-start);(r/'RESULT.json').write_text(json.dumps(v,indent=2)+'\n')
