from pathlib import Path
import hashlib,json,tarfile
root=Path(__file__).resolve().parent
paths=[p for p in root.iterdir() if p.is_file() and p.suffix in ['.c','.h','.py','.sh','.log','.sha256','.txt','.exit','.md']]
for name in ['lib/low/KeccakP-1600-times8/AVX512/KeccakP-1600-times8-AVX512.c','lib/low/KeccakP-1600-times8/AVX512/KeccakP-1600-times8-AVX512.h','lib/common/align.h','lib/common/brg_endian.h','lib/common/PlSnP-common.h','lib/low/common/SIMD-types.h']:
 paths.append(root/'XKCP'/name)
paths.append(root/'include/config.h')
paths=sorted(set(paths));manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
with tarfile.open(root/'evidence.tar.gz','w:gz') as t:
 for p in paths+[root/'manifest.json']:t.add(p,arcname=str(p.relative_to(root)))
print('Bundled',len(paths),'artifacts')
