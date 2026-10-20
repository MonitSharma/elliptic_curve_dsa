import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());src=r.parent/'breakthrough-public1829-width-port-local-v4-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/zero_lifetime_audit';results={}
for mode,h in f['inputs'].items():
 p=src/mode/'ops.bin';assert sha(p)==h
 with(r/(mode+'.log')).open('xb')as log:subprocess.run([str(exe),str(p),str(r/(mode+'.json'))],stdout=log,stderr=subprocess.STDOUT,check=True)
 results[mode]=json.loads((r/(mode+'.json')).read_text())
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_PROVISIONAL_PUBLIC1829_LIFETIME_AUDIT_NOT_A_RESOURCE_RECORD','cases':results,'scope':f['scope'],'binary_sha256':sha(exe)},indent=2)+'\n')
