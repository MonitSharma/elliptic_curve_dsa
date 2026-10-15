"""Preserve the earlier fifteen counterexamples verbatim, without searching inputs."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
source=root.parent/'overnight-20261014/product-b3-arithmetic-compare/known-official-failures.tsv'
lines=[l.split() for l in source.read_text().splitlines() if l.strip() and not l.startswith('#')]
assert len(lines)==15 and lines[0][0]=='249'
dest=root/'known15.tsv';assert not dest.exists()
dest.write_text('\n'.join('\t'.join(v[:7]) for v in lines)+'\n')
(root/'known15-manifest.json').write_text(json.dumps({'original_path':str(source),'original_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'normalized_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'indices':[int(v[0]) for v in lines],'qualification':'fixed diagnostic counterexamples, not an official benchmark packet'},indent=2)+'\n')
