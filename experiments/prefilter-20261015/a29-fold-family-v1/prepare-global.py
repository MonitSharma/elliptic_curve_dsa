from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[1];out=r/'a29-mask-v3';out.mkdir(exist_ok=True)
def put(p,s):p.write_bytes(s.encode())
base=json.loads((r/'a29-mask-v2/candidates-v3.json').read_text())
family=json.loads((r/'a29-fold-family-v1/candidates.json').read_text())
assert family['mapped_shadow']==family['hints']==31 and family['unmapped']==0
base['candidate_shadow_regions']=sorted({tuple(x)for x in base['candidate_shadow_regions']+family['candidate_shadow_regions']},key=lambda x:(x[0],-x[1]))
base['status']='SOURCE_ONLY_CANDIDATES_EACH_ACTUAL_REGION_REQUIRES_FRESH_PROOF_AND_PREFIX_PRECONDITIONS'
base['additional_full_fold_source_family']=family
base['overlap_policy']='Existing selected reset intervals must be disjoint or wholly contained; candidate ends sorted largest-first, no packet or fixture dependence.'
put(out/'candidates.json',json.dumps(base,indent=2)+'\n')
s=(r/'tool/src/bin/a29_rng_mask_v2.rs').read_text(encoding='utf8').replace('../a29_rng_mask_v2_body.rs','../a29_rng_mask_v3_body.rs')
put(r/'tool/src/bin/a29_rng_mask_v3.rs',s)
s=(r/'tool/src/a29_rng_mask_v2_body.rs').read_text(encoding='utf8').replace('a29-mask-v2/candidates-v3.json','a29-mask-v3/candidates.json').replace('a29-mask-v2/mr-mask-a29','a29-mask-v3/mr-mask-a29')
s=s.replace('"old_mask_transfer_used":false,','"old_mask_transfer_used":false,"whole_fold_family_candidate_count":31,')
put(r/'tool/src/a29_rng_mask_v3_body.rs',s)
s=(r/'a29-mask-v2/run-global.sh').read_text(encoding='utf8').replace('a29-mask-v2/global','a29-mask-v3/global').replace('a29-mask-v2/mask.sha256','a29-mask-v3/mask.sha256').replace('a29-mask-v2/mr-mask-a29','a29-mask-v3/mr-mask-a29').replace('a29-mask-v2/candidates-v3.json','a29-mask-v3/candidates.json').replace('a29_rng_mask_v2','a29_rng_mask_v3')
needle='/home/hclau/.cargo/bin/cargo test'
s=s.replace(needle,'/home/hclau/.cargo/bin/cargo build --manifest-path tool/Cargo.toml --release --bin a29_rng_mask_v3 > a29-mask-v3/global.build.log 2>&1 || exit $?\n'+needle)
put(out/'run-global.sh',s)
