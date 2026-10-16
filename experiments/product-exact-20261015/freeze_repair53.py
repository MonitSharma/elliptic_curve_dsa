"""Source-bind the predeclared repaired25/53 endpoints after full anchored proofs."""
import copy,hashlib,json,re,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair-cache53-20261016';count=int(sys.argv[1]);assert count in [25,53]
target=r/f'REPAIR{count}_FREEZE.json';assert not target.exists()
if count==53:assert (d/'launcher.exit').read_text().strip()=='0'
plan=json.loads((d/'DECLARATION.json').read_text());stages=copy.deepcopy(plan['stages'][:count]);spec=stages[-1]
path=d/f"repair-{count:02d}-{spec['family']}-{spec['atom_cap']}.bin"
packets={}
for f in ['independent','structured']:
    line=next(x for x in (d/f'stage-{count}-{f}.log').read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '))
    packets[f]=dict(re.findall(r'(\w+)=([^ ]+)',line));assert packets[f]['unequal_batches']=='0'
prefix=subprocess.check_output(['python3',str(r/'stream_prefix_manifest.py'),str(path)],text=True)
(r/f'repair{count}-prefix-manifest.jsonl').write_text(prefix)
row={'base_revision':plan['source_base_revision'],'stages':stages,'repair_parent_stream':str((d/'input-1cd3457b.bin').relative_to(r)),'repair_parent_sha256':plan['source_sha256'],'repair_source_snapshot':str((d/'repair-point-add-source').relative_to(r)),'repair_source_manifest':str((d/'repair-source-files.json').relative_to(r)),'repair_parent_prefix_manifest':json.loads((d/'input-prefix-manifest.jsonl').read_text()),'external_stream':str(path.relative_to(r)),'external_stream_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'resources':json.loads((d/f'stage-{count}-resources.jsonl').read_text()),'prefix_manifest':json.loads(prefix),'packets':packets,'native_source_port':'pending','fresh_failure_census_vs_original4b':'pending; fixed32768 final53 plan is REPAIR53_FRESH_CENSUS_PLAN.json','nonce_search_performed':False,'score':None,'scope':'New uniform precision correction plus freshly derived exact caches. Checkpoint25 and final53 fixed before measurements. Anchored512-state equality compares repair parent with transformed source; it does not alone establish correctness or failure rate versus original4b. No old lease reuse or packet-selected stopping.','declaration':str((d/'DECLARATION.json').relative_to(r)),'chain_manifest':str((d/f'stage-{count}.manifest').relative_to(r))}
target.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
