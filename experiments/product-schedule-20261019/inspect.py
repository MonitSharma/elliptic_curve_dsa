import json
from pathlib import Path
base = Path('/home/hclau/ecdsa_research')
p = base/'product-width-tradeoff-20261019/parent-width.json'
d = json.loads(p.read_text())
print(json.dumps({k:v for k,v in d.items() if k!='scratch_at_first_peak'}, indent=2))
print('Shortest active lifetimes:')
print(json.dumps(sorted(d['scratch_at_first_peak'],key=lambda x:x['end']-x['start'])[:25],indent=2))
source = base/'product-pareto-20261019/parent'
print('SOURCE STATE')
import subprocess
for args in [['git','-C',str(source),'rev-parse','HEAD'], ['git','-C',str(source),'status','--short']]:
    subprocess.run(args, check=True)
for name in ['parent-generate.log','parent-exact.json']:
    path=base/'product-pareto-20261019'/name
    print(name)
    print(path.read_text()[-16000:])
