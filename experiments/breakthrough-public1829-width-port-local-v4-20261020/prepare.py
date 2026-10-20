import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_text());assert all(hashlib.sha256((r/'observer'/p).read_bytes()).hexdigest()==h for p,h in {**f['source_files'],**f['protected_files']}.items())
