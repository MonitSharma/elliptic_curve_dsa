"""Declare and prepare ALL74 original CCXs, keeping all70 reductions unchanged."""
from pathlib import Path
import hashlib,json,subprocess,shutil
r=Path(__file__).resolve().parent;d=r/'all74-cache67-20261016';d.mkdir(exist_ok=True);b=r.parent;tip=b/'product-exact-20261015/tip';tree=r/'candidate-all74-base';base='4b2ec52fc55da796aa8f5ef851290297e8706424';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(r/'PRODUCT67_FREEZE.json')=='30922550c7301a745bb7d611a2b20e38a9f58121e37f8ccdaf5e5073eae4471c'
stages=json.loads((r/'PRODUCT67_FREEZE.json').read_text())['stages'];assert len(stages)==67
inventory=b/'census-deletion-family-20261016';assert sha(inventory/'source-only-v1.tar.gz')=='93e34a44b9ab8e93e162838471a10b19ccbeb38758ebbf484f9ff46958d745e6'
rows=json.loads((inventory/'ALL74.json').read_text());assert len(rows)==74 and all(e['old'][0]==13 and e['action']=='del' for e in rows)
plan=dict(status='PREDECLARED_BEFORE_ANY_BUILD_OR_GENERATION',base_revision=base,family='ALL74 inherited deletion rows uniformly retain exact original CCXs. All70 CX reductions and every other pass/table/anchor retained. No A29, no selected seven-row subset.',all74_inventory_sha256=sha(inventory/'ALL74.json'),all144_source_data_sha256=sha(b/'census-control-review-20261016/census_cut_data.txt'),original_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',before_census_stream_sha256='4b603d502456f8db2145ac5f7c36c9b44f496acfd0c3c5cc3149006cbc51a310',required_Q=1234,added_Q_MR_B=[0,0,0],added_executed_T_per_shot_bounds=[59,74],syntactic_depth_weight_T=66.5,syntactic_proxy_not_measured_mean=True,stages=stages,stage_count=67,recipe_freeze_sha256=sha(r/'PRODUCT67_FREEZE.json'),cache_rule='Fresh leases, independent zero/product/function/phase proofs at every stage; no old certificate/mask transfer',diagnostic_checkpoints=[25,67],sole_final_fresh_gate=dict(parent='original4b',label='product-all74-fixed67-independent-20261016-v1',first_batch=0,batches_per_source=32768,shots_per_batch=64,requirements=['candidate failed batches <= parent','candidate lambda <=18','candidate dirty=0','Q=1234','all rows retained'],no_interim_selection=True,no_resampling=True),resources=dict(build_cores=2,generation_proof_cores=1,generation_address_GiB=24),no_nonce_or_search=True,no_global_arithmetic_or_monotone_failure_claim=True,primitive_contract='Each restored CCX is the exact original reversible arbitrary-dirty target permutation, with no phase multiplier; whole-family failure behavior remains an empirical gate.')
assert not(d/'DECLARATION.json').exists();(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(tree),base],check=True)
p=tree/'src/point_add/census_cut.rs';s=p.read_text();old='None if f[6] == "del" => { n_del += 1; vec![] }';new='None if f[6] == "del" => { assert_eq!(kind, K::CCX, "ALL74 family is CCX only"); n_del += 1; vec![o] }';assert s.count(old)==1;s=s.replace(old,new)
old='if !rep.is_empty() { n_red += 1; for r in &rep { r.validate(); } }';new='if !rep.is_empty() { if f[6] != "del" { n_red += 1; } for r in &rep { r.validate(); } }';assert s.count(old)==1;s=s.replace(old,new)
needle='    let w1 = static_t(&ops);';assert s.count(needle)==1;s=s.replace(needle,'    assert_eq!((rows.len(), n_del, n_red, n_blk), (144, 74, 70, 0), "complete ALL74 restore / ALL70 reductions required");\n'+needle)
s=s.replace('deleted={} reduced={} blocks={}','restored_original_deleted_CCX={} retained_reductions={} blocks={}')
s+='''
#[cfg(test)] mod all74_uniform_tests {
 use super::*;
 #[test] fn complete_source_family() {
  let r=rows();assert_eq!(r.len(),144);let deleted:Vec<_>=r.iter().filter(|(_,f)|f[6]=="del").collect();assert_eq!(deleted.len(),74);
  assert!(deleted.iter().all(|(_,f)|f[1]=="ccx"));let reduced:Vec<_>=r.iter().filter(|(_,f)|f[6]!="del").collect();assert_eq!(reduced.len(),70);assert!(reduced.iter().all(|(_,f)|f[1]=="ccx"&&f[6].starts_with("cx:")));
 }
 #[test] fn restored_ccx_arbitrary_dirty_target_permutation() {
  for a in [false,true] {for b in [false,true] {for t in [false,true] {for enabled in [false,true] {let after=t^(enabled&&a&&b);assert_eq!(after^(enabled&&a&&b),t);}}}}
 }
}
''';p.write_text(s)
(d/'base-source.patch').write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']))
files={str(p.relative_to(tree/'src/point_add')):sha(p)for p in(tree/'src/point_add').rglob('*')if p.is_file()};(d/'base-source-files.json').write_text(json.dumps(files,indent=2)+'\n');shutil.copytree(tree/'src/point_add',d/'base-point-add-source');print(json.dumps(dict(status='SOURCE_PREPARED_AFTER_DECLARATION',tree=str(tree),patch_sha256=sha(d/'base-source.patch'),declaration_sha256=sha(d/'DECLARATION.json'))),flush=True)
