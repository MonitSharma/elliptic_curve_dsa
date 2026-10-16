from pathlib import Path
import json,re,hashlib,collections
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');p=2**256-2**32-977
assert(r/'actual-replay.exit').read_text().strip()=='0'
text=(r/'actual-replay.log').read_text();declaration=json.loads((r/'REPLAY-PREDECLARATION.json').read_text());binding=json.loads((r/'actual-markers.json').read_text())
expected=[json.loads(s)for s in(r/'packets/expected-census.jsonl').read_text().splitlines()]
targets={b['batch']*64+f['lane']:dict(f,batch=b['batch'])for b in expected for f in b['failures']if f['value']};assert len(targets)==431
def parse(line):
 x=dict(re.findall(r'(\w+)=([^ ]+)',line));x['line']=line
 for k in ['shot','at','tick','window','shift','value_width','cin','low_L','E','Nm','m','C','c','observed_low','got','want']:
  if k in x:
   try:x[k]=int(x[k],0)if str(x[k]).startswith(('0x','-0x'))else int(x[k])
   except ValueError:pass
 for k in ['rev','skip','inv','final_bad','event','observer_equal']:
  if k in x:x[k]=x[k]=='true'
 if'tape='in line:x['tape']=[int(z)for z in re.search(r'tape=\[([^\]]*)\]',line)[1].split(',')]
 return x
types=['PAY_EVENT','STAGE_EVENT','FOLD_BOUNDARY','FOLD_LOW_MISMATCH','WINDOW_EVENT','PAY_SHOT','ATTR_BATCH']
events={name:[parse(s)for s in text.splitlines()if s.startswith(name+' ')]for name in types}
assert len(events['PAY_SHOT'])==431 and{e['shot']for e in events['PAY_SHOT']}==set(targets)
assert len(events['ATTR_BATCH'])==413
assert all(e['original_census_flags_reproduced']=='true'and e['full64q_b_phase_T_equal']=='true'for e in events['ATTR_BATCH'])
assert all(e['final_bad']and e['observer_equal']for e in events['PAY_SHOT'])
assert(r/'actual-replay-stream-before.sha256').read_text().split()[0]==(r/'actual-replay-stream-after.sha256').read_text().split()[0]==declaration['actual_final_stream_sha256']
model={}
path=r.parent/'prefilter-20261015/evidence/native-walk4096.jsonl'
for line in path.read_text().splitlines():
 x=json.loads(line);shot=int(x['batch'])*64+int(x['lane'])
 if shot in targets:model[shot]=x
assert len(model)==431
for x in events['FOLD_BOUNDARY']:
 expected_low=(x['low_L']+x['C'])%(1<<x['window']);x['recomputed_low_formula_matches']=expected_low==x['observed_low']
 x['signed_boundary_delta']=x['c'];x['candidate_correction_to_full_payload']=x['c']*(1<<(x['window']if x['rev']else x['window']-x['shift']))
 # The source-derived integer carry is a diagnosis only after its low equation
 # is checked at these actual final gates, not from a field name in a log.
for x in events['WINDOW_EVENT']:
 a,b,got,want,diff=[int(x[k],16)if isinstance(x[k],str)else x[k]for k in ['a','b','got','want','diff']]
 width=x['value_width']+20;lo=(a>>x['shift'])%2**width;term=(-1 if x['inv']else 1)*(b+x['cin']);c=(lo+term)//2**width
 truncated=(a-lo*2**x['shift']+((lo+term)%2**width)*2**x['shift'])%p
 full=(a+term*2**x['shift'])%p
 x.update(exact_truncated_window_equation=got==truncated,exact_full_signed_field_equation=want==full,signed_carry=c,top=x['shift']+width,
          exact_loss_delta_equation=diff==(-c*2**(x['shift']+width))%p)
