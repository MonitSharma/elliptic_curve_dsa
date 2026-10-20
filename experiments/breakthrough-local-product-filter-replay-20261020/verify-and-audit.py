import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert all(sha(t/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
actual=sha(t/'ops.bin');assert actual==f['expected_ops_sha256'],actual
(r/'STREAM-REPRODUCTION.json').write_text(json.dumps({'status':'EXACT_OLD_FROZEN_STREAM_REPRODUCED_WITH_LOCAL_COMPILER','stream_sha256':actual,'source_files':len(f['source_files']),'protected_files':len(f['protected_files']),'scope':f['scope']},indent=2)+'\n')
audit=r.parent/'breakthrough-value-guard-fusion-audit-20261020';tool=audit/'local-tool';compiler='/root/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/cargo'
with (r/'audit-build.log').open('xb')as log:subprocess.run([compiler,'build','--release','--locked','--bin','value_ir_audit'],cwd=tool,stdout=log,stderr=subprocess.STDOUT,check=True)
with (r/'full-audit.log').open('xb')as log:subprocess.run([str(tool/'target/release/value_ir_audit'),str(t/'ops.bin'),str(r/'full-audit.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
result=json.loads((r/'full-audit.json').read_text());(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_LOCAL_STREAM_REPLAY_AND_VERIFICATION_ONLY_AUDIT_COMPLETE','native_controls':20,'audit':result,'scope':f['scope']},indent=2)+'\n')
