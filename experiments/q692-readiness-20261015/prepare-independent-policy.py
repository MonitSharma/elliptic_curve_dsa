"""Fixed independent arithmetic-domain audit. Every flagged input is retained."""
from pathlib import Path
import hashlib,json,shutil,sys
root=Path(sys.argv[1]);source=root/'candidate-repair-v9';dest=root/'independent-policy-v9';tree=dest/'source/point_add';shutil.copytree(source/'src/point_add',tree)
p=tree/'frogdrop_sched.rs';s=p.read_text(encoding='utf8')
for name in ['g_hr_ok','g_ht_ok']:s=s.replace('fn '+name+'(','pub(crate) fn '+name+'(')
p.write_text(s,encoding='utf8')
base=(root/'failed-packet-v6-r2-crate/src/main.rs').read_text(encoding='utf8');program=base[:base.index('\nfn main(){')].replace(str(root/'failed-packet-v6-r2-crate/source/point_add'),str(tree));needle='{32}else{24}}else{cp.k}';assert program.count(needle)==1;program=program.replace(needle,'{32}else{25}}else{cp.k}')
program+=r'''
fn main(){
 let args:Vec<_>=std::env::args().collect();let p=point_add::frogdrop_sched::p();let mut h=Shake256::default();h.update(b"q692-independent-arithmetic-domain-audit-v1");let mut reader=h.finalize_xof();let mut flagged=vec![];let mut policy_failures=0;let mut envelope_failures=0;let mut v2_failures=0;
 for index in 0..50000{
  let mut bytes=[0u8;32];XofReader::read(&mut reader,&mut bytes);let x=wide(U256::from_le_bytes(bytes))%(p/N::from(2u64))+N::from(1u64);let result=diagnosis(x);
  let(mut r,mut t)=(vec![p,x],vec![N::ZERO,N::from(1u64)]);while !r.last().unwrap().is_zero(){let n=r.len();let q=r[n-2]/r[n-1];r.push(r[n-2]-q*r[n-1]);t.push(t[n-2]+q*t[n-1]);}let largest=r.iter().chain(&t).filter(|v|!v.is_zero()).map(|v|v.trailing_zeros()).max().unwrap();
  let policy_bad=!result["candidate_policy_issues"].as_array().unwrap().is_empty();let envelope_bad=!result["envelope_check"].is_null();let v2_bad=largest>23;
  policy_failures+=usize::from(policy_bad);envelope_failures+=usize::from(envelope_bad);v2_failures+=usize::from(v2_bad);
  if policy_bad||envelope_bad||v2_bad{flagged.push(serde_json::json!({"fixed_independent_index":index,"largest_v2":largest,"diagnosis":result}));}
 }
 let report=serde_json::json!({"scope":"fixed 50000 independent arithmetic inputs; classical policy diagnosis only; TC27/K25-large/K32-small/EMAX23; not curve-point execution or a score; every flagged input retained","inputs":50000,"policy_failure_inputs":policy_failures,"envelope_failure_inputs":envelope_failures,"conservative_v2_failure_inputs":v2_failures,"flagged":flagged});std::fs::write(&args[1],serde_json::to_vec_pretty(&report).unwrap()).unwrap();println!("INDEPENDENT_POLICY_COMPLETE inputs=50000 policy_failures={policy_failures} envelope_failures={envelope_failures} conservative_v2_failures={v2_failures}");
}
'''
(dest/'src').mkdir(parents=True);(dest/'src/main.rs').write_text(program,encoding='utf8');(dest/'Cargo.toml').write_text((root/'failed-packet-v6-r2-crate/Cargo.toml').read_text(encoding='utf8').replace('name="q692_failed_packet"','name="q692_independent_policy"'),encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='independent fixed-seed arithmetic policy only; every failure retained',candidate=str(source),source_sha256={p.relative_to(source).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((source/'src/point_add').rglob('*'))if p.is_file()},driver_sha256=hashlib.sha256((dest/'src/main.rs').read_bytes()).hexdigest(),seed='q692-independent-arithmetic-domain-audit-v1',inputs=50000),indent=2)+'\n',encoding='utf8')
