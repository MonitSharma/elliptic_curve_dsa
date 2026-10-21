import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert all(sha(r/'local-tool'/n)==h for n,h in f['source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/n)==h for n,h in f['protected_files'].items());assert sha(r.parent/f['cache_path'])==f['cache_sha256']and sha(r.parent/f['stream_path'])==f['stream_sha256']and sha(r/'WORD-FIXTURES.json')==f['fixtures_sha256']
