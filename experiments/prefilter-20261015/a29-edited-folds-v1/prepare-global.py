from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];out=r/'a29-mask-v4';out.mkdir(exist_ok=True)
def put(p,s):p.write_bytes(s.encode())
original=json.loads((r/'a29-edited-folds-v1/original-candidates.json').read_text())
edited=json.loads((r/'a29-edited-folds-v1/a29-candidates.json').read_text())
for p in [original,edited]:
 assert p['mapped_shadow']==p['hints']==6 and p['unmapped']==0
 assert all(x['prefix_matches']==x['suffix_matches']==x['candidate_pairs']==1 for x in p['rows'])
assert all(x['mapping']['actual_full_region_byte_identical'] for x in edited['rows'])
base=json.loads((r/'a29-mask-v3/candidates.json').read_text())
base['candidate_shadow_regions']=sorted({tuple(x)for x in base['candidate_shadow_regions']+edited['candidate_shadow_regions']},key=lambda x:(x[0],-x[1]))
base['additional_edited_fold_bindings']=dict(raw_to_actual_original=original,actual_original_to_actual_A29=edited)
base['whole_fold_family_candidate_count']=37
base['status']='ALL37_SOURCE_FOLD_CANDIDATES_REQUIRE_FRESH_ACTUAL_GATE_PROOF_AND_PREFIX_PRECONDITIONS'
put(out/'candidates.json',json.dumps(base,indent=2)+'\n')
s=(r/'tool/src/bin/a29_rng_mask_v3.rs').read_text(encoding='utf8').replace('../a29_rng_mask_v3_body.rs','../a29_rng_mask_v4_body.rs')
put(r/'tool/src/bin/a29_rng_mask_v4.rs',s)
s=(r/'tool/src/a29_rng_mask_v3_body.rs').read_text(encoding='utf8').replace('a29-mask-v3/candidates.json','a29-mask-v4/candidates.json').replace('a29-mask-v3/mr-mask-a29','a29-mask-v4/mr-mask-a29').replace('"whole_fold_family_candidate_count":31','"whole_fold_family_candidate_count":37')
put(r/'tool/src/a29_rng_mask_v4_body.rs',s)
s=(r/'a29-mask-v3/run-global.sh').read_text(encoding='utf8').replace('a29-mask-v3','a29-mask-v4').replace('a29_rng_mask_v3','a29_rng_mask_v4')
put(out/'run-global.sh',s)
