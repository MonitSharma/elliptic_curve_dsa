//! Exact Boolean identities only; bounded expansion never assumes a value.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{BTreeSet,HashSet};
use sha3::{Digest,Sha3_256};
type M=Vec<u32>;type P=Vec<M>;const NO:u64=u64::MAX;
fn one()->P{vec![vec![]]}
struct Algebra{next:u32,cap:usize,degree:usize,cuts:u64}
impl Algebra{
 fn fresh(&mut self)->P{let n=self.next;self.next=self.next.checked_add(1).unwrap();vec![vec![n]]}
 fn limit(&mut self,p:P)->P{if p.len()>self.cap{self.cuts+=1;self.fresh()}else{p}}
 fn xor(&mut self,a:&P,b:&P)->P{
  let(mut i,mut j)=(0,0);let mut p=vec![];
  while i<a.len()||j<b.len(){if j==b.len()||(i<a.len()&&a[i]<b[j]){p.push(a[i].clone());i+=1;}else if i==a.len()||b[j]<a[i]{p.push(b[j].clone());j+=1;}else{i+=1;j+=1;}}
  self.limit(p)
 }
 fn and(&mut self,a:&P,b:&P)->P{
  if a.is_empty()||b.is_empty(){return vec![];}if a==b||b==&one(){return a.clone();}if a==&one(){return b.clone();}
  let mut result=BTreeSet::new();
  for x in a{for y in b{let mut m=x.clone();m.extend_from_slice(y);m.sort_unstable();m.dedup();
   if m.len()>self.degree{self.cuts+=1;return self.fresh();}
   if !result.remove(&m){result.insert(m);}if result.len()>self.cap{self.cuts+=1;return self.fresh();}
  }}result.into_iter().collect()
 }
 fn select(&mut self,old:&P,new:&P,c:&P)->P{if c==&one(){return new.clone();}if c.is_empty(){return old.clone();}let d=self.xor(old,new);let d=self.and(c,&d);self.xor(old,&d)}
}
include!("witness.rs");
fn scan(v:&[Op],alg:&mut Algebra)->(Vec<Op>,Vec<serde_json::Value>){scan_with_witness(v,alg,std::env::var("ANF_WITNESSES").unwrap_or_else(|_|"1".into())=="1")}
fn scan_with_witness(v:&[Op],alg:&mut Algebra,use_witnesses:bool)->(Vec<Op>,Vec<serde_json::Value>){
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&x|x!=NO).max().unwrap_or(0)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&x|x!=NO).max().unwrap_or(0)as usize+1;
 let mut q=vec![P::new();nq];let mut c=vec![P::new();nb];let(mut qs,mut cs)=(HashSet::new(),HashSet::new());
 for o in v{if o.kind==K::AppendToRegister{if o.q_target.0!=NO&&qs.insert(o.q_target.0){q[o.q_target.0 as usize]=alg.fresh();}if o.c_target.0!=NO&&cs.insert(o.c_target.0){c[o.c_target.0 as usize]=alg.fresh();}}}
 let mut witnesses=Witnesses::default();if use_witnesses{for (slot,value)in q.iter().enumerate(){witnesses.insert(slot,value);}}
 let mut base=one();let mut stack=vec![];let mut out=vec![];let mut sites=vec![];
 for(i,o)in v.iter().enumerate(){
  if o.kind==K::AppendToRegister{out.push(*o);continue;}
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);out.push(*o);continue;}
  if o.kind==K::PopCondition{base=stack.pop().expect("balanced guards");out.push(*o);continue;}
  let eff=if o.c_condition.0==NO{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let(a,b,t,ct)=(o.q_control1.0 as usize,o.q_control2.0 as usize,o.q_target.0 as usize,o.c_target.0 as usize);
  let mut replacement=Some(*o);let mut increment=None;let mut prefix=None;
  if o.kind==K::CCX{
   let raw_product=alg.and(&q[a],&q[b]);let ab=alg.and(&eff,&raw_product);
   if !eff.is_empty(){let ca=alg.and(&eff,&q[a]);let cb=alg.and(&eff,&q[b]);
    let single=if ab.is_empty(){replacement=None;None}else if ab==ca{Some(o.q_control1.0)}else if ab==cb{Some(o.q_control2.0)}else{None};
    if let Some(control)=single{let mut x=*o;x.kind=K::CX;x.q_control2=QubitId(NO);x.q_control1=QubitId(control);x.validate();replacement=Some(x);}
    if replacement.is_none()||single.is_some(){sites.push(serde_json::json!({"op":i,"replacement_control":single,"guard_unconditional":eff==one(),"proof_effect":ab,"guard":eff,"control1":q[a],"control2":q[b]}));}
   }
   if use_witnesses&&!eff.is_empty()&&replacement.as_ref().is_some_and(|x|x.kind==K::CCX){
    if let Some((w,complement))=witnesses.find(&raw_product,a,b,t,alg.cap){
     let mut x=*o;x.kind=K::CX;x.q_control2=QubitId(NO);x.q_control1=QubitId(w as u64);x.validate();replacement=Some(x);
     if complement{let mut z=*o;z.kind=K::X;z.q_control1=QubitId(NO);z.q_control2=QubitId(NO);z.validate();prefix=Some(z);}
     sites.push(serde_json::json!({"op":i,"kind":"exact_current_wire_product","witness":w,"complement":complement,"guard":eff,"product":raw_product,"witness_value":q[w]}));
    }
   }
increment=Some(ab);
  }
  if let Some(x)=prefix{out.push(x);}
  if let Some(o)=replacement{out.push(o);}
  if eff.is_empty(){continue;}
  let mut changed=if use_witnesses{match o.kind{K::Swap=>vec![a,t],K::X|K::CX|K::CCX|K::R|K::Hmr=>vec![t],_=>vec![]}}else{vec![]};changed.sort_unstable();changed.dedup();for &slot in &changed{witnesses.remove(slot,&q[slot]);}
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let d=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&d);},
   K::CCX=>q[t]=alg.xor(&q[t],&increment.unwrap()),
   K::Swap=>{let d=alg.xor(&q[a],&q[t]);let d=alg.and(&d,&eff);q[a]=alg.xor(&q[a],&d);q[t]=alg.xor(&q[t],&d);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let d=alg.fresh();c[ct]=alg.select(&c[ct],&d,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&one(),&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::DebugPrint=>{},
   _=>panic!("unhandled {:?}",o.kind)
  }
  for &slot in &changed{witnesses.insert(slot,&q[slot]);}
  if i%1_000_000==0{eprintln!("op={i} sites={} fresh={} cuts={}",sites.len(),alg.next,alg.cuts);}
 }assert!(stack.is_empty());(out,sites)
}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let v=io::load_ops(&a[1]);assert_eq!(hash(&v),a[3]);let mut alg=Algebra{next:1,cap:256,degree:12,cuts:0};let(out,sites)=scan(&v,&mut alg);io::save_ops(&format!("{}.ops.bin",a[2]),&out);
 let result=serde_json::json!({"status":"EXACT_ANF_SOURCE_DIAGNOSTIC_NOT_A_RESOURCE_RESULT","input":a[1],"input_ops":v.len(),"input_sha3_256":hash(&v),"output_ops":out.len(),"output_sha3_256":hash(&out),"term_cap":alg.cap,"degree_cap":alg.degree,"cuts":alg.cuts,"sites_count":sites.len(),"sites":sites});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("sites={}",result["sites_count"]);}
