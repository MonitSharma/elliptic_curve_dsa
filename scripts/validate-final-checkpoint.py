"""Check exact staged final manifests, source-only patches and artifact bounds."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def blob(p):return subprocess.check_output(['git','show',':'+p],cwd=ROOT)
a=argparse.ArgumentParser(description=__doc__)
a.add_argument('--extra-manifest',action='append',default=[])
args=a.parse_args()
paths=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
allowed=set(json.loads((ROOT/'research-output/overnight-20261014/final-stage-paths.json').read_text()))
assert set(paths)<=allowed,sorted(set(paths)-allowed)
for p in paths:
    assert not p.startswith('agents/'),p
    raw=blob(p)
    assert len(raw)<=2_000_000,p
    if p.endswith('.json'):json.loads(raw)
    if p.endswith('.patch'):
        content=raw.decode('utf8')
        diffs=re.findall(r'^diff --git a/(.*?) b/(.*?)$',content,re.M)
        if Path(p).name=='ht25-v9-done-private-fixture.patch':
            assert re.findall(r'^(?:---|\+\+\+) (.*)$',content,re.M)==['prepared15/tests_midg_k24.rs','private16/tests_midg_k24.rs'],p
        else:assert diffs and all(x.startswith('src/point_add/') and y.startswith('src/point_add/') for x,y in diffs),p
groups=['product/checkpoint-final-product-manifest-v2.json','qubits/ht25-completed-manifest.json',
        'toffoli/final-track-checkpoint-receipt.json']+args.extra_manifest
for n in groups:
    p='experiments/overnight-20261014/'+n
    d=json.loads(blob(p))
    entries=d['files']
    if isinstance(entries,list):
        for e in entries:assert hashlib.sha256(blob(e['path'])).hexdigest()==e['sha256'],e['path']
    else:
        for name,h in entries.items():assert hashlib.sha256(blob((Path(p).parent/name).as_posix())).hexdigest()==h,name
print('Validated',len(paths),'staged paths and',len(groups),'exact manifests; no nested source or bulk outputs.')
