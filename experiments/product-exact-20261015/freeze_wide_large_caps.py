"""Freeze each independent completed endpoint, without selecting by packet gain."""
import copy,hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'wide-largecaps-20261016';plan=json.loads((d/'DECLARATION.json').read_text());base=json.loads((r/plan['source_freeze']).read_text());results=json.loads((d/'RESULTS.json').read_text())
for result in results:
    if result['status']!='ENDPOINT_GENERATED_PROOFS_PASS':continue
    spec=result['case'];cap=spec['atom_cap'];name=d/spec['name'];path=Path(str(name)+'.bin');target=r/f'WIDE95_PLUS_CAP{cap}_FREEZE.json'
    packets={}
    for packet in ['independent','structured']:
        line=next(x for x in Path(str(name)+f'-{packet}.log').read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '))
        row=dict(re.findall(r'(\w+)=([^ ]+)',line));assert row['unequal_batches']=='0';packets[packet]=row
    prefix=subprocess.check_output(['python3',str(r/'stream_prefix_manifest.py'),str(path)],text=True);(r/f'wide95-plus-cap{cap}-prefix-manifest.jsonl').write_text(prefix)
    row={'base_revision':base['base_revision'],'stages':copy.deepcopy(base['stages'])+[spec],'external_stream':str(path.relative_to(r)),'external_stream_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resources':json.loads(Path(str(name)+'-resources.jsonl').read_text()),'prefix_manifest':json.loads(prefix),'packets':packets,'native_source_port':'pending','fresh_failure_census':'pending; entire sole32768 sample in declaration, no interim selection','fresh_census_label':spec['fresh_census_label'],'nonce_search_performed':False,'score':None,'declaration':str((d/'DECLARATION.json').relative_to(r)),'chain_manifest':str(Path(str(name)+'.manifest').relative_to(r)),'scope':'Independent fixed one-stage endpoint after95. Source-only analytical rank; no packet-selected source or earlier checkpoint.512 full replay comparisons passed; packet T counts remain diagnostic.'}
    assert row['external_stream_sha256']==result['stream_sha256']
    if target.exists():assert json.loads(target.read_text())==row,'existing freeze differs'
    else:target.write_text(json.dumps(row,indent=2)+'\n')
    print(target.name,row['external_stream_sha256'],flush=True)
