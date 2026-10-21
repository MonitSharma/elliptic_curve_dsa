import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/p)==h for p,h in f['source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());assert sha(r.parent/'breakthrough-public-semantic-finished-20261021/candidate/ops.bin')==f['expected_stream_sha256']

assert sha(r.parent/"breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/value_normalized_aig_audit")==json.loads((r/"QUALIFIED-BINARY.json").read_text())["sha256"]
