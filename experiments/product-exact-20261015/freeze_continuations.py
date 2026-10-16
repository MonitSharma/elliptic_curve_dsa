"""Freeze predetermined completed continuations; no packet-selected stage count."""
import copy,hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent
cycle=[('retained',128),('retained',512),('retained',1024),('anf',512),('retained',128),('retained',512),('retained',1024)]
for family,count,old,folder in [('product',53,'PRODUCT25_FREEZE.json','product-to53-20261016'),('wide',43,'WIDE_COMPOUND_FREEZE.json','wide-to43-20261016')]:
    d=r/folder;assert (d/'launcher.exit').read_text().strip()=='0'
    base=json.loads((r/old).read_text());stages=copy.deepcopy(base['stages'])
    exemplar=next(x for x in stages if x['family']=='retained' and x['atom_cap']==128)
    for mode,cap in cycle*4:
        x=copy.deepcopy(exemplar);x.update(family=mode,atom_cap=cap);stages.append(x)
    assert len(stages)==count
    path=d/f'{family}-{count}-retained-1024.bin'
    packets={}
    for f in ['independent','structured']:
        line=next(x for x in (d/f'stage-{count}-{f}.log').read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '))
        packets[f]=dict(re.findall(r'(\w+)=([^ ]+)',line));assert packets[f]['unequal_batches']=='0'
    prefix=subprocess.check_output(['python3',str(r/'stream_prefix_manifest.py'),str(path)],text=True)
    (r/f'{family}{count}-prefix-manifest.jsonl').write_text(prefix)
    resources=json.loads((d/f'stage-{count}-resources.jsonl').read_text())
    row={'base_revision':base['base_revision'],'stages':stages,'external_stream':str(path.relative_to(r)),
        'external_stream_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resources':resources,
        'prefix_manifest':json.loads(prefix),'packets':packets,'native_source_port':'pending; coordinator source-bound static table preferred',
        'fresh_failure_census':'pending','nonce_search_performed':False,'score':None,
        'scope':'Exact rewrite preserving inherited failures. Stage count fixed before continuation measurements. Complete 512-input anchored value/phase/scratch proof; diagnostic counts are fixed coupled packets, not universal means.',
        'declaration':str((d/'DECLARATION.txt').relative_to(r)), 'chain_manifest':str((d/f'stage-{count}.manifest').relative_to(r))}
    (r/f'{family.upper()}{count}_FREEZE.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({k:row[k] for k in ['external_stream','external_stream_sha256','resources','prefix_manifest']}),flush=True)
for name in ['guard-cache-weighted-20261016','scoped-cache-20261016','factor-cache-20261016','factor-witness-20261016']:
    d=r/name;print('STATUS',name,(d/'launcher.exit').read_text().strip() if (d/'launcher.exit').exists() else 'running')
    for p in sorted(d.glob('*independent.log')):
        for line in p.read_text().splitlines():
            if line.startswith('DIAGNOSTIC_ONLY'):print(p.name,line)