#[cfg(test)]mod tests{
 use super::*;
 fn alg()->Algebra{Algebra{next:8,cap:64,degree:8,cuts:0}}
 fn var(n:u32)->P{vec![vec![n]]}
 fn eval(p:&P,x:u32)->bool{p.iter().fold(false,|a,m|a^m.iter().all(|i|x>>(i-1)&1!=0))}
 #[test]fn distributivity(){let mut g=alg();let a=var(1);let b=var(2);let c=var(3);let bc=g.xor(&b,&c);let lhs=g.and(&a,&bc);let ab=g.and(&a,&b);let ac=g.and(&a,&c);assert_eq!(lhs,g.xor(&ab,&ac));}
 #[test]fn complementary_product_zero(){let mut g=alg();let p=vec![vec![],vec![1],vec![2,3]];let np=g.xor(&p,&one());assert!(g.and(&p,&np).is_empty());}
 #[test]fn exhaustive_polynomial_arithmetic(){let mut g=alg();let ps=[vec![],one(),var(1),vec![vec![1],vec![2]],vec![vec![],vec![1,2],vec![3]]];for a in &ps{for b in &ps{let x=g.xor(a,b);let y=g.and(a,b);for n in 0..8{assert_eq!(eval(&x,n),eval(a,n)^eval(b,n));assert_eq!(eval(&y,n),eval(a,n)&eval(b,n));}}}}
 #[test]fn term_limit_creates_fresh_unknown(){let mut g=alg();g.cap=1;let a=g.xor(&var(1),&var(2));let b=g.xor(&var(1),&var(2));assert_ne!(a,b);assert!(!a.is_empty());}
 #[test]fn conditional_reset_preserves_old_branch(){let mut g=alg();let p=g.select(&var(1),&vec![],&var(2));for n in 0..4{assert_eq!(eval(&p,n),(n&1!=0)&&(n&2==0));}}
 fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o}
 #[test]fn arbitrary_input_not_assumed_zero(){let mut r=gate(K::AppendToRegister,NO,NO,0);r.r_target.0=0;let v=vec![gate(K::X,NO,NO,1),gate(K::CCX,0,1,2),r];let(_,s)=scan(&v,&mut alg());assert_eq!(s.len(),1);assert_eq!(s[0]["replacement_control"],0);}
 #[test]fn nonlinear_complement_removes_product(){let mut v=vec![];for t in 0..2{let mut r=gate(K::AppendToRegister,NO,NO,t);r.r_target.0=0;v.push(r);}v.extend([gate(K::CCX,0,1,2),gate(K::CX,2,NO,3),gate(K::X,NO,NO,3),gate(K::CCX,2,3,4)]);let(_,s)=scan(&v,&mut alg());assert_eq!(s.len(),1);assert_eq!(s[0]["op"],5);assert!(s[0]["replacement_control"].is_null());}
}

#[cfg(test)] #[path="tests_large.rs"] mod large_tests;

#[cfg(test)] #[path="tests_witness.rs"] mod witness_tests;
