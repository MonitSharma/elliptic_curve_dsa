"""Freeze the sole predeclared95 endpoint after every required replay passed."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;family=sys.argv[1];assert family in ['product','wide']
d=r/f'{family}-to95-rank-20261016';assert (d/'launcher.exit').read_text().strip()=='0'
plan=json.loads((d/'DECLARATION.json').read_text());assert plan['fixed_endpoint']==95
target=r/f'{family.upper()}95_FREEZE.json';assert not target.exists()
packets={}
for stage in plan['checkpoints']:
    packets[stage]={}
    for packet in ['independent','structured']:
        line=next(x for x in (d/f'stage-{stage}-{packet}.log').read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '))
        row=dict(re.findall(r'(\w+)=([^ ]+)',line));assert row['unequal_batches']=='0';packets[stage][packet]=row
spec=plan['stages'][-1];path=d/f"{family}-95-{spec['family']}-{spec['atom_cap']}-{spec['rank']}.bin"
prefix=subprocess.check_output(['python3',str(r/'stream_prefix_manifest.py'),str(path)],text=True)
(r/f'{family}95-prefix-manifest.jsonl').write_text(prefix)
answer={'base_revision':plan['base_revision'],'stages':copy.deepcopy(plan['stages']),'external_stream':str(path.relative_to(r)),'external_stream_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resources':json.loads((d/'stage-95-resources.jsonl').read_text()),'prefix_manifest':json.loads(prefix),'packets':packets,'native_source_port':'pending','fresh_failure_census':'pending','nonce_search_performed':False,'score':None,'declaration':str((d/'DECLARATION.json').relative_to(r)),'chain_manifest':str((d/'stage-95.manifest').relative_to(r)),'scope':'Predeclared fixed95 endpoint; all checkpoints and512 coupled quantum/classical/phase/scratch comparisons pass. These packet counts are diagnostic, not a scored record or failure qualification. No earlier checkpoint selection.'}
target.write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer),flush=True)
