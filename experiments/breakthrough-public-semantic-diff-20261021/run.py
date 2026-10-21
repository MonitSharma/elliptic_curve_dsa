import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/n)==h for n,h in f['tool_source_files'].items());old=r.parent/'breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin';new=r.parent/'breakthrough-global-semantic-component-20261020/public1829.ops.bin';assert sha(old)==f['input_sha256']and sha(new)==f['output_sha256'];exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/semantic_stream_diff'
with(r/'diff.log').open('xb')as log:subprocess.run([str(exe),str(old),str(new),str(r/'DIFF.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
