from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent
patch=r.parent/'overnight-20261014/product/classical-xor-candidate.patch'
lines=patch.read_text().splitlines();files={};current=None
for line in lines:
    if line.startswith('+++ b/src/point_add/'):
        current=line.split('/')[-1];files[current]=[]
    elif line.startswith('--- '):current=None
    elif current is not None and line.startswith('+') and not line.startswith('+++'):files[current].append(line[1:])
for name in ['classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']:
    assert name in files
    (r/'proof'/name).write_text('\n'.join(files[name])+'\n',encoding='utf-8',newline='\n')
(r/'EXTRACTION.json').write_text(json.dumps({'archived_patch':str(patch),'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),
 'extracted':{name:hashlib.sha256((r/'proof'/name).read_bytes()).hexdigest() for name in ['classical_factors_xor.rs','product7_simplify.rs','tests_classical_factors.rs']}},indent=2)+'\n')
