"""Preserve allowed changes from a local isolated snapshot as a compact patch."""
from pathlib import Path
import hashlib,json,difflib,sys
root=Path(__file__).resolve().parents[3]
original=root/'agents/product/src/point_add'
source=Path(sys.argv[1]); name=sys.argv[2]
out=Path(__file__).resolve().parent
chunks=[]; hashes={}
for path in sorted(source.rglob('*')):
    if not path.is_file():continue
    rel=path.relative_to(source);base=original/rel
    current=path.read_bytes()
    if base.exists() and base.read_bytes()==current:continue
    logical='src/point_add/'+rel.as_posix()
    hashes[logical]=hashlib.sha256(current).hexdigest()
    before=base.read_text().splitlines(keepends=True) if base.exists() else []
    after=path.read_text().splitlines(keepends=True)
    chunks.extend(difflib.unified_diff(before,after,fromfile='a/'+logical if base.exists() else '/dev/null',tofile='b/'+logical))
patch=''.join(chunks).encode()
(out/(name+'.patch')).write_bytes(patch)
(out/(name+'-manifest.json')).write_text(json.dumps(dict(base_revision='c5bb1ec876db859a3f9f8a9052c140a145df834e',source_sha256=hashes,patch_sha256=hashlib.sha256(patch).hexdigest(),qualification='Research only; see report and exact full evaluation evidence before claiming a score.',nonce_policy='Inherited TAIL_NONCE unchanged; no packet search or selection.',apply_to='Clean base_revision checkout only.'),indent=2)+'\n',newline='\n')
print(name,len(patch),hashes)
