from pathlib import Path
import shutil,json,collections
root=Path(__file__).resolve().parent;old=root/'initial-seed-ordinal-metadata';old.mkdir(exist_ok=False)
for name in ['inventory.py','ALL144.json','ALL70.json','SUMMARY.json']:shutil.copyfile(root/name,old/name)
rows=json.loads((root/'ALL144.json').read_text());seed=[]
for e in rows:
 e['source_row_one_based']=e['row']+1;e['seed_restoration_same_row']=(e['source_row_one_based']==11 and e['legacy_index']==619007 and e['actual_index']==619000)
 if e['seed_restoration_same_row']:assert e['old'][:4]==[13,881,1106,1134]and e['new'][0]==8 and e['new'][2:4]==[1106,1134];seed.append(e)
 e['prior_coverage']='seed_exact_control_restored'if e['seed_restoration_same_row']else'A29_region_overlap_semantic_coverage_not_inferred'if e['A29_old_region_overlap_ticks']else'outside_A29_regions_and_seed'
assert len(seed)==1
markers=json.loads((root/'inputs/actual-markers.json').read_text())['markers'];windows=[]
for before in markers:
 if before['family']!='window'or not before.get('before')or'anchor'not in before:continue
 after=[x for x in markers if x['family']=='window'and x['id']==before['id']and x.get('before')is False and'anchor'in x]
 if len(after)!=1:continue
 span=[before['anchor']['actual_at'],after[0]['anchor']['actual_at']];windows.append({'id':before['id'],'actual_span':span,'inverse':before.get('inv'),'shift':before.get('shift'),'carry_in':before.get('cin')})
reductions=[e for e in rows if e['new']is not None]
for e in reductions:e['square_window_memberships']=[w for w in windows if w['actual_span'][0]<=e['actual_index']<w['actual_span'][1]]
summary=json.loads((root/'SUMMARY.json').read_text());summary.update(seed_same_row=1,outside_A29_and_seed=69,seed_external_row_one_based=11,seed_internal_index=10,seed_ordinal_metadata_corrected=True)
(root/'ALL144.json').write_text(json.dumps(rows,indent=2)+'\n');(root/'ALL70.json').write_text(json.dumps(reductions,indent=2)+'\n');(root/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
selected={'status':'ALL_SOURCE_WINDOWS_AND_REQUESTED_REVERSE127_EXTRACT','all_square_windows':windows,'square_reductions':[e for e in reductions if e['square_window_memberships']],'multiply_reverse127_reductions':[e for e in reductions if any(r['family']=='payload'and r['phase']=='multiply'and r['tick']==127 and r['reverse']for r in e['actual_regions'])]};(root/'REQUESTED-REGIONS.json').write_text(json.dumps(selected,indent=2)+'\n')
print(json.dumps({'seed':[(e['row'],e['source_row_one_based'],e['legacy_index'],e['actual_index'])for e in seed],'square_windows':len(windows),'square_reduction_rows':len(selected['square_reductions']),'multiply_reverse127_rows':len(selected['multiply_reverse127_reductions']),'no_source_gate_or_binding_changed':True}))
