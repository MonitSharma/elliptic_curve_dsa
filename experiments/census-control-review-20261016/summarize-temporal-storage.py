from pathlib import Path
import json,bisect,hashlib
r=Path('/home/hclau/ecdsa_research/n2-temporal-storage-20261016');p=r/'RESULT.json';x=json.loads(p.read_text());rows=[]
for f in x['phases']:
 c=f['optimistic_core_capacity'];events=[v['first_any_touch']['at']for v in f['all8slot_first_events']if not v['prefix_exact_zero']];assert len(events)==6;segments=c['segments'];starts=[s[0]for s in segments];points=sorted({v for s in segments for v in s[:2]}|set(events));gaps=[]
 for a,b in zip(points,points[1:]):
  if a<c['start']or a>=c['end']:continue
  cap=segments[bisect.bisect_right(starts,a)-1][2];demand=sum(e<=a for e in events)
  if cap<demand:
   if gaps and gaps[-1]['end']==a and gaps[-1]['capacity']==cap and gaps[-1]['separate_slot_demand']==demand:gaps[-1]['end']=b
   else:gaps.append(dict(start=a,end=b,capacity=cap,separate_slot_demand=demand,shortfall=demand-cap))
 steady=[s[2]for s in segments if s[1]>max(events)];initial=[s[2]for s in segments if s[0]==c['start']][0]
 rows.append(dict(phase=f['phase'],full_interval=[f['full_start'],f['full_end']],optimistic_core=[c['start'],c['end']],hole_intervals=len(f['holes']),initial_clean_hole_capacity=initial,minimum_core_capacity=c['minimum'],maximum_core_capacity=c['maximum'],first6_boundary=c['first_possible6_separate_slot_bank_boundary'],first_nonconstant_slot_touch=min(events),all6_original_nonconstant_slots_first_touched_by=max(events),minimum_capacity_after_all6_touched=min(steady),below6_epochs=len(c['epochs_below6']),first_below6_epoch=c['epochs_below6'][0]if c['epochs_below6']else None,gradual_start_demand_gaps=len(gaps),first_gradual_start_violation=gaps[0]if gaps else None,maximum_shortfall=max((g['shortfall']for g in gaps),default=0),all_gradual_start_violations=gaps))
out=dict(status='NEGATIVE FOR SEPARATE-SLOT TRANSPORT THROUGH STRICT UNCONDITIONAL-MR HOLES',result_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),all2loans_all16source_slots=True,zero_only_after_unconditional_MR=True,every_quantum_read_write_phase_is_fence=True,all_original_and_returned_loan_slots_excluded=True,phases=rows,conclusion='Both phases have zero temporal hole capacity after all six nonconstant source slots have been touched. Even gradually moving each bit only before its first use violates capacity. Free SWAP/CX moves among these holes cannot by themselves retain six separate slots for the entire source loan.',limitations=['Six separate slots are not a proof of six independent information bits.','No claim excludes compression, dirty-compatible arithmetic during gaps, broader zero proofs, or reuse of excluded loan slots.','No arithmetic transformation, candidate, sampling or profit claim. Stop this fixed ordinary-liveness feasibility front.'])
(r/'SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({**out,'phases':[{k:v for k,v in p.items()if k!='all_gradual_start_violations'}for p in rows]},indent=2))
