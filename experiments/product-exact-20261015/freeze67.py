"""Freeze only the completed, predeclared stage67 endpoints; never choose a packet."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent
family=sys.argv[1];assert family in ['product','wide']
folder='product-to67-rank-20261016' if family=='product' else 'wide-to67-scratch-20261016'
d=r/folder;assert (d/'launcher.exit').read_text().strip()=='0'
old='PRODUCT53_FREEZE.json' if family=='product' else 'WIDE43_FREEZE.json'
base=json.loads((r/old).read_text());stages=copy.deepcopy(base['stages'])
if family=='product':
    cycle=[('retained',128,'start'),('retained',512,'proxy'),('retained',1024,'start'),('anf',512,'proxy'),('retained',128,'proxy'),('retained',512,'start'),('retained',1024,'proxy')]
    for mode,cap,rank in cycle*2:stages.append({'family':mode,'atom_cap':cap,'pair_cap':64,'product_cap':1000000,'rank':rank,'split':True,'flags':'three per donor; disjoint top-level lifetimes'})
    path=d/'product-67-retained-1024-proxy.bin'
else:
    for cap in [128,512,1024,128,512,1024]*4:stages.append({'family':'retained','atom_cap':cap,'pair_cap':256,'extra_zero_slots_offered':16,'product_cap':1000000,'rank':'density','split':True})
    path=d/'wide-67-retained-1024.bin'
assert len(stages)==67
target=r/f'{family.upper()}67_FREEZE.json';assert not target.exists()
packets={}
for f in ['independent','structured']:
    line=next(x for x in (d/f'stage-67-{f}.log').read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '))
    packets[f]=dict(re.findall(r'(\w+)=([^ ]+)',line));assert packets[f]['unequal_batches']=='0'
prefix=subprocess.check_output(['python3',str(r/'stream_prefix_manifest.py'),str(path)],text=True)
(r/f'{family}67-prefix-manifest.jsonl').write_text(prefix)
row={'base_revision':base['base_revision'],'stages':stages,'external_stream':str(path.relative_to(r)),'external_stream_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resources':json.loads((d/'stage-67-resources.jsonl').read_text()),'prefix_manifest':json.loads(prefix),'packets':packets,'native_source_port':'pending','fresh_failure_census':'pending','nonce_search_performed':False,'score':None,'scope':'Fixed67 stages predeclared before metrics; exact rewrite preserving inherited failures. Anchored512-state equality and sampled coupled T are diagnostic only. No packet-selected stopping or benchmark claim.','declaration':str((d/'DECLARATION.txt').relative_to(r)),'chain_manifest':str((d/'stage-67.manifest').relative_to(r))}
target.write_text(json.dumps(row,indent=2)+'\n')
print(json.dumps(row),flush=True)
