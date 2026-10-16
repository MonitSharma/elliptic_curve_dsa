"""Uniformly retain all inherited reduced controls; retain all deletion rows."""
from pathlib import Path
import hashlib,json,subprocess,shutil
r=Path(__file__).resolve().parent;d=r/'all70-cache67-20261016';d.mkdir(exist_ok=True)
tree=r/'candidate-all70-base';base='4b2ec52fc55da796aa8f5ef851290297e8706424'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inventory=r.parent/'census-control-family-20261016'
assert sha(inventory/'ALL70.json')=='453e32f606d5dfaabbf12b4c7714c1cc986c5a6bdd534de3c76b123837d977d7'
stages=json.loads((r/'PRODUCT67_FREEZE.json').read_text())['stages'];assert len(stages)==67
plan={'status':'PREDECLARED_BEFORE_NATIVE_GENERATION','base_revision':base,'family':'ALL70 CCX-to-CX census reductions uniformly retain original CCX; ALL74 deletion rows unchanged; original tables/anchors/checks unchanged; no A29 mix','inventory_sha256':sha(inventory/'ALL70.json'),'original_stream_sha256':'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e','added_Q_MR_B':[0,0,0],'added_executed_T_per_shot_bounds':[56,70],'syntactic_depth_weight_T':63,'stages':stages,'stage_count':67,'cache_rule':'All leases and independent universal proofs derived freshly from changed input at every stage; no old equivalence certificate reused','diagnostic_checkpoints':[25,67],'sole_final_fresh_gate':{'parent':'original4b','label':'product-all70-fixed67-independent-20261016-v1','first_batch':0,'batches_per_source':32768,'shots_per_batch':64,'requirements':['candidate failed batches <= parent','lambda <=18','dirty=0'],'no_interim_selection':True,'no_resampling':True},'resources':{'generation_proof_cores':1,'build_cores':2,'generation_address_GiB':24},'search_authority':False}
assert not (d/'DECLARATION.json').exists();(d/'DECLARATION.json').write_text(json.dumps(plan,indent=2)+'\n')
subprocess.run(['git','-C',str(r/'tip'),'worktree','add','--detach',str(tree),base],check=True)
p=tree/'src/point_add/census_cut.rs';s=p.read_text();old='Some(("cx", a)) if kind == K::CCX => { x.kind = K::CX; x.q_control1 = QubitId(w(a)); x.q_target = o.q_target; vec![x] }'
new='Some(("cx", a)) if kind == K::CCX => { assert!(w(a) == o.q_control1.0 || w(a) == o.q_control2.0, "restored control must be original"); vec![o] }'
assert s.count(old)==1;s=s.replace(old,new)
old='x.kind = K::CZ; x.q_control1 = QubitId(w(a)); x.q_target = QubitId(w(b)); vec![x]'
assert s.count(old)==1;s=s.replace(old,'assert!(a != b); panic!("ALL70 source family contains CCX reductions only")')
needle='    let w1 = static_t(&ops);';assert s.count(needle)==1;s=s.replace(needle,'    assert_eq!((rows.len(), n_del, n_red, n_blk), (144, 74, 70, 0), "complete ALL70 family required");\n'+needle)
s=s.replace('reduced={} blocks={}','retained_original_controls={} blocks={}')
s+='''
#[cfg(test)] mod all70_uniform_tests {
 use super::*;
 #[test] fn fixed_source_family_is_complete() {
  let r=rows();assert_eq!(r.len(),144);assert_eq!(r.iter().filter(|(_,f)|f[6]=="del").count(),74);
  let reds:Vec<_>=r.iter().filter(|(_,f)|f[6]!="del").collect();assert_eq!(reds.len(),70);
  assert!(reds.iter().all(|(_,f)|f[1]=="ccx"&&f[6].starts_with("cx:")));
 }
 #[test] fn retained_ccx_arbitrary_dirty_target_truth_table() {
  for a in [false,true] {for b in [false,true] {for t in [false,true] {for enabled in [false,true] {
   let after=t^(enabled&&a&&b);assert_eq!(after^ (enabled&&a&&b),t);
  }}}}
 }
}
''';p.write_text(s)
(d/'base-source.patch').write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','HEAD','--','src/point_add']))
files={str(p.relative_to(tree/'src/point_add')):sha(p) for p in (tree/'src/point_add').rglob('*') if p.is_file()};(d/'base-source-files.json').write_text(json.dumps(files,indent=2)+'\n')
shutil.copytree(tree/'src/point_add',d/'base-point-add-source')
print(json.dumps({'status':'SOURCE_PREPARED','tree':str(tree),'patch_sha256':sha(d/'base-source.patch')}),flush=True)
