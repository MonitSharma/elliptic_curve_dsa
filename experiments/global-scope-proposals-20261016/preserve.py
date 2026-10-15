from pathlib import Path
import hashlib,json,subprocess
r=Path(__file__).resolve().parent
assert all((r/(case+'.exit')).read_text().strip()=='0' for case in ['original4b','product95'])
assert (r/'audit.exit').read_text().strip()=='0' and not (r/'NEVER-EMIT.bin').exists()
prepared=json.loads((r/'PREPARED-SOURCE.json').read_text())
for name,h in prepared['private_files'].items():assert hashlib.sha256((r/'tool'/name).read_bytes()).hexdigest()==h,name
assert (r/'audit.rs').read_bytes()==(r/'audit-tool/src/main.rs').read_bytes()
pins={}
for name in ['tool/target/release/product_paired_diagnostic','audit-tool/target/release/scope_proposal_audit']:
    pins[name]=hashlib.sha256((r/name).read_bytes()).hexdigest()
for case in ['original4b','product95']:
    inp=json.loads((r/(case+'-INPUT.json')).read_text())
    assert hashlib.sha256(Path(inp['source']).read_bytes()).hexdigest()==inp['sha256']
    pins[case+'-source']=inp['sha256']
(r/'BINARY-PINS.json').write_text(json.dumps(pins,indent=2)+'\n')
subprocess.run(['python3','/home/hclau/ecdsa_research/collect-terminal-v2.py',str(r)],check=True)
print(hashlib.sha256((r/'evidence.tar.gz').read_bytes()).hexdigest())
