"""Read-only highest-wire coverage screen before any ancilla-leasing rewrite."""
from pathlib import Path
import hashlib,json,shutil
ws=Path(__file__).resolve().parent.parent;r=ws/'product-lease-footprint-20261020';assert not r.exists();r.mkdir()
shutil.copy2(ws/'product-copy-cache-20261019/io.rs',r/'io.rs')
(r/'footprint.rs').write_text('''mod io;
use quantum_ecc::circuit::{Op,OperationType as K};
use sha3::{Digest,Sha3_256};
use std::collections::{BTreeMap,BTreeSet};
const NO:u64=u64::MAX;
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn footprint(v:&[Op])->serde_json::Value{
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let top=nq-1;
 let abi:BTreeSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=NO).map(|o|o.q_target.0 as usize).collect();
 let mut touches=vec![vec![];nq];for(i,o)in v.iter().enumerate(){let mut qs=[o.q_control1.0,o.q_control2.0,o.q_target.0];qs.sort_unstable();for(j,q)in qs.into_iter().enumerate(){if q!=NO&&(j==0||q!=qs[j-1]){touches[q as usize].push(i);}}}
 let(mut depth,mut outer)=(0usize,0usize);let mut first=None;let mut begin=0;let mut epochs=vec![];let mut total=0usize;let mut covered=0usize;let mut kinds=BTreeMap::<u32,usize>::new();
 for(i,o)in v.iter().enumerate(){
  if o.kind==K::PushCondition{if depth==0{outer=i;}depth+=1;continue;}
  if o.kind==K::PopCondition{assert!(depth>0);depth-=1;continue;}
  let touched=[o.q_control1.0,o.q_control2.0,o.q_target.0].contains(&(top as u64));if !touched{continue;}
  total+=1;*kinds.entry(o.kind as u32).or_default()+=1;
  if first.is_none(){first=Some(i);begin=if depth==0{i}else{outer};}
  if matches!(o.kind,K::R|K::Hmr)&&o.q_target.0==top as u64&&depth==0&&o.c_condition.0==NO{
   let start=first.take().unwrap();let mut donors=vec![];
   for(q,positions)in touches.iter().enumerate(){if q==top||abi.contains(&q){continue;}let at=positions.partition_point(|&x|x<begin);if at==positions.len()||positions[at]>i{donors.push(serde_json::json!({"q":q,"previous_touch":at.checked_sub(1).map(|j|positions[j]),"next_touch":positions.get(at).copied()}));}}
   let count=touches[top].partition_point(|&x|x<=i)-touches[top].partition_point(|&x|x<start);covered+=count;
   epochs.push(serde_json::json!({"first_high_wire_touch":start,"window_start_outside_scope":begin,"window_end_reset":i,"touches":count,"window_ops":i-begin+1,"closing_reset_kind":o.kind as u32,"untouched_nonABI_donors":donors}));
  }
 }
 assert_eq!(depth,0);assert_eq!(total,touches[top].len());
 serde_json::json!({"status":"HIGHEST_WIRE_TEMPORARY_COMPRESSION_FOOTPRINT_DIAGNOSTIC","source_ops":v.len(),"source_Q":nq,"target_high_wire":top,"target_is_ABI":abi.contains(&top),"registered_quantum_wires":abi.len(),"high_wire_touches":total,"touch_kinds":kinds,"unconditional_reset_closed_epochs":epochs,"covered_high_wire_touches":covered,"trailing_unclosed_first_touch":first,"all_touches_closed_by_unconditional_reset":covered==total,"scope":"Only static quantum-touch/scoped-reset coverage. Donor states unknown; no equivalence, width saving, circuit, census, nonce or score. Conditional clean epochs are not assumed."})
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let v=io::load_ops(&a[1]);assert_eq!(hash(&v),a[3]);let result=footprint(&v);std::fs::write(&a[2],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{}",serde_json::json!({"target":result["target_high_wire"],"touches":result["high_wire_touches"],"epochs":result["unconditional_reset_closed_epochs"].as_array().unwrap().len(),"all_closed":result["all_touches_closed_by_unconditional_reset"]}));}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::{QubitId,BitId};
 fn op(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o}
 fn qr(q:u64)->Op{let mut o=op(K::AppendToRegister,NO,NO,q);o.r_target.0=0;o}
 #[test]fn all_roles_and_phase_touches_exclude_donors(){let v=vec![qr(0),op(K::X,NO,NO,4),op(K::CCZ,1,2,3),op(K::R,NO,NO,4)];let r=footprint(&v);let e=&r["unconditional_reset_closed_epochs"][0];let donors=e["untouched_nonABI_donors"].as_array().unwrap();assert!(donors.is_empty());assert_eq!(e["touches"],2);assert_eq!(r["covered_high_wire_touches"],2);}
 #[test]fn scope_expands_window_and_abi_is_excluded(){let mut push=op(K::PushCondition,NO,NO,NO);push.c_condition=BitId(0);let v=vec![qr(0),op(K::X,NO,NO,1),push,op(K::X,NO,NO,4),op(K::PopCondition,NO,NO,NO),op(K::R,NO,NO,4)];let r=footprint(&v);let e=&r["unconditional_reset_closed_epochs"][0];assert_eq!(e["window_start_outside_scope"],2);assert_eq!(e["first_high_wire_touch"],3);assert!(e["untouched_nonABI_donors"].as_array().unwrap().iter().any(|x|x["q"]==1));assert!(!e["untouched_nonABI_donors"].as_array().unwrap().iter().any(|x|x["q"]==0));}
 #[test]fn conditional_reset_never_closes_an_arbitrary_epoch(){let mut reset=op(K::R,NO,NO,4);reset.c_condition=BitId(0);let v=vec![op(K::X,NO,NO,4),reset];let r=footprint(&v);assert_eq!(r["all_touches_closed_by_unconditional_reset"],false);assert_eq!(r["covered_high_wire_touches"],0);assert_eq!(r["trailing_unclosed_first_touch"],0);}
 #[test]fn disjoint_closed_epochs_cover_every_high_wire_event(){let v=vec![qr(0),op(K::X,NO,NO,4),op(K::R,NO,NO,4),op(K::CX,0,NO,4),op(K::Hmr,NO,NO,4)];let r=footprint(&v);assert_eq!(r["unconditional_reset_closed_epochs"].as_array().unwrap().len(),2);assert_eq!(r["high_wire_touches"],4);assert_eq!(r["all_touches_closed_by_unconditional_reset"],true);}
}
''',newline='\n')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
base=json.loads((ws/'product-linear-witness-controls-v2-20261020/RESULT.json').read_text())['compiler_and_dependencies']
(r/'BINDING.json').write_text(json.dumps({'source_files':{p.name:sha(p) for p in r.glob('*.rs')},'compiler_and_direct_dependencies':base,'input_compressed_sha256':'26dc60ee329a6cf448143eebc9f1f218efd73ffeaaef92213a75e7d31f3e7cc1','input_raw_sha3_256':'d343ca717c726c9136505edb1ba3602a58f7bfe063151d8a9e82b4f39d71a6a5','scope':'Read-only footprint with fixed highest-wire target and four controls, no emitted circuit or statistical gate.'},indent=2)+'\n')
s=(ws/'product-linear-witness-controls-v2-20261020/evidence/run.py').read_text()
s=s.replace("args+['--test','anf.rs'", "args+['--test','footprint.rs'").replace("assert '30 passed; 0 failed'", "assert '4 passed; 0 failed'")
start=s.index("(r/'RESULT.json').write_text")
s=s[:start]+'''with (r/'build.log').open('xb') as f:subprocess.run(args+['footprint.rs','-o','footprint.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
inp=ws/'product-copy-cache-native-20261020/candidate/ops.bin';assert sha(inp)==b['input_compressed_sha256']
with (r/'screen.log').open('xb') as f:subprocess.run(['/usr/bin/time','-v','./footprint.bin',str(inp),str(r/'FOOTPRINT.json'),b['input_raw_sha3_256']],stdout=f,stderr=subprocess.STDOUT,check=True)
assert sha(inp)==b['input_compressed_sha256']
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_HIGHEST_WIRE_FOOTPRINT_COMPLETED','tests':4,'input_sha256':sha(inp),'footprint_sha256':sha(r/'FOOTPRINT.json'),'binary_sha256':sha(r/'footprint.bin'),'source_files':b['source_files'],'compiler_and_dependencies':b['compiler_and_direct_dependencies'],'circuit_emitted':False,'gate_or_nonce_or_score':False},indent=2)+'\\n')
print('Read-only footprint finished; no circuit or width claim',flush=True)
'''
(r/'run.py').write_text(s,newline='\n')
for name in ['run.sh','launch.py']:
 s=(ws/'product-linear-witness-controls-v2-20261020/evidence'/name).read_text().replace('product-linear-witness-controls-v2-20261020','product-lease-footprint-20261020');(r/name).write_text(s,newline='\n')
(r/'.gitignore').write_text('/*.bin\n')
(r/'STATUS.md').write_text('''# Read-only top-wire leasing footprint

Declared before launch,20 October2026. Parent frozen copy-cache raw d343ca71…,
17,889,637 operations, current own census untouched. Fixed target highest
qubit1233. Find all scope-expanded epochs closed by unconditional depth0 reset,
quantum/phase/ABI touches and static untouched non-ABI donor candidates.
Conditional cleanups are unknown at this first lexical screen. Never infer a
donor is zero or has a recomputable value from inactivity. No operations are
emitted or changed. Four boundary/coverage controls before full input scan.
This diagnostic only decides what exact clean/provenance analysis is needed
next; it cannot establish a width improvement or rule out richer leasing.
One server CPU/12GiB, source/compiler/direct dependencies/input hashes bound.
''')
print('Prepared read-only highest-wire footprint and four controls; no launch')
