from pathlib import Path
import json,re,collections,hashlib
r=Path(__file__).resolve().parent;p=2**256-2**32-977
base=json.loads((r/'attribution.json').read_text());text=(r/'phase-attribution.log').read_text();lines=text.splitlines()
def parse(s):
 v=dict(re.findall(r'(\w+)=([^ ]+)',s));v['line']=s
 for k in ['shot','tick','at']: 
  if k in v:v[k]=int(v[k])
 for k in ['rev','skip']:
  if k in v:v[k]=v[k]=='true'
 if 'tape='in s:v['tape']=[int(x)for x in re.search(r'tape=\[([^\]]*)\]',s)[1].split(',')]
 return v
batch=[parse(s)for s in lines if s.startswith('ATTR_BATCH ')];assert len(batch)==413 and all(x['full64q_b_phase_T_equal']=='true'and x['original_census_flags_reproduced']=='true'for x in batch)
shots=[parse(s)for s in lines if s.startswith('PAY_SHOT ')];assert len(shots)==431 and all(x['final_bad']=='true'and x['observer_equal']=='true'for x in shots)
stages={x['shot']:x for x in map(parse,(s for s in lines if s.startswith('STAGE_EVENT ')))};assert len(stages)==431
assert all(stages[x['shot']]['line']==x['first_incorrect_global_stage']['line']for x in base['cases'])
pay={};parks={}
for s in lines:
 if s.startswith('PAY_EVENT '):
  v=parse(s);key=v['shot'],v['phase'];assert key not in pay;pay[key]=v
 elif s.startswith('PARKED_RAILS '):
  v=parse(s);key=v['shot'],v['phase'];assert key not in parks;parks[key]=v
assert len(parks)==862
for name in ['phase-attribution-stream-before.sha256','phase-attribution-stream-after.sha256']:
 assert(r/name).read_text().split()[0]==base['source_stream_sha256']
n2={x['shot']:x for x in json.loads((r/'N2-DIAGNOSIS.json').read_text())['cases']}
cases=[];newfold=[]
for old in base['cases']:
 if old['model_predicted_wrong_value']:continue
 shot=old['shot'];stage=stages[shot]['stage'];event=pay.get((shot,stage));folds=[]
 if event:
  for f in old['events']['FOLD_BOUNDARY']:
   if(f['phase'],f['tick'],f['rev'])==(event['phase'],event['tick'],event['rev'])and not event['skip']and f['recomputed_low_formula_matches']and int(event['diff'],16)==(-f['candidate_correction_to_full_payload'])%p:folds.append(f)
 if folds:
  category='exact_fold_boundary_loss_at_first_bad_global_stage'
  if not old['matched_fold_boundary_losses']:newfold.append(shot)
 elif stage=='square'and old['exact_square_window_losses']:category='exact_square_window_loss'
 elif shot in n2:
  assert stage=='divide'and event['tick']==131
  actual=parks[shot,'divide'];assert [int(actual[k])for k in ['r0','r1']]==n2[shot]['parked_signed6bit_rails'];category='exact_N2_dirty_carry_first_add'
 else:category='unresolved_first_bad_global_stage'
 cases.append(dict(shot=shot,batch=shot//64,lane=shot%64,first_bad_global_stage=stage,first_PAY_in_that_phase=event,earlier_wholecircuit_PAY=old['first_payload_mismatch'],matched_fold_losses=folds,
  parked_rails={phase:{k:parks[shot,phase][k]for k in ['at','r0','r1','clean0','clean1']}for phase in ['divide','multiply']},category=category,
  old_category=old['attribution_category'],square_losses=old['exact_square_window_losses']))
assert len(cases)==55 and len(newfold)==8
counts=collections.Counter(x['category']for x in cases);assert counts=={'exact_fold_boundary_loss_at_first_bad_global_stage':34,'exact_square_window_loss':3,'exact_N2_dirty_carry_first_add':14,'unresolved_first_bad_global_stage':4}
fold_split=collections.Counter(f['phase']for x in cases for f in x['matched_fold_losses']);assert fold_split=={'divide':13,'multiply':21}
out=dict(status='TERMINAL PER-PHASE ACTUAL-FINAL ATTRIBUTION ADDENDUM; NO REPAIR',source_stream_sha256=base['source_stream_sha256'],same431_witnesses_413_original_contexts_26432_shots=True,every_original_q_b_phase_T_and_census_failure_mask_equal=True,no_new_sampling=True,no_candidate_change=True,
 limitation_corrected='an earlier local interface mismatch at divide137(skip) can cancel before correct divide output and hide a later multiply mismatch under the old wholecircuit first-event latch. Both observer logs preserved; this addendum uses first-event PERactualsourcephase.',
 advisory_category=dict(shots=55,batches=54,fixed4096_cohort_lambda=54/4096*141,not_a_universal_floor=True),by_observed_mechanism=dict(counts),exact_fold_split=dict(fold_split),newly_unhidden_reverse_fold_shots=newfold,remaining_unresolved_shots=[x['shot']for x in cases if x['category']=='unresolved_first_bad_global_stage'],
 parked_snapshots=862,all431_cases_have_same_first_incorrect_global_stage=True,source_code_declaration=json.loads((r/'PHASE-REPLAY-DECLARATION.json').read_text()),phase_log_sha256=hashlib.sha256((r/'phase-attribution.log').read_bytes()).hexdigest(),cases=cases)
(r/'PHASE-ATTRIBUTION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if k not in['cases','source_code_declaration']},indent=2))
