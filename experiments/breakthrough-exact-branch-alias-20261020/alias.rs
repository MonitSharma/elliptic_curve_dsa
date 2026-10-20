//! Research only. Exact XOR functions plus conservative branch supports.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K};
use std::collections::{HashMap,HashSet};
const NO:u64=u64::MAX;
type E=Vec<u32>;
type Triple=[E;3];
struct Algebra{next:u32,products:HashMap<Triple,u32>,cap:usize,truncations:u64}
impl Algebra{
 fn fresh(&mut self)->E{let n=self.next;self.next+=1;vec![n]}
 fn xor_raw(a:&E,b:&E)->E{let(mut i,mut j)=(0,0);let mut r=vec![];while i<a.len()||j<b.len(){if j==b.len()||(i<a.len()&&a[i]<b[j]){r.push(a[i]);i+=1;}else if i==a.len()||b[j]<a[i]{r.push(b[j]);j+=1;}else{i+=1;j+=1;}}r}
 fn xor(&mut self,a:&E,b:&E)->E{let r=Self::xor_raw(a,b);if r.len()>self.cap{self.truncations+=1;self.fresh()}else{r}}
 fn and(&mut self,a:&E,b:&E)->E{if a.is_empty()||b.is_empty(){return vec![];}if a==&vec![0]{return b.clone();}if b==&vec![0]||a==b{return a.clone();}let z=Self::xor_raw(&vec![0],&Self::xor_raw(a,b));let mut t=[a.clone(),b.clone(),z];t.sort();if t[0].is_empty(){return vec![];}if let Some(&v)=self.products.get(&t){return vec![v];}let v=self.next;self.next+=1;self.products.insert(t,v);vec![v]}
 fn select(&mut self,old:&E,new:&E,g:&E)->E{if g==&vec![0]{return new.clone();}if g.is_empty(){return old.clone();}let d=self.xor(old,new);let v=self.and(g,&d);self.xor(old,&v)}
}
// Literals identify complete Boolean functions, including captured guard values.
// Equal HashMap keys are compared in full; hashes are never proof witnesses.
type Term=Vec<i64>;
type Support=Vec<Term>;
fn conj(a:&Term,b:&Term)->Option<Term>{let mut r=a.clone();r.extend(b);r.sort_unstable();r.dedup();if r.iter().any(|x|r.binary_search(&(-x)).is_ok()){None}else{Some(r)}}
fn subset(a:&Term,b:&Term)->bool{a.iter().all(|x|b.binary_search(x).is_ok())}
fn norm(terms:Support)->Support{let mut r:Support=vec![];for t in terms{if t.is_empty(){return vec![vec![]];}if r.iter().any(|a|subset(a,&t)){continue;}r.retain(|a|!subset(&t,a));r.push(t);if r.len()>32{return vec![vec![]];}}r.sort();r}
fn union(a:&Support,b:&Support)->Support{let mut r=a.clone();r.extend(b.clone());norm(r)}
fn intersect(a:&Support,b:&Support)->Support{norm(a.iter().flat_map(|x|b.iter().filter_map(move|y|conj(x,y))).collect())}
fn reset(a:&Support,g:&Support)->Support{if g.is_empty(){return a.clone();}assert_eq!(g.len(),1);let guard=&g[0];a.iter().filter(|t|!subset(guard,t)).cloned().collect()}
struct Pred{keys:HashMap<E,i64>}
impl Pred{fn guard(&mut self,e:&E)->Support{if e.is_empty(){return vec![];}if e==&vec![0]{return vec![vec![]];}let flip=e[0]==0;let key=if flip{e[1..].to_vec()}else{e.clone()};let next=self.keys.len()as i64+1;let id=*self.keys.entry(key).or_insert(next);vec![vec![if flip{-id}else{id}]]}}
fn dims(v:&[Op])->(usize,usize){let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&x|x!=NO).max().unwrap()as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&x|x!=NO).max().map_or(0,|x|x as usize+1);(nq,nb)}
#[derive(Clone)]struct Interval{first:usize,last:usize,donor:usize,choices:usize}
struct Answer{nq:usize,nb:usize,intervals:Vec<Interval>,failure:Option<serde_json::Value>,truncations:u64,zero_cancellations:u64,products:usize}
fn analyze(v:&[Op],cap:usize)->Answer{
 let(nq,nb)=dims(v);let top=nq-1;let mut alg=Algebra{next:1,products:HashMap::new(),cap,truncations:0};let mut pred=Pred{keys:HashMap::new()};let mut q=vec![E::new();nq];let mut c=vec![E::new();nb];let mut s=vec![Support::new();nq];let mut registered=HashSet::new();
 for o in v{if o.kind==K::AppendToRegister{if o.q_target.0!=NO&&registered.insert(o.q_target.0){q[o.q_target.0 as usize]=alg.fresh();s[o.q_target.0 as usize]=vec![vec![]];}if o.c_target.0!=NO{c[o.c_target.0 as usize]=alg.fresh();}}}
 let mut result=Answer{nq,nb,intervals:vec![],failure:None,truncations:0,zero_cancellations:0,products:0};if registered.contains(&(top as u64)){result.failure=Some(serde_json::json!({"reason":"highest qubit is a fixed register input"}));return result;}
 let mut base=vec![0];let mut guard=vec![vec![]];let mut stack=vec![];let mut active:Option<(usize,Vec<bool>)>=None;
 for(i,o)in v.iter().enumerate(){
  if matches!(o.kind,K::Register|K::AppendToRegister){continue;}
  if o.kind==K::PushCondition{stack.push((base.clone(),guard.clone()));let p=pred.guard(&c[o.c_condition.0 as usize]);guard=intersect(&guard,&p);base=alg.and(&base,&c[o.c_condition.0 as usize]);if base.is_empty(){guard.clear();}continue;}
  if o.kind==K::PopCondition{(base,guard)=stack.pop().expect("balanced stack");continue;}
  let mut g=guard.clone();let mut e=base.clone();if o.c_condition.0!=NO{g=intersect(&g,&pred.guard(&c[o.c_condition.0 as usize]));e=alg.and(&e,&c[o.c_condition.0 as usize]);}if e.is_empty(){g.clear();}if g.is_empty(){e.clear();}
  let mut touched:Vec<_>=[o.q_control1.0,o.q_control2.0,o.q_target.0].into_iter().filter(|&x|x!=NO).map(|x|x as usize).collect();touched.sort_unstable();touched.dedup();let top_touch=touched.contains(&top);
  if top_touch&&active.is_none(){assert!(s[top].is_empty());active=Some((i,vec![true;top]));}
  if let Some((first,allowed))=&mut active{
   if top_touch{for d in 0..top{if allowed[d]&&(touched.contains(&d)||!intersect(&g,&s[d]).is_empty()){allowed[d]=false;}}}
   for &d in &touched{if d<top&&allowed[d]&&!intersect(&g,&s[top]).is_empty(){allowed[d]=false;}}
   if !allowed.iter().any(|x|*x){result.failure=Some(serde_json::json!({"reason":"no branch-disjoint donor for complete top interval","first":first,"failed_at":i,"top_support_terms":s[top].len(),"universal_supports":s.iter().filter(|x|**x==vec![vec![]]).count(),"globally_zero_wires":s.iter().filter(|x|x.is_empty()).count()}));break;}
  }
  let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);
  if !g.is_empty(){match o.kind{
   K::X=>{q[t]=alg.xor(&q[t],&e);s[t]=union(&s[t],&g);},
   K::CX=>{let x=alg.and(&q[a],&e);q[t]=alg.xor(&q[t],&x);s[t]=union(&s[t],&intersect(&g,&s[a]));},
   K::CCX=>{let x=alg.and(&q[a],&q[b]);let x=alg.and(&x,&e);q[t]=alg.xor(&q[t],&x);s[t]=union(&s[t],&intersect(&g,&intersect(&s[a],&s[b])));},
   K::Swap=>{let x=alg.xor(&q[a],&q[t]);let x=alg.and(&x,&e);q[a]=alg.xor(&q[a],&x);q[t]=alg.xor(&q[t],&x);let sa=s[a].clone();let st=s[t].clone();if e==vec![0]{s[a]=st;s[t]=sa;}else{s[a]=union(&sa,&intersect(&g,&st));s[t]=union(&st,&intersect(&g,&sa));}},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&e);s[t]=reset(&s[t],&g);if o.kind==K::Hmr{let mr=alg.fresh();c[ct]=alg.select(&c[ct],&mr,&e);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&e),K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&e),K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&e),
   K::Neg|K::Z|K::CZ|K::CCZ|K::DebugPrint=>{},_=>panic!("unhandled {:?}",o.kind)
  }}
  for &d in &touched{if q[d].is_empty(){if !s[d].is_empty(){result.zero_cancellations+=1;}s[d].clear();}if s[d].is_empty(){q[d].clear();}}
  if s[top].is_empty(){if let Some((first,allowed))=active.take(){let donor=allowed.iter().position(|x|*x).unwrap();result.intervals.push(Interval{first,last:i,donor,choices:allowed.iter().filter(|x|**x).count()});}}
  if i%1_000_000==0{eprintln!("op={i} intervals={} products={} truncations={} exact_zero={}",result.intervals.len(),alg.products.len(),alg.truncations,result.zero_cancellations);}
 }
 if result.failure.is_none(){assert!(stack.is_empty());if let Some((first,_))=active{result.failure=Some(serde_json::json!({"reason":"top lifetime not proved closed","first":first}));}}
 result.truncations=alg.truncations;result.products=alg.products.len();result
}
fn rewrite(v:&[Op],a:&Answer)->Vec<Op>{assert!(a.failure.is_none());let mut out=v.to_vec();for x in &a.intervals{for o in &mut out[x.first..=x.last]{for q in [&mut o.q_control1,&mut o.q_control2,&mut o.q_target]{if q.0==(a.nq-1)as u64{q.0=x.donor as u64;}}o.validate();}}assert!(out.iter().all(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0].iter().all(|&x|x==NO||x<(a.nq-1)as u64)));out}
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let v=io::load_ops(&args[1]);let a=analyze(&v,64);let report=serde_json::json!({"status":if a.failure.is_none(){"COMPLETE_STATIC_ALIAS_WITNESS_NOT_BENCHMARK"}else{"NO_COMPLETE_WIDTH_REDUCTION"},"input_Q":a.nq,"classical_bits":a.nb,"failure":a.failure,"proved_intervals":a.intervals.iter().map(|x|serde_json::json!({"first":x.first,"last":x.last,"donor":x.donor,"choices":x.choices})).collect::<Vec<_>>(),"xor_expression_cap":64,"opaque_truncations":a.truncations,"products":a.products,"exact_zero_cancellations":a.zero_cancellations,"scope":"Same kinds, conditions, order and RNG events. Full function keys and conservative supports; no sampled arithmetic or packet inputs. Stops at first failed lifetime. Static proof diagnostic only."});std::fs::write(format!("{}.json",args[2]),serde_json::to_string_pretty(&report).unwrap()).unwrap();if a.failure.is_none(){io::save_ops(&format!("{}.ops.bin",args[2]),&rewrite(&v,&a));}println!("{}",report);}

