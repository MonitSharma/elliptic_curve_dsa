"""Classical diagnosis of the SAME failed packet under proposed wider bounds."""
from pathlib import Path
import hashlib,json,shutil,sys
root=Path(sys.argv[1]);original=root/'candidate-control-fold-v6';dest=root/'policy-census-v8';tree=dest/'source/point_add'
shutil.copytree(original/'src/point_add',tree)
p=tree/'frogdrop_sched.rs';s=p.read_text(encoding='utf8')
for name in ['g_hr_ok','g_ht_ok']:s=s.replace('fn '+name+'(','pub(crate) fn '+name+'(')
p.write_text(s,encoding='utf8')
p=tree/'midg.rs';s=p.read_text(encoding='utf8');assert 'pub const TC: usize = 26;' in s;s=s.replace('pub const TC: usize = 26;','pub const TC: usize = 27;');p.write_text(s,encoding='utf8')
p=tree/'pointadd_frogdrop.rs';s=p.read_text(encoding='utf8');assert 'pub const EMAX: usize = 21;' in s;s=s.replace('pub const EMAX: usize = 21;','pub const EMAX: usize = 22;');p.write_text(s,encoding='utf8')
base=(root/'failed-packet-v6-r2-crate/src/main.rs').read_text(encoding='utf8');s=base[:base.index('\nfn main(){')]
s=s.replace(str(root/'failed-packet-v6-r2-crate/source/point_add'),str(tree))
needle='{32}else{24}}else{cp.k}';assert s.count(needle)==1;s=s.replace(needle,'{32}else{25}}else{cp.k}')
s+=r'''
fn main(){
 let a:Vec<_>=std::env::args().collect();let input:serde_json::Value=serde_json::from_slice(&std::fs::read(&a[1]).unwrap()).unwrap();let mut flagged=vec![];let p=point_add::frogdrop_sched::p();
 for packet in input["packets"].as_array().unwrap(){let shot=packet["shot"].as_u64().unwrap();let mut reasons=vec![];
  for division in ["division1","division2"]{let dx=N::from_str_radix(packet[division]["reflected_dx"].as_str().unwrap(),16).unwrap();let result=diagnosis(dx);
   let(mut r,mut t)=(vec![p,dx],vec![N::ZERO,N::from(1u64)]);let mut largest_v2=0usize;while !r.last().unwrap().is_zero(){let n=r.len();let q=r[n-2]/r[n-1];let rn=r[n-2]-q*r[n-1];let tn=t[n-2]+q*t[n-1];r.push(rn);t.push(tn);}
   for value in r.iter().chain(&t){if !value.is_zero(){largest_v2=largest_v2.max(value.trailing_zeros());}}
   if largest_v2>22||!result["candidate_policy_issues"].as_array().unwrap().is_empty()||!result["envelope_check"].is_null(){reasons.push(serde_json::json!({"division":division,"largest_v2":largest_v2,"diagnosis":result}));}
   if [2726,2913,3532].contains(&shot){println!("FIXED_FAILED_CASE_POLICY shot={shot} division={division} largest_v2={largest_v2} issues={} envelope={}",result["candidate_policy_issues"],result["envelope_check"]);}
  }
  if !reasons.is_empty(){flagged.push(serde_json::json!({"shot":shot,"reasons":reasons}));}
 }
 std::fs::write(&a[2],serde_json::to_vec_pretty(&serde_json::json!({"scope":"classical policy only, same failed packet; TC27, K25 large/K32 small, EMAX22; not a circuit or score","flagged":flagged})).unwrap()).unwrap();println!("POLICY_CENSUS_COMPLETE flagged={}",flagged.len());
 for value in flagged{println!("STILL_FLAGGED {value}");}
}
'''
(dest/'src').mkdir(parents=True);(dest/'src/main.rs').write_text(s,encoding='utf8')
cargo=(root/'failed-packet-v6-r2-crate/Cargo.toml').read_text(encoding='utf8').replace('name="q692_failed_packet"','name="q692_policy_census"');(dest/'Cargo.toml').write_text(cargo,encoding='utf8')
(dest/'source-binding.json').write_text(json.dumps(dict(scope='private classical model, not a candidate source change',original_source=str(original),packet=str(root/'failed-v6-packet-r2.json'),packet_sha256=hashlib.sha256((root/'failed-v6-packet-r2.json').read_bytes()).hexdigest(),proposed_TC=27,proposed_EMAX=22,proposed_large_head=25),indent=2)+'\n',encoding='utf8')
