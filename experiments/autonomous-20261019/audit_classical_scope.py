"""Size/path audit of only this research cycle's intended staging scope."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;root=r.parents[1]
names=['product-guard-schedule-20261019','product-guard-mrfree-20261019','product-two-target-20261019','product-branch-alias-20261019','product-classical-factors-refresh-20261019','product-captured-factors-20261019','product-captured-factors-native-20261019','product-classical-factors-native-20261019','product-factor-cost-proof-20261019','product-classical-type-probe-20261019','product-classical-control-expression-20261019','product-classical-nine-proof-20261019','product-classical-nine-20261019','parent4-final-sat-v2-20261019']
p=r/'LOG.md';p.write_text(p.read_text(encoding='utf-8').rstrip()+'\n',encoding='utf-8',newline='\n')
files=[]
for name in names:
    for p in (root/'experiments'/name).rglob('*'):
        if not p.is_file():continue
        assert not any(x in p.parts for x in ['target','candidate','libraries','.git','__pycache__'])
        assert p.suffix!='.bin' and p.stat().st_size<5_000_000
        files.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
result={'scope':'Only current completed experiments, frozen native candidate and declared live gate. No credentials, runtime binaries, public-data/plot/README updates or user submodules. Archives preserve exact bytes despite Git newline normalization.',
 'directories':names,'files':len(files),'bytes':sum(x['bytes'] for x in files),'largest_files':sorted(files,key=lambda x:-x['bytes'])[:8]}
(r/'CLASSICAL-CYCLE-SCOPE.json').write_text(json.dumps(result,indent=2)+'\n',newline='\n')
print(json.dumps(result,indent=2))
