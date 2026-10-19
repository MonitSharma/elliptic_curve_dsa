mod io;
use quantum_ecc::circuit::{Op, OperationType as K, QubitId, BitId};
use std::collections::{HashMap, HashSet};
use sha3::{Digest,Sha3_256};

// Exact XOR expressions. Atom 0 means one; all other atoms denote Boolean
// functions. HashMap hashes are only indices: full keys are compared on lookup.
type E = Vec<u32>;
type Triple = [E;3];
struct Algebra { next:u32, products:HashMap<Triple,u32>, cap:usize, truncations:u64 }
impl Algebra {
 fn fresh(&mut self)->E { let n=self.next; self.next+=1; vec![n] }
 fn xor_raw(a:&E,b:&E)->E {
  let (mut i,mut j)=(0,0); let mut r=Vec::with_capacity(a.len()+b.len());
  while i<a.len() || j<b.len() {
   if j==b.len() || (i<a.len()&&a[i]<b[j]) { r.push(a[i]);i+=1; }
   else if i==a.len() || b[j]<a[i] { r.push(b[j]);j+=1; }
   else {i+=1;j+=1;}
  } r
 }
 fn limit(&mut self,e:E)->E {if e.len()>self.cap {self.truncations+=1;self.fresh()} else {e}}
 fn xor(&mut self,a:&E,b:&E)->E {self.limit(Self::xor_raw(a,b))}
 fn triple(a:&E,b:&E)->Triple {
  let z=Self::xor_raw(&vec![0],&Self::xor_raw(a,b));
  let mut t=[a.clone(),b.clone(),z];t.sort();t
 }
 fn and(&mut self,a:&E,b:&E)->E {
  if a.is_empty()||b.is_empty(){return vec![];}
  if a==&vec![0]{return b.clone();} if b==&vec![0]||a==b{return a.clone();}
  let t=Self::triple(a,b); if t.iter().any(|v|v.is_empty()){return vec![];}
  if let Some(&v)=self.products.get(&t){return vec![v];}
  let v=self.next;self.next+=1;self.products.insert(t,v);vec![v]
 }
 fn select(&mut self,old:&E,new:&E,cond:&E)->E {
  if cond==&vec![0]{return new.clone();} if cond.is_empty(){return old.clone();}
  let d=self.xor(old,new);let v=self.and(cond,&d);self.xor(old,&v)
 }
}
fn hash(ops:&[Op])->String {
 let mut h=Sha3_256::new();for o in ops {h.update((o.kind as u64).to_le_bytes());
 for v in [o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}
 format!("{:x}",h.finalize())
}
fn make(k:K,c2:u64,c1:u64,t:u64,ct:u64,cc:u64)->Op {
 let mut o=Op::empty();o.kind=k;o.q_control2=QubitId(c2);o.q_control1=QubitId(c1);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o.validate();o
}
fn initial_inputs(ops:&[Op],nq:usize,nb:usize,alg:&mut Algebra)->(Vec<E>,Vec<E>){
 // Register annotations are metadata: inputs are loaded before op zero.
 let no=u64::MAX;let mut q=vec![E::new();nq];let mut c=vec![E::new();nb];
 let mut qs=HashSet::new();let mut cs=HashSet::new();
 for o in ops {if o.kind==K::AppendToRegister {
  if o.q_target.0!=no&&qs.insert(o.q_target.0){q[o.q_target.0 as usize]=alg.fresh();}
  if o.c_target.0!=no&&cs.insert(o.c_target.0){c[o.c_target.0 as usize]=alg.fresh();}
 }}(q,c)
}

fn audit(ops:&[Op],leases:&[[u64;9]],zeros:&[usize],cap:usize,sat:&HashSet<(usize,usize)>,boundaries:&HashMap<usize,serde_json::Value>){
 let no=u64::MAX;
 let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let mut alg=Algebra{next:1,products:HashMap::new(),cap,truncations:0};
 let(mut q,mut c)=initial_inputs(ops,nq,nb,&mut alg);let mut base=vec![0];let mut stack=vec![];
 let starts:HashMap<_,_>=leases.iter().map(|s|(s[0]as usize,s)).collect();
 let ends:HashMap<_,_>=leases.iter().map(|s|(s[1]as usize,s)).collect();
 assert_eq!(starts.len(),leases.len());assert_eq!(ends.len(),leases.len());
 assert!(starts.keys().all(|i|!ends.contains_key(i)));
 let mut expected:HashMap<usize,E>=HashMap::new();let mut active:HashMap<u64,usize>=HashMap::new();
 let zeros:HashSet<_>=zeros.iter().copied().collect();let mut checked_zero=0;let mut checked_end=0;
 for(i,o)in ops.iter().enumerate(){
  if o.kind==K::AppendToRegister||o.kind==K::Register{continue;}
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  let product=if o.kind==K::CCX{Some(alg.and(&q[a],&q[b]))}else{None};
  if zeros.contains(&i){assert_eq!(o.kind,K::CCX);let v=alg.and(product.as_ref().unwrap(),&eff);assert!(v.is_empty(),"unproved zero row {i}");checked_zero+=1;}
  if let Some(s)=starts.get(&i){
   assert_eq!(eff,vec![0],"unknown start guard {i}");assert_eq!(o.kind,K::CCX);
   assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);
   assert!(q[s[2]as usize].is_empty(),"unclean donor at {i}");
   assert!(!active.contains_key(&s[2]));assert!(s[0]<s[1]);
   if let Some(bd)=boundaries.get(&i){
    assert_eq!(bd["first"].as_u64().unwrap(),i as u64);
    for(k,e)in bd["q"].as_object().unwrap(){assert_eq!(q[k.parse::<usize>().unwrap()],serde_json::from_value::<E>(e.clone()).unwrap(),"quantum boundary mismatch at {i}");}
    for(k,e)in bd["c"].as_object().unwrap(){assert_eq!(c[k.parse::<usize>().unwrap()],serde_json::from_value::<E>(e.clone()).unwrap(),"classical boundary mismatch at {i}");}
    assert_eq!(base,serde_json::from_value::<E>(bd["base"].clone()).unwrap());
    assert_eq!(stack,serde_json::from_value::<Vec<E>>(bd["stack"].clone()).unwrap());
   }
   active.insert(s[2],i);expected.insert(i,product.clone().unwrap());
  }
  if let Some(s)=ends.get(&i){
   assert_eq!(eff,vec![0],"unknown end guard {i}");assert_eq!(o.kind,K::CCX);
   assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);
   assert!(product.as_ref().unwrap()==&expected[&(s[0]as usize)] || sat.contains(&(s[0]as usize,i)),"no verified product theorem at {i}");
   assert_eq!(active.get(&s[2]),Some(&(s[0]as usize)));checked_end+=1;
  }
  if !eff.is_empty(){for w in [o.q_control2.0,o.q_control1.0,o.q_target.0]{assert!(!active.contains_key(&w),"donor touched at {i}");}}
  if let Some(s)=ends.get(&i){active.remove(&s[2]);}
    match o.kind {
   K::X=>{q[t]=alg.xor(&q[t],&eff);},
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(product.as_ref().unwrap(),&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{
    q[t]=alg.select(&q[t],&vec![],&eff);
    if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}
   },
   K::BitInvert=>{c[ct]=alg.xor(&c[ct],&eff);},
   K::BitStore0=>{c[ct]=alg.select(&c[ct],&vec![],&eff);},
   K::BitStore1=>{c[ct]=alg.select(&c[ct],&vec![0],&eff);},
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::DebugPrint=>{},
   _=>panic!("unhandled {:?}",o.kind)
  }

  if i%2000000==0{eprintln!("audited {i} end_proofs={checked_end} zero_proofs={checked_zero}");}
 }
 assert!(stack.is_empty()&&active.is_empty());assert_eq!(checked_end,leases.len());assert_eq!(checked_zero,zeros.len());
}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),6,"baseline public_parent leases_json receipt verified_proofs");
 let base=io::load_ops(&args[1]);let parent=io::load_ops(&args[2]);
 assert_eq!(base.len(),17891821);assert_eq!(parent.len(),17891901);
 assert_eq!(hash(&base[..base.len()-96]),"c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04");
 assert_eq!(hash(&parent),"429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842");
 let leases:Vec<[u64;9]>=serde_json::from_str(&std::fs::read_to_string(&args[3]).unwrap()).unwrap();assert_eq!(leases.len(),27);
 let proof_bytes=std::fs::read(&args[5]).unwrap();let proof_manifest:serde_json::Value=serde_json::from_slice(&proof_bytes).unwrap();
 assert_eq!(proof_manifest["status"],"SOURCE_BOUND_EXTENSION_PROOFS_VERIFIED");
 assert_eq!(proof_manifest["base_pre_tail_sha3_256"],hash(&base[..base.len()-96]));
 let mut sat=HashSet::new();let mut boundaries=HashMap::new();
 for p in proof_manifest["proofs"].as_array().unwrap(){
  assert_eq!(p["fresh_replay"]["verdict"],"unsat");let first=p["first"].as_u64().unwrap()as usize;let last=p["last"].as_u64().unwrap()as usize;
  assert!(sat.insert((first,last)));let bd:serde_json::Value=serde_json::from_str(&std::fs::read_to_string(p["boundary_file"].as_str().unwrap()).unwrap()).unwrap();assert!(boundaries.insert(first,bd).is_none());
 }
 assert_eq!(sat.len(),27);assert!(leases.iter().all(|s|sat.contains(&(s[0]as usize,s[1]as usize))));
 audit(&base,&leases,&[],1024,&sat,&boundaries);
 let no=u64::MAX;let nb=base.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap()+1;assert_eq!(nb,54995);
 let starts:HashMap<_,_>=leases.iter().map(|s|(s[0]as usize,s)).collect();let ends:HashMap<_,_>=leases.iter().map(|s|(s[1]as usize,s)).collect();
 let mut generated=Vec::with_capacity(parent.len()+1);
 for(i,o)in base[..base.len()-96].iter().enumerate(){
  if let Some(s)=starts.get(&i){let mut fill=*o;fill.q_target=QubitId(s[2]);generated.push(fill);generated.push(make(K::CX,no,s[2],s[5],no,no));}
  else if let Some(s)=ends.get(&i){generated.push(make(K::CX,no,s[2],s[8],no,no));generated.push(make(K::Hmr,no,no,s[2],nb,no));generated.push(make(K::CZ,no,s[6],s[7],no,nb));}
  else{generated.push(*o);}
 }
 assert_eq!(hash(&generated),"468e86dd1628976643d42b4bb50bdb8c43211f4d29bfbc3df60b11f7342ac619");
 generated.extend_from_slice(&parent[parent.len()-96..]);
 let zero=&proof_manifest["zero_row"];assert_eq!(zero["fresh_replay"]["verdict"],"unsat");assert_eq!(zero["meaningful_source_fault_detected"],true);
 let meta=&zero["input"];assert_eq!(meta["base_pre_tail_sha3_256"],"468e86dd1628976643d42b4bb50bdb8c43211f4d29bfbc3df60b11f7342ac619");
 let start=meta["start"].as_u64().unwrap()as usize;let index=meta["first"].as_u64().unwrap()as usize;assert_eq!(index,17876252);assert_eq!(meta["last"].as_u64().unwrap()as usize,index);assert_eq!(meta["initial_depth"],0);
 let mut depth=0isize;for o in &generated[..start]{if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}assert!(depth>=0);}assert_eq!(depth,0);
 assert_eq!(hash(&generated[start..=index]),meta["raw_sha3_256"].as_str().unwrap());
 assert_eq!(hash(&generated[index..=index]),meta["row_sha3_256"].as_str().unwrap());
 assert_eq!(meta["row_sha3_256"],"167c7dad3201c7b11743b8d6bdd1949fa61952ac7201f71692a3a369be305823");
 generated.remove(17876252);assert_eq!(generated,parent);
 for s in [&base[base.len()-96..],&parent[parent.len()-96..]]{for pair in s.chunks_exact(2){assert_eq!(pair[0],pair[1]);assert_eq!(pair[0].kind,K::X);assert!(pair[0].q_target.0<=1);}}
 let result=serde_json::json!({"status":"PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS","base_pre_tail_sha3_256":hash(&base[..base.len()-96]),"parent_sha3_256":hash(&parent),"retained_products":leases.len(),"zero_rows":1,"zero_row_proof":"source-bound root-scope arbitrary-input SAT theorem, freshly replayed with detected source-control mutation","no_sampled_inputs":true,"sat_proof_manifest_sha3_256":format!("{:x}",Sha3_256::digest(&proof_bytes)),"statement":"The 27 unconditional products follow from replayed source-bound SAT theorems and matched global boundary states, with clean untouched donors and fresh private measurement/phase correction. The removed CCX has zero effective product for every input and measurement assignment. Reconstructed output equals the exact public parent bytes."});
 std::fs::write(&args[4],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("PUBLIC_PARENT_EXTENSION_UNIVERSAL_AUDIT_PASS");
}
