"""Versioned six-stage finite value localization, with MR misalignment explicit."""
from pathlib import Path
import hashlib, json, re
out=Path(__file__).parent
raw=out.parents[2]/'research-output/overnight-20261014/product'
e=raw/'b3-earlier-replay'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(e/'run.exit').read_text().strip()=='0'
log=(e/'run.log').read_text();results=[];values={}
for line in log.splitlines():
 if line.startswith('B3_STAGE_DIAGNOSTIC '):
  f=dict(re.findall(r'(\w+)=(\S+)',line));results.append({k:int(v)if v.isdigit()else v for k,v in f.items()})
 elif line.startswith('B3_STAGE_SHOT '):
  f=dict(re.findall(r'(\w+)=(\S+)',line));values[(f['stage'],f['mode'],int(f['index']))]=(f['x'],f['y'])
stages=['raw-body','before-y42-bound','before-square-guard','after-square-guard','after-linear-restore','final']
keys={(mode,index)for stage,mode,index in values}
assert len(results)==12 and len(keys)==271
equal=all(len({values[(stage,mode,index)]for stage in stages})==1 for mode,index in keys)
receipt={'status':'completed_six_stage_native_diagnostic','qualified_score':None,
 'baseline_revision':'b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7','final_stream_sha256':'0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce',
 'gate_inert_observer_final_byte_identity':True,'builder_receipt_sha256':sha(out/'b3-earlier-stages-receipt.json'),
 'stage_results':results,'all271_value_pairs_equal_across_six_stages':equal,
 'earliest_observed_known_point_value_failure_stage':next((r['stage']for r in results if r['mode']=='official_known_bad'and r['bad']),'none'),
 'measurement_alignment':'NONE; stage consumption differs. Fixed starting random domain; source packet unchanged; phase variation and value variation do not independently establish an introduced defect.',
 'native_sha256':(e/'native.sha256').read_text().split()[0],
 'files_sha256':{p.name:sha(p)for p in e.iterdir()if p.is_file()},
 'first249_all_stages':[line for line in log.splitlines()if line.startswith('B3_STAGE_SHOT ')and'mode=official_known_bad index=249 'in line],
 'limitations':['Fifteen official-failing pointtuples are repacked in a15shot batch with fixedMR domain, distinct from exactofficial transcript pairing.','Finite source-bound value diagnostics; global/allMR arithmetic diagnosis remains separate.','No scorer, sourceassertion, protectedfile or nonce changes; no qualified resource claim.']}
(out/'b3-earlier-stage-replay-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
print(json.dumps({'first_observed_value_failure':receipt['earliest_observed_known_point_value_failure_stage'],'all_values_equal':equal,'results':results},indent=2))