#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{circuit::{BitId,QubitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 fn op(k:K,a:u64,t:u64,ct:u64,cc:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o}
 fn regs()->Vec<Op>{let mut out=vec![];for q in 0..2{let mut o=op(K::AppendToRegister,NO,q,NO,NO);o.r_target=RegisterId(0);out.push(o);}let mut o=op(K::AppendToRegister,NO,NO,0,NO);o.r_target=RegisterId(1);out.push(o);out}
 fn fixture()->Vec<Op>{let mut v=regs();v.extend([op(K::BitStore1,NO,NO,1,NO),op(K::BitInvert,NO,NO,1,0),op(K::X,NO,2,NO,1),op(K::X,NO,3,NO,0),op(K::CX,3,0,NO,0),op(K::CX,2,1,NO,1),op(K::Hmr,NO,3,2,0),op(K::Neg,NO,NO,NO,2),op(K::Hmr,NO,2,3,1),op(K::Neg,NO,NO,NO,3)]);v}
 fn sim(v:&[Op],nq:usize,seed:u64)->(Vec<u64>,Vec<u64>,u64,u64,[u8;32]){let mut h=Shake256::default();h.update(&seed.to_le_bytes());let mut rng=h.finalize_xof();let mut s=Simulator::new(nq,4,&mut rng);s.qubits[0]=0xaaaaaaaaaaaaaaaa;s.qubits[1]=0xcccccccccccccccc;s.bits[0]=0xf0f0f0f0f0f0f0f0;s.phase=0x5555555555555555;s.apply_iter(v.iter());let data=(s.qubits.clone(),s.bits.clone(),s.phase,s.stats.toffoli_gates);drop(s);let mut rest=[0;32];rng.read(&mut rest);(data.0,data.1,data.2,data.3,rest)}
 #[test]fn disjoint_branch_alias_preserves_protected_state_phase_and_rng(){let v=fixture();let a=analyze(&v,64);assert!(a.failure.is_none(),"{:?}",a.failure);assert!(a.intervals.iter().any(|x|x.donor==2));let w=rewrite(&v,&a);for seed in 0..16{let x=sim(&v,4,seed);let y=sim(&w,3,seed);assert_eq!(x.0[3],0);assert_eq!(x.0[..3],y.0);assert_eq!((x.1,x.2,x.3,x.4),(y.1,y.2,y.3,y.4));}}
 #[test]fn overlapping_dirty_donor_is_rejected(){let mut v=fixture();v[5].c_condition=BitId(NO);let a=analyze(&v,64);assert!(a.failure.is_some());}
 #[test]fn same_operation_operand_alias_is_rejected(){let mut v=fixture();v.insert(7,op(K::CX,2,3,NO,0));let a=analyze(&v,64);assert!(a.failure.is_some());}
 #[test]fn wrong_reset_guard_cannot_close_lifetime(){let mut v=fixture();v[9].c_condition=BitId(1);let a=analyze(&v,64);assert!(a.failure.is_some());}
 #[test]fn exact_xor_cancellation_closes_unmeasured_lifetime(){let mut v=regs();v.extend([op(K::CX,0,3,NO,0),op(K::CX,1,3,NO,0),op(K::CX,0,3,NO,0),op(K::CX,1,3,NO,0)]);let a=analyze(&v,64);assert!(a.failure.is_none());assert!(a.zero_cancellations>0);assert_eq!(a.intervals.len(),1);}
 #[test]fn complementary_captured_guard_survives_bit_mutation(){let mut v=regs();v.extend([op(K::X,NO,2,NO,NO),op(K::R,NO,2,NO,NO),op(K::PushCondition,NO,NO,NO,0),op(K::X,NO,3,NO,NO),op(K::BitInvert,NO,NO,0,NO),op(K::Hmr,NO,3,2,NO),op(K::PopCondition,NO,NO,NO,NO)]);assert!(analyze(&v,64).failure.is_none());}
 #[test]fn support_contradiction_and_overflow_are_conservative(){assert!(conj(&vec![1],&vec![-1]).is_none());let terms=(1..35).map(|i|vec![i]).collect();assert_eq!(norm(terms),vec![vec![]]);let s=vec![vec![1,2],vec![3]];assert_eq!(reset(&s,&vec![vec![1]]),vec![vec![3]]);}
 #[test]fn symtriple_representations_and_complements(){let mut a=Algebra{next:1,products:HashMap::new(),cap:64,truncations:0};let x=a.fresh();let y=a.fresh();let p=a.and(&x,&y);let z=Algebra::xor_raw(&vec![0],&Algebra::xor_raw(&x,&y));assert_eq!(p,a.and(&x,&z));let nx=Algebra::xor_raw(&vec![0],&x);assert!(a.and(&x,&nx).is_empty());}
}
