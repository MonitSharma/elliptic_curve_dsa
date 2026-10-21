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
fn main(){
 let args:Vec<_>=std::env::args().collect();assert!(args.len()==4,"input output-prefix expression-cap");
 let ops=io::load_ops(&args[1]);let out=&args[2];let no=u64::MAX;
 let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|x|*x!=no).max().unwrap() as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap() as usize+1;
 let mut alg=Algebra{next:1,products:HashMap::new(),cap:args[3].parse().unwrap(),truncations:0};
 let (mut q,mut c)=initial_inputs(&ops,nq,nb,&mut alg);
 let mut stack:Vec<E>=vec![];let mut base=vec![0];
 let mut touches=vec![None;nq];let mut busy=vec![None;nq];
 let mut uses:HashMap<Triple,(usize,Op)>=HashMap::new();let mut endpoints=HashSet::new();
 let mut leases:Vec<[u64;9]>=vec![];let mut pairs=0;let mut dead=0;let mut unconditional=0;
 let mut zero_products:Vec<usize>=vec![];let mut linear_products:HashMap<usize,u64>=HashMap::new();
 let mut exact_reductions_unconditional=0;
 for (i,o) in ops.iter().enumerate(){
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::AppendToRegister {continue;}
  if o.kind==K::PushCondition {stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition {base=stack.pop().expect("balanced conditions");continue;}
  let eff=if o.c_condition.0==no {base.clone()} else {alg.and(&base,&c[o.c_condition.0 as usize])};
  if eff.is_empty(){dead+=1;continue;}
  let always=eff==vec![0];
  let product=if o.kind==K::CCX{Some(alg.and(&q[a],&q[b]))}else{None};
  let reducible=if let Some(ref p)=product {
   if p.is_empty(){zero_products.push(i);true}
   else if p==&q[a]{linear_products.insert(i,a as u64);true}
   else if p==&q[b]{linear_products.insert(i,b as u64);true}
   else{false}
  }else{false};
  if reducible&&always {exact_reductions_unconditional+=1;}
  if o.kind==K::CCX && always && !reducible {
   unconditional+=1;let key=Algebra::triple(&q[a],&q[b]);
   if let Some(&(first,p))=uses.get(&key){
    pairs+=1;
    if !endpoints.contains(&first)&&!endpoints.contains(&i) {
     let donor=(0..nq).find(|&d| d!=a&&d!=b&&d!=t&&q[d].is_empty()&&touches[d].is_none_or(|j|j<first)&&busy[d].is_none_or(|j|j<first));
     if let Some(d)=donor {
      leases.push([first as u64,i as u64,d as u64,p.q_control2.0,p.q_control1.0,p.q_target.0,o.q_control2.0,o.q_control1.0,o.q_target.0]);
      busy[d]=Some(i);endpoints.insert(first);endpoints.insert(i);
     }
    }
   }
   uses.insert(key,(i,*o));
  }
  for v in [o.q_control1.0,o.q_control2.0,o.q_target.0] {if v!=no{touches[v as usize]=Some(i);}}
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
  if i%1000000==0{eprintln!("op {i}, products {}, leases {}, truncated {}",alg.products.len(),leases.len(),alg.truncations);}
 }
 assert!(stack.is_empty());
 let result=serde_json::json!({"status":"EXACT_SYMBOLIC_DISCOVERY_ONLY","input":args[1],"input_count":ops.len(),"input_sha3_256":hash(&ops),"peak_qubits":nq,"classical_bits":nb,"expression_cap":alg.cap,"truncations":alg.truncations,"unconditional_ccx":unconditional,"repeated_pairs":pairs,"dead_ops":dead,"leases":leases,"zero_products":zero_products,"linear_products":linear_products,"exact_reductions_unconditional":exact_reductions_unconditional});
 std::fs::write(format!("{out}.json"),serde_json::to_string_pretty(&result).unwrap()).unwrap();
 eprintln!("SUMMARY leases={} zero={} linear={} unconditional_reductions={} repeated_pairs={} truncations={}",leases.len(),zero_products.len(),linear_products.len(),exact_reductions_unconditional,pairs,alg.truncations);
 // Add a fresh classical bit. It cannot affect any existing control path.
 let starts:HashMap<_,_>=leases.iter().map(|s|(s[0] as usize,s)).collect();
 let ends:HashMap<_,_>=leases.iter().map(|s|(s[1] as usize,s)).collect();
 let mut rewritten=Vec::with_capacity(ops.len()+3*leases.len());
 let zero_products:HashSet<_>=zero_products.into_iter().collect();
 for (i,o) in ops.into_iter().enumerate(){
  if zero_products.contains(&i){continue;}
  if let Some(&control)=linear_products.get(&i){let mut cx=o;cx.kind=K::CX;cx.q_control2=QubitId(no);cx.q_control1=QubitId(control);cx.validate();rewritten.push(cx);}
  else if let Some(s)=starts.get(&i){let mut fill=o;fill.q_target=QubitId(s[2]);rewritten.push(fill);rewritten.push(make(K::CX,no,s[2],s[5],no,no));}
  else if let Some(s)=ends.get(&i){rewritten.push(make(K::CX,no,s[2],s[8],no,no));rewritten.push(make(K::Hmr,no,no,s[2],nb as u64,no));rewritten.push(make(K::CZ,no,s[6],s[7],no,nb as u64));}
  else {rewritten.push(o);}
 }
 io::save_ops(&format!("{out}.ops.bin"),&rewritten);
}

#[cfg(test)]mod tests{
 use super::*;
 fn alg()->Algebra{Algebra{next:3,products:HashMap::new(),cap:128,truncations:0}}
 #[test]fn triple_and_complement(){let mut a=alg();let x=vec![1];let y=vec![2];let z=vec![0,1,2];let xy=a.and(&x,&y);assert_eq!(xy,a.and(&x,&z));assert_eq!(xy,a.and(&y,&z));assert_eq!(a.and(&x,&vec![0,1]),E::new());}
 #[test]fn unknown_guard_is_not_assumed_true(){let mut a=alg();let v=a.select(&vec![],&vec![0],&vec![1]);assert_eq!(v,vec![1]);assert_ne!(v,vec![0]);}
 #[test]fn truncation_is_fresh(){let mut a=alg();a.cap=1;assert_ne!(a.xor(&vec![1],&vec![2]),a.xor(&vec![1],&vec![2]));}
 #[test]fn late_register_annotations_are_initial_inputs(){let mut a=alg();let mut r=Op::empty();r.kind=K::AppendToRegister;r.q_target=QubitId(0);r.r_target.0=0;let x=make(K::X,u64::MAX,u64::MAX,0,u64::MAX,u64::MAX);let (q,_)=initial_inputs(&[x,r,r],2,0,&mut a);assert!(!q[0].is_empty());assert_eq!(q[0].len(),1);assert!(q[1].is_empty());assert_eq!(a.next,4);}
}
