"""Prepare an isolated, exact recomputation-versus-width research experiment."""
import hashlib, json, shutil, urllib.request
from datetime import datetime, timezone
from pathlib import Path
r=Path(__file__).resolve().parent
out=r.parent/'product-width-tradeoff-20261019'
out.mkdir(exist_ok=False)
api='https://api.ecdsa.fail/api/benchmarks/1ffb695a-309b-46b6-a728-2f97d8c7be74/submissions'
data=urllib.request.urlopen(api,timeout=60).read();(out/'public-submissions.json').write_bytes(data)
rows=json.loads(data)['submissions']
eligible=[x for x in rows if (x.get('status')=='accepted' or (x.get('status')=='rejected' and x.get('rejectionReason')=='score did not improve current best')) and isinstance(x.get('officialScore'),int) and x['officialScore']>0 and x['officialScore']==(x.get('officialMetrics') or {}).get('qubits',0)*(x.get('officialMetrics') or {}).get('toffoli',0)]
leader=min(eligible,key=lambda x:x['officialScore'])
assert leader['id']=='9dc3798c-93e0-4da4-a6a9-37586737c4af','Refresh source plan if public parent changed'
(out/'public-parent.json').write_text(json.dumps(leader,indent=2)+'\n')
source=(r/'unwrap.rs').read_text()
source=source.replace('read:Option<(usize,u64)>','reads:Vec<(usize,u64)>').replace('read:None','reads:vec![]')
source=source.replace('ep.read.is_some()','!ep.reads.is_empty()').replace('ep.read.is_none()','ep.reads.len()<64')
source=source.replace('ep.read=Some((i,o.q_target.0));','ep.reads.push((i,o.q_target.0));')
old='let phase=f.phase.unwrap();let (read,target)=f.ep.read.unwrap();let indices=[f.ep.start,read,f.end,phase];if indices.iter().any(|i|occupied.contains(i)){continue;}'
new='let phase=f.phase.unwrap();let mut indices=vec![f.ep.start,f.end,phase];indices.extend(f.ep.reads.iter().map(|r|r.0));if indices.iter().any(|i|occupied.contains(i)){continue;}'
assert source.count(old)==1;source=source.replace(old,new)
old='occupied.extend(indices);deletions.extend([f.ep.start,f.end,phase]);let mut replacement=f.ep.fill;replacement.q_target=QubitId(target);replacement.c_condition=BitId(no);replacement.validate();replacements.insert(read,replacement);'
new='occupied.extend(indices);deletions.extend([f.ep.start,f.end,phase]);let mut moved=vec![];for &(read,target) in &f.ep.reads{let mut replacement=f.ep.fill;replacement.q_target=QubitId(target);replacement.c_condition=BitId(no);replacement.validate();replacements.insert(read,replacement);moved.push(serde_json::json!({"read":read,"target":target}));}'
assert source.count(old)==1;source=source.replace(old,new)
old='"fill":f.ep.start,"read":read,"hmr":f.end,"phase":phase,"donor":f.ep.fill.q_target.0,"replacement":[replacement.kind as u64,replacement.q_control2.0,replacement.q_control1.0,replacement.q_target.0,replacement.c_target.0,replacement.c_condition.0,replacement.r_target.0]'
new='"fill":f.ep.start,"reads":moved,"hmr":f.end,"phase":phase,"donor":f.ep.fill.q_target.0,"fill_kind":f.ep.fill.kind as u64,"control1":f.ep.fill.q_control1.0,"control2":f.ep.fill.q_control2.0,"additional_toffoli":if f.ep.fill.kind==K::CCX{f.ep.reads.len()-1}else{0}'
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace('"expected_toffoli_change":0','"predicted_additional_toffoli":certificates.iter().map(|v|v["additional_toffoli"].as_u64().unwrap()).sum::<u64>()')
source=source.replace('EXACT_SYMBOLIC_UNWRAPPING_ONLY','EXACT_MULTI_READ_RECOMPUTATION_DIAGNOSTIC')
needle='#[test]fn unwrap_proves_only_isolated_repaired_measurements()'
assert source.count(needle)==1
extra=r'''
 #[test]fn two_reads_are_retained_and_third_control_change_rejected(){
  let n=u64::MAX;let mut a=Algebra{next:5,products:HashMap::new(),cap:128,truncations:0};
  let mut q=vec![vec![1],vec![2],vec![],vec![3],vec![4]];let mut c=vec![vec![]];
  let mut w=Unwrapper{active:vec![None;5],finished:vec![],bits:HashMap::new(),inputs:HashSet::new()};
  let fill=make(K::CCX,0,1,2,n,n);w.observe(0,&fill,&vec![0],&q,&c,&mut a);q[2]=a.and(&q[0],&q[1]);
  for (i,t) in [(1,3),(2,4)]{let x=make(K::CX,n,2,t,n,n);w.observe(i,&x,&vec![0],&q,&c,&mut a);q[t as usize]=a.xor(&q[t as usize],&q[2]);}
  assert_eq!(w.active[2].as_ref().unwrap().reads.len(),2);
  let mut bad=w.active[2].clone();assert!(bad.is_some());
  let h=make(K::Hmr,n,n,2,0,n);w.observe(3,&h,&vec![0],&q,&c,&mut a);q[2]=vec![];c[0]=a.fresh();
  let z=make(K::CZ,n,0,1,n,0);w.observe(4,&z,&c[0].clone(),&q,&c,&mut a);assert!(w.finished[0].valid&&w.finished[0].phase.is_some());
  w.active[2]=bad.take();q[0]=a.fresh();let x=make(K::CX,n,2,3,n,n);w.observe(5,&x,&vec![0],&q,&c,&mut a);assert!(w.active[2].is_none());
 }
'''
source=source.replace(needle,extra+'\n '+needle)
(out/'tradeoff.rs').write_text(source)
shutil.copyfile(r/'io.rs',out/'io.rs')
shutil.copyfile(r/'width_pressure.rs',out/'width_pressure.rs')
cargo=(r/'Cargo.toml').read_text().split('[[bin]]')[0].replace('product_pareto_exact','product_width_tradeoff')
(out/'Cargo.toml').write_text(cargo+'\n[[bin]]\nname="tradeoff"\npath="tradeoff.rs"\n[[bin]]\nname="width_pressure"\npath="width_pressure.rs"\n[profile.release]\nopt-level=3\n')
plan={'declared_utc':datetime.now(timezone.utc).isoformat(),'public_parent':leader['id'],
 'input':str(r/'parent/ops.bin'),'input_sha256':'99edb1d39f94c40752cb1fa2581dd2b13fe17696c486f542b8d43c1af1974683',
 'hypothesis':'Trade bounded extra exact AND recomputation for shorter ancilla lifetimes; inspect current public source after removing multi-use caches, unlike the prior no-cost relabeling test.',
 'fixed_discovery_settings':{'expression_cap':1024,'maximum_reads_per_cache':64},
 'one_qubit_break_even_extra_T':(leader['officialScore']-1)//1233-leader['officialMetrics']['toffoli'],
 'screen':'Compare conservative lifetime peaks before and after complete proven cache removal; stop or narrow to a minimum-cost removal set. No statistical gate or nonce search in this experiment.',
 'not_a_resource_record':True,'memory_limit_GiB':64,'build_threads':4,'scanner_threads':1}
(out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(out/'SOURCE-MANIFEST.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()},indent=2)+'\n')
print(json.dumps(plan,indent=2),flush=True)