cases=[]
for shot,witness in sorted(targets.items()):
 ev={kind:[x for x in rows if x.get('shot')==shot]for kind,rows in events.items()if kind!='ATTR_BATCH'}
 assert len(ev['PAY_EVENT'])<=1 and len(ev['STAGE_EVENT'])<=1
 pay=ev['PAY_EVENT'][0]if ev['PAY_EVENT']else None;stage=ev['STAGE_EVENT'][0]if ev['STAGE_EVENT']else None
 matching=[]
 if pay:
  delta=int(pay['diff'],16)
  for f in ev['FOLD_BOUNDARY']:
   if f['recomputed_low_formula_matches']and(f['phase'],f['tick'],f['rev'])==(pay['phase'],pay['tick'],pay['rev'])and not pay['skip']:
    if delta==(-f['candidate_correction_to_full_payload'])%p:matching.append(f)
 windows=[x for x in ev['WINDOW_EVENT']if x['exact_truncated_window_equation']and x['exact_full_signed_field_equation']and x['exact_loss_delta_equation']]
 local=sorted([*ev['PAY_EVENT'],*ev['FOLD_LOW_MISMATCH'],*ev['WINDOW_EVENT']],key=lambda x:x['at'])
 if matching:category='exact_fold_boundary_loss'
 elif windows and stage and stage['stage']=='square':category='exact_square_window_loss'
 elif pay:category='other_actual_payload_transition_mismatch'
 elif stage:category='wrong_global_stage_without_observed_payload_transition_mismatch'
 else:category='outside_observed_stage_or_unresolved'
 cases.append(dict(shot=shot,batch=witness['batch'],lane=witness['lane'],original_failure=witness,
  advisory_model_only=model[shot],model_predicted_wrong_value=bool(model[shot]['predicted_wrong_value']),
  first_incorrect_global_stage=stage,first_observed_local_interface_violation=local[0]if local else None,
  first_payload_mismatch=pay,matched_fold_boundary_losses=matching,exact_square_window_losses=windows,
  attribution_category=category,events=ev,
  causal_limit='First observed mathematical interface violation; inherited entry preconditions and any earlier unmapped internal fold remain explicit. Advisory model is not native-stage authority. No global correctness proof inferred.'))
unknown=[x for x in cases if not x['model_predicted_wrong_value']]
def counts(rows):
 return dict(shots=len(rows),batches=len({x['batch']for x in rows}),lambda_value_affected_batches_per9024=len({x['batch']for x in rows})/4096*141,
  by_category=dict(collections.Counter(x['attribution_category']for x in rows)),
  first_global_stage=dict(collections.Counter(x['first_incorrect_global_stage']['stage']if x['first_incorrect_global_stage']else'NONE'for x in rows)),
  payload_phase_direction=dict(collections.Counter((x['first_payload_mismatch']['phase']+('/reverse'if x['first_payload_mismatch']['rev']else'/forward'))if x['first_payload_mismatch']else'NONE'for x in rows)))
out=dict(status='ACTUAL FINAL431-WITNESS ATTRIBUTION; DIAGNOSTIC ONLY',source_stream_sha256=declaration['actual_final_stream_sha256'],original_cohort_label=declaration['cohort_label'],
 no_new_sampling=True,exact_original_input_keys_MR_continuation_and_failure_flags_reproduced=True,every_q_b_phase_T_protected_differential=True,
 full_original_batches_replayed=413,context_shots=413*64,target_witnesses=431,
 all=counts(cases),advisory_model_unexplained=counts(unknown),event_counts={k:len(v)for k,v in events.items()},
 marker_coverage={k:binding[k]for k in ['source_markers','admitted_markers','unknown_regions','source_counts','admitted_counts']},
 unmapped_internal_regions=binding['unknown'],
 reports_no_record_or_repair=True,no_candidate_change=True,no_packet_selected_cuts=True,source_proof_files={name:hashlib.sha256((r/name).read_bytes()).hexdigest()for name in ['REPLAY-PREDECLARATION.json','actual-markers.json','runtime-source.json','actual-replay.log']},cases=cases)
(r/'attribution.json').write_text(json.dumps(out,indent=2)+'\n');(r/'model-unexplained55.json').write_text(json.dumps(unknown,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in['cases','unmapped_internal_regions','source_proof_files']},indent=2))
