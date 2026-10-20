"""Choose only structurally cheaper whole-tick alternatives, with live interfaces equal."""
import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert(r/'run.exit').read_text().strip()=='0'and not(r/'TICK-CHOICES.json').exists();result=json.loads((r/'RESULT.json').read_text());cases=result['cases'];assert len(cases)==22 and cases[0]['label']=='baseline';tables={}
for case in cases:
 assert case['raw_sha256']==case['expected_raw_sha256'];rows=json.loads((r/case['label']/'TICKS.json').read_text());table={tuple(x['key']):x for x in rows};assert len(table)==len(rows)==550;tables[case['label']]=table
base=tables['baseline'];assert all(set(t)==set(base)for t in tables.values());choices=[];rejected=[]
for key,old in base.items():
 options=[(old['cost'],0,0,'baseline',cases[0])]
 for case in cases[1:]:
  row=tables[case['label']][key]
  if(row['live_before'],row['live_after'])!=(old['live_before'],old['live_after']):rejected.append({'key':key,'label':case['label'],'reason':'Different live-qubit boundary counts'});continue
  options.append((row['cost'],case['keep'],case['room'],case['label'],case))
 cost,_,_,label,case=min(options,key=lambda x:x[:4])
 if cost<old['cost']:
  choices.append({'key':key,'keep':case['keep'],'mask':case['mask'],'room':case['room'],'profile_case':label,'baseline_tick_cost':old['cost'],'selected_tick_cost':cost,'saving':old['cost']-cost,'baseline_live_before':old['live_before'],'baseline_live_after':old['live_after']})
answer={'status':'STRUCTURAL_TICK_CHOICES_REQUIRE_NEW_COMPLETE_BUILD','baseline_raw_sha256':cases[0]['raw_sha256'],'choices':choices,'ticks_chosen':len(choices),'sum_predicted_tick_savings':sum(x['saving']for x in choices),'baseline_raw_diagnostic_weight':762230.75,'predicted_mixed_raw_diagnostic_weight':762230.75-sum(x['saving']for x in choices),'rejected_live_interfaces':rejected,'source_profile_freeze_sha256':sha(r/'SOURCE-FREEZE.json'),'profile_result_sha256':sha(r/'RESULT.json'),'tick_table_hashes':{c['label']:sha(r/c['label']/'TICKS.json')for c in cases},'scope':'Deterministic minimum static whole-tick cost, tie-break by fewer retained helpers then room and case label. Exact frozen raw streams byte-verified in all22 source cases. All choices require equal live-qubit boundary counts. NO point/nonce/census packet or measured failure inputs used. Predicted sum need not compose, because allocator/bookkeeping and external sweeps may interact; require new direct mixed source build, exact controls, final gate, nonce and unchanged benchmark before any result.'};(r/'TICK-CHOICES.json').write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps({k:v for k,v in answer.items()if k not in ['choices','rejected_live_interfaces','tick_table_hashes']},indent=2));print('Rejected live-boundary comparisons',len(rejected))
