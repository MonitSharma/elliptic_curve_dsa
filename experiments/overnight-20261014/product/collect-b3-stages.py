"""Collect stage-local value evidence; phase comparisons remain unaligned."""
from pathlib import Path
import hashlib, json, re

out=Path(__file__).parent
raw=out.parents[2]/'research-output/overnight-20261014/product'
e=raw/'b3-stage-replay'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log=(e/'run.log').read_text()
results=[]; values={}
for line in log.splitlines():
 if line.startswith('B3_STAGE_DIAGNOSTIC '):
  f=dict(re.findall(r'(\w+)=(\S+)',line));results.append({k:int(v)if v.isdigit()else v for k,v in f.items()})
 elif line.startswith('B3_STAGE_SHOT '):
  f=dict(re.findall(r'(\w+)=(\S+)',line));values[(f['stage'],f['mode'],int(f['index']))]=(f['x'],f['y'])
stages=['before-square-guard','after-square-guard','after-linear-restore','final']
keys={(mode,index)for stage,mode,index in values}
equal=all(len({values[(stage,mode,index)]for stage in stages})==1 for mode,index in keys)
assert len(results)==8 and len(keys)==271
receipt={'status':'completed_stage_native_diagnostic_with_failures','qualified_score':None,
 'baseline_revision':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7','final_stream_sha256':'0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce',
 'gate_inert_observer_final_byte_identity':True,'source_only_builder_receipt_sha256':sha(out/'b3-stages-receipt.json'),
 'stage_results':results,'all271_observed_value_pairs_equal_across_four_stages':equal,
 'measurement_alignment':'NONE; fixed starting MR domain has differing R/Hmr consumption between stages. Neither rate changes nor equality of phase is asserted.',
 'packet_scope':'All15candidate-official classical failing point tuples, repacked15shots; fresh256independent point tuples. Expected values recomputed from protected curve reference and asserted equal to packet.',
 'native_sha256':(e/'native.sha256').read_text().split()[0],
 'files_sha256':{p.name:sha(p)for p in e.iterdir()if p.is_file()},
 'stage_stream_hashes_file_sha256':sha(raw/'b3-stages-streams.sha256'),
 'first249_all_stages':[line for line in log.splitlines()if line.startswith('B3_STAGE_SHOT ')and'mode=official_known_bad index=249 'in line],
 'interpretation':'All15known candidate failures already have wrongy beforeSquareGuard; this finite evidence localizes their value obstruction upstream of that guard. Does not exclude other guard defects.',
 'coordinate_count_correction':'An earlier report incorrectly generalized the y-only firstshot249 to all15official failures. The preserved officialcounterexamples have13xerrors and15yerrors, matching repacked stagecounts; noMR/lane value-sensitivity inference is supported by that count comparison.',
 'limitations':['The15repacked fixedMR cases and exactofficial transcript both show13xerrors and15yerrors. They remain separate finite measurement domains.','No global exactness or resource qualification claim.','Source assertions and nonce unchanged; protectedserializer copied read-only into point_add observer; no protectedfile edits.']}
(out/'b3-stage-replay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
print(json.dumps({'all_values_equal':equal,'cases':len(keys),'results':results},indent=2))
