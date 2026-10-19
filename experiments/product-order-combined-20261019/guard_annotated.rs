//! Conservative nonzero supports. Never use sampled inputs to choose a circuit.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{BTreeSet,HashMap};
use sha3::{Digest,Sha3_256};
const NO:u64=u64::MAX;
type Id=u32;
#[derive(Clone,Debug,Hash,PartialEq,Eq)]enum B{Zero,One,Input(u64),Mr(u64),Not(Id),And(Vec<Id>),Xor(Id,Id),Ite(Id,Id,Id),Cut(u64,Id,Id)}
struct BoolDag{nodes:Vec<B>,intern:HashMap<B,Id>,cuts:u64}
impl BoolDag{
 fn new()->Self{let mut d=Self{nodes:vec![],intern:HashMap::new(),cuts:0};assert_eq!(d.node(B::Zero),0);assert_eq!(d.node(B::One),1);d}
 fn node(&mut self,b:B)->Id{if let Some(&i)=self.intern.get(&b){return i;}let i:Id=self.nodes.len().try_into().unwrap();self.nodes.push(b.clone());self.intern.insert(b,i);i}
 fn not(&mut self,a:Id)->Id{match self.nodes[a as usize]{B::Zero=>1,B::One=>0,B::Not(x)=>x,_=>self.node(B::Not(a))}}
 fn opposite(&self,a:Id,b:Id)->bool{matches!(self.nodes[a as usize],B::Not(x) if x==b)||matches!(self.nodes[b as usize],B::Not(x) if x==a)||(a<2&&b<2&&a!=b)}
 fn factors(&self,a:Id)->Vec<Id>{match &self.nodes[a as usize]{B::One=>vec![],B::And(v)=>v.clone(),_=>vec![a]}}
 fn and(&mut self,a:Id,b:Id)->Id{
  if a==0||b==0{return 0;}if a==1||a==b{return b;}if b==1{return a;}
  let mut v=self.factors(a);v.extend(self.factors(b));v.sort_unstable();v.dedup();
  if v.iter().any(|&x|v.iter().any(|&y|self.opposite(x,y))){return 0;}
  if v.len()>32{let serial=self.cuts;self.cuts+=1;return self.node(B::Cut(serial,a,b));}
  if v.len()==1{return v[0];}self.node(B::And(v))
 }
 fn xor(&mut self,a:Id,b:Id)->Id{if a==b{return 0;}if a==0{return b;}if b==0{return a;}if a==1{return self.not(b);}if b==1{return self.not(a);}if self.opposite(a,b){return 1;}self.node(B::Xor(a.min(b),a.max(b)))}
 fn select(&mut self,old:Id,new:Id,g:Id)->Id{
  if g==0||old==new{return old;}if g==1{return new;}if old==0{return self.and(g,new);}if new==0{let n=self.not(g);return self.and(n,old);}if old==1{let n=self.not(new);let x=self.and(g,n);return self.not(x);}if new==1{let ng=self.not(g);let no=self.not(old);let x=self.and(ng,no);return self.not(x);}self.node(B::Ite(g,old,new))
 }
 #[cfg(test)]fn eval(&self,id:Id,assignment:u64)->bool{match &self.nodes[id as usize]{B::Zero=>false,B::One=>true,B::Input(i)|B::Mr(i)=>assignment>>i&1!=0,B::Not(a)=>!self.eval(*a,assignment),B::And(v)=>v.iter().all(|&a|self.eval(a,assignment)),B::Xor(a,b)=>self.eval(*a,assignment)^self.eval(*b,assignment),B::Ite(g,a,b)=>self.eval(if self.eval(*g,assignment){*b}else{*a},assignment),B::Cut(_,a,b)=>self.eval(*a,assignment)&&self.eval(*b,assignment)}}
}
type Term=Vec<Id>;
#[derive(Clone,Debug,PartialEq,Eq)]struct Support(Vec<Term>);
impl Support{fn no()->Self{Self(vec![])}fn yes()->Self{Self(vec![vec![]])}fn is_no(&self)->bool{self.0.is_empty()}fn is_yes(&self)->bool{self.0.len()==1&&self.0[0].is_empty()}}
struct Bounds{cuts:u64}
impl Bounds{
 fn subset(a:&[Id],b:&[Id])->bool{a.iter().all(|x|b.binary_search(x).is_ok())}
 fn normalize(&mut self,terms:Vec<Term>,d:&BoolDag)->Support{
  let mut out:Vec<Term>=vec![];
  for term in terms{let mut t=vec![];for x in term{if x==0{t=vec![0];break;}t.extend(d.factors(x));}if t.contains(&0){continue;}t.sort_unstable();t.dedup();
   if t.iter().any(|&a|t.iter().any(|&b|d.opposite(a,b))){continue;}
   if t.len()>32{self.cuts+=1;return Support::yes();}if t.is_empty(){return Support::yes();}
   if out.iter().any(|old|Self::subset(old,&t)){continue;}out.retain(|old|!Self::subset(&t,old));out.push(t);if out.len()>16{self.cuts+=1;return Support::yes();}
  }out.sort();Support(out)
 }
 fn guard(&mut self,g:Id,d:&BoolDag)->Support{if g==0{Support::no()}else{self.normalize(vec![d.factors(g)],d)}}
 fn union(&mut self,a:&Support,b:&Support,d:&BoolDag)->Support{if a.is_yes()||b.is_no(){return a.clone();}if b.is_yes()||a.is_no(){return b.clone();}let mut v=a.0.clone();v.extend(b.0.clone());self.normalize(v,d)}
 fn and(&mut self,a:&Support,b:&Support,d:&BoolDag)->Support{if a.is_no()||b.is_no(){return Support::no();}if a.is_yes(){return b.clone();}if b.is_yes(){return a.clone();}let mut v=vec![];for x in &a.0{for y in &b.0{let mut t=x.clone();t.extend(y);v.push(t);}}self.normalize(v,d)}
 fn restrict(&mut self,a:&Support,g:Id,d:&BoolDag)->Support{let b=self.guard(g,d);self.and(a,&b,d)}
 fn reset(&mut self,a:&Support,g:Id,d:&BoolDag)->Support{if g==0||a.is_no(){return a.clone();}if g==1{return Support::no();}let factors=d.factors(g);Support(a.0.iter().filter(|t|!Self::subset(&factors,t)).cloned().collect())}
 #[cfg(test)]fn eval(a:&Support,d:&BoolDag,x:u64)->bool{a.0.iter().any(|t|t.iter().all(|&id|d.eval(id,x)))}
}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn color(v:&[Op])->(Vec<Op>,serde_json::Value,Vec<(u64,u64)>){
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let mut d=BoolDag::new();let mut bounds=Bounds{cuts:0};let mut c=vec![0;nb];let mut q=vec![Support::no();nq];let mut registered=BTreeSet::new();
 for o in v{if o.kind==K::AppendToRegister{if o.q_target.0!=NO{registered.insert(o.q_target.0);q[o.q_target.0 as usize]=Support::yes();}if o.c_target.0!=NO{c[o.c_target.0 as usize]=d.node(B::Input(o.c_target.0));}}}
 let mut free:BTreeSet<u64>=(0..nq as u64).collect();let mut map=vec![NO;nq];let mut owner=vec![NO;nq];for &q in &registered{map[q as usize]=q;owner[q as usize]=q;free.remove(&q);}
 let mut stack=vec![];let mut base=1;let mut out=Vec::with_capacity(v.len()+registered.len());let mut peak=registered.iter().next_back().map_or(0,|q|q+1);let mut live_peak=registered.len();let mut rng_events=0u64;let mut zero_releases=0u64;let mut conditional_clean_releases=0u64;let mut registered_releases=0u64;let mut release_hash=Sha3_256::new();let mut examples=vec![];let mut clean_events=vec![];
 for(i,original)in v.iter().enumerate(){let mut o=*original;
  if matches!(o.kind,K::Register|K::AppendToRegister){out.push(o);continue;}
  if o.kind==K::PushCondition{stack.push(base);base=d.and(base,c[o.c_condition.0 as usize]);out.push(o);continue;}
  if o.kind==K::PopCondition{base=stack.pop().expect("balanced guard stack");out.push(o);continue;}
  let eff=if o.c_condition.0==NO{base}else{d.and(base,c[o.c_condition.0 as usize])};
  let touched:BTreeSet<_>=[o.q_control1.0,o.q_control2.0,o.q_target.0].into_iter().filter(|&x|x!=NO).collect();
  for &role in &touched{if map[role as usize]==NO{assert!(q[role as usize].is_no(),"only proved-zero roles lack a lane");let p=free.pop_first().expect("physical allocation overflow");assert_eq!(owner[p as usize],NO);map[role as usize]=p;owner[p as usize]=role;peak=peak.max(p+1);}}
  live_peak=live_peak.max(nq-free.len());
  for x in [&mut o.q_control1,&mut o.q_control2,&mut o.q_target]{if x.0!=NO{x.0=map[x.0 as usize];}}
  o.validate();out.push(o);
  let(t,a,b,ct)=(original.q_target.0 as usize,original.q_control1.0 as usize,original.q_control2.0 as usize,original.c_target.0 as usize);
  match original.kind{
   K::X=>{let s=bounds.guard(eff,&d);q[t]=bounds.union(&q[t],&s,&d);},
   K::CX=>{let s=bounds.restrict(&q[a],eff,&d);q[t]=bounds.union(&q[t],&s,&d);},
   K::CCX=>{let s=bounds.and(&q[a],&q[b],&d);let s=bounds.restrict(&s,eff,&d);q[t]=bounds.union(&q[t],&s,&d);},
   K::R|K::Hmr=>{
    let was=q[t].clone();q[t]=bounds.reset(&q[t],eff,&d);
    if !was.is_no()&&q[t].is_no()&&eff!=1{conditional_clean_releases+=1;if examples.len()<128{examples.push(serde_json::json!({"op":i,"role":t,"guard_function":eff,"old_support":was.0}));}}
    if original.kind==K::Hmr{let fresh=d.node(B::Mr(rng_events));c[ct]=d.select(c[ct],fresh,eff);}rng_events+=1;
   },
   K::Swap=>{let olda=q[a].clone();let oldt=q[t].clone();if eff==1{q[a]=oldt;q[t]=olda;}else{let sa=bounds.restrict(&olda,eff,&d);let st=bounds.restrict(&oldt,eff,&d);q[a]=bounds.union(&olda,&st,&d);q[t]=bounds.union(&oldt,&sa,&d);}},
   K::BitInvert=>c[ct]=d.xor(c[ct],eff),
   K::BitStore0=>c[ct]=d.select(c[ct],0,eff),
   K::BitStore1=>c[ct]=d.select(c[ct],1,eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::DebugPrint=>{},
   _=>panic!("unhandled {:?}",original.kind)
  }
  for &role in &touched{let r=role as usize;if q[r].is_no(){let p=map[r];assert_ne!(p,NO);assert_eq!(owner[p as usize],role);assert!(free.insert(p));owner[p as usize]=NO;map[r]=NO;zero_releases+=1;clean_events.push((i as u64,role));if registered.contains(&role){registered_releases+=1;}for x in [i as u64,role,eff as u64]{release_hash.update(x.to_le_bytes());}}}
  if i%1_000_000==0{eprintln!("op={i} Q={peak} live={} conditional_clean={conditional_clean_releases} bool_nodes={} support_cuts={}",nq-free.len(),d.nodes.len(),bounds.cuts);}
 }
 assert!(stack.is_empty());let mut output_allocations=0;for &role in &registered{let r=role as usize;if map[r]==NO{assert!(q[r].is_no());let p=free.pop_first().unwrap();map[r]=p;owner[p as usize]=role;peak=peak.max(p+1);output_allocations+=1;}}
 let mut swaps=0;for &role in &registered{let r=role as usize;let p=map[r];if p!=role{let other=owner[r];let mut o=Op::empty();o.kind=K::Swap;o.q_control1=QubitId(p);o.q_target=QubitId(role);o.validate();out.push(o);owner[r]=role;map[r]=role;owner[p as usize]=other;if other!=NO{map[other as usize]=p;}swaps+=1;}}
 assert!(registered.iter().all(|&r|map[r as usize]==r));
 let result=serde_json::json!({"status":"GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE","input_Q":nq,"recolored_Q":peak,"arithmetic_live_peak":live_peak,"input_count":v.len(),"output_count":out.len(),"all_original_operations_retained":true,"all_original_R_and_Hmr_events_retained":true,"all_original_Toffolis_retained":true,"rng_events":rng_events,"zero_role_releases":zero_releases,"conditional_clean_releases":conditional_clean_releases,"registered_releases":registered_releases,"output_zero_allocations":output_allocations,"output_restoration_swaps":swaps,"bool_nodes":d.nodes.len(),"bool_cuts":d.cuts,"support_cuts":bounds.cuts,"support_term_cap":16,"support_factor_cap":32,"release_event_sha3_256":format!("{:x}",release_hash.finalize()),"conditional_clean_examples":examples});(out,result,clean_events)
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let mut v=io::load_ops(&a[1]);assert!(v.len()>96);let tail=v.split_off(v.len()-96);for p in tail.chunks_exact(2){assert_eq!(p[0],p[1]);assert_eq!(p[0].kind,K::X);assert!(p[0].q_target.0<=1);assert_eq!(p[0].c_condition.0,NO);}
 let full_input_hash={let mut x=v.clone();x.extend_from_slice(&tail);hash(&x)};let(out,mut result,events)=color(&v);let mut raw=b"GRCLEAN1".to_vec();raw.extend((v.len()as u64).to_le_bytes());raw.extend(hash(&v).as_bytes());raw.extend((events.len()as u64).to_le_bytes());for(i,q)in events{raw.extend(i.to_le_bytes());raw.extend(q.to_le_bytes());}std::fs::write(format!("{}.clean-events.bin",a[2]),&raw).unwrap();result["clean_event_file_sha3_256"]=serde_json::json!(format!("{:x}",Sha3_256::digest(&raw)));let mut out=out;out.extend(tail);result["input_full_sha3_256"]=serde_json::json!(full_input_hash);result["input_pre_tail_sha3_256"]=serde_json::json!(hash(&v));result["output_full_sha3_256"]=serde_json::json!(hash(&out));result["full_input_count"]=serde_json::json!(v.len()+96);result["full_output_count"]=serde_json::json!(out.len());io::save_ops(&format!("{}.ops.bin",a[2]),&out);std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("Q={} conditional_clean={}",result["recolored_Q"],result["conditional_clean_releases"]);}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{circuit::{BitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 fn fixture_dag()->(BoolDag,Id,Id){let mut d=BoolDag::new();let g=d.node(B::Input(0));let h=d.node(B::Input(1));(d,g,h)}
 #[test]fn boolean_constructors_exhaustive_truth_tables(){let(mut d,g,h)=fixture_dag();let ng=d.not(g);let both=d.and(g,h);let xx=d.xor(g,h);let ids=[0,1,g,h,ng,both,xx];for &a in &ids{for &b in &ids{let ab=d.and(a,b);let xor=d.xor(a,b);for &e in &ids{let selected=d.select(a,b,e);for x in 0..4{assert_eq!(d.eval(ab,x),d.eval(a,x)&&d.eval(b,x));assert_eq!(d.eval(xor,x),d.eval(a,x)^d.eval(b,x));assert_eq!(d.eval(selected,x),d.eval(if d.eval(e,x){b}else{a},x));}}}}}
 #[test]fn support_rules_are_sound_for_all_two_variable_functions(){let(mut d,g,h)=fixture_dag();let ng=d.not(g);let nh=d.not(h);let minterms=[vec![ng,nh],vec![g,nh],vec![ng,h],vec![g,h]];let mut b=Bounds{cuts:0};let supports:Vec<_>=(0..16).map(|mask|b.normalize((0..4).filter(|i|mask>>i&1!=0).map(|i|minterms[i].clone()).collect(),&d)).collect();
  for sa in &supports{for sb in &supports{for st in &supports{for guard in [0,1,g,h]{let sguard=b.guard(guard,&d);let x=b.union(st,&sguard,&d);let ca=b.restrict(sa,guard,&d);let cx=b.union(st,&ca,&d);let ab=b.and(sa,sb,&d);let ab=b.restrict(&ab,guard,&d);let ccx=b.union(st,&ab,&d);let reset=b.reset(st,guard,&d);let olda=sa.clone();let oldt=st.clone();let a_new=if guard==1{oldt.clone()}else{let extra=b.restrict(&oldt,guard,&d);b.union(&olda,&extra,&d)};let t_new=if guard==1{olda.clone()}else{let extra=b.restrict(&olda,guard,&d);b.union(&oldt,&extra,&d)};
   for assign in 0..4{let e=d.eval(guard,assign);let (aa,bb,tt)=(Bounds::eval(sa,&d,assign),Bounds::eval(sb,&d,assign),Bounds::eval(st,&d,assign));for bits in 0..8{let(a,v,t)=(bits&1!=0,bits&2!=0,bits&4!=0);if(a&&!aa)||(v&&!bb)||(t&&!tt){continue;}for(actual,support)in [(t^e,&x),(t^(a&&e),&cx),(t^(a&&v&&e),&ccx),(t&&!e,&reset),(if e{t}else{a},&a_new),(if e{a}else{t},&t_new)]{assert!(!actual||Bounds::eval(support,&d,assign));}}}
  }}}}assert_eq!(b.cuts,0);
 }
 #[test]fn nested_guard_reset_kills_the_entire_support(){let(mut d,g,h)=fixture_dag();let gh=d.and(g,h);let mut b=Bounds{cuts:0};let s=b.guard(gh,&d);assert!(b.reset(&s,g,&d).is_no());assert!(b.reset(&s,gh,&d).is_no());let only_g=b.guard(g,&d);assert!(!b.reset(&only_g,h,&d).is_no());}
 #[test]fn overflow_is_unknown_true_never_false(){let mut d=BoolDag::new();let vars:Vec<_>=(0..40).map(|i|d.node(B::Input(i))).collect();let mut b=Bounds{cuts:0};assert!(b.normalize(vec![vars.clone()],&d).is_yes());assert!(b.cuts>0);let mut and=1;for &v in &vars{and=d.and(and,v);}assert_ne!(and,0);assert!(d.cuts>0);let many:Vec<_>=(0..17).map(|i|vec![vars[i]]).collect();assert!(b.normalize(many,&d).is_yes());}
 fn op(k:K,a:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_target=QubitId(t);o}
 fn qr(q:u64)->Op{let mut o=op(K::AppendToRegister,NO,q);o.r_target=RegisterId(0);o}
 fn cr(c:u64)->Op{let mut o=Op::empty();o.kind=K::AppendToRegister;o.c_target=BitId(c);o.r_target=RegisterId(1);o}
 fn capture_fixture()->Vec<Op>{let mut push=Op::empty();push.kind=K::PushCondition;push.c_condition=BitId(0);let mut pop=Op::empty();pop.kind=K::PopCondition;let mut inv=Op::empty();inv.kind=K::BitInvert;inv.c_target=BitId(0);let mut h=op(K::Hmr,NO,2);h.c_target=BitId(1);vec![qr(0),cr(0),push,op(K::X,NO,2),inv,h,pop,op(K::X,NO,3),op(K::X,NO,3),op(K::R,NO,3)]}
 fn simulate(v:&[Op],qinput:u64,cinput:u64,seed:u64)->(Vec<u64>,Vec<u64>,u64,u64,[u8;64]){let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let mut h=Shake256::default();h.update(&seed.to_le_bytes());let mut r=h.finalize_xof();let mut s=Simulator::new(nq,nb,&mut r);s.qubits[0]=qinput;s.bits[0]=cinput;s.phase=0xaaaa5555aaaa5555;s.apply_iter(v.iter());let x=(s.qubits.clone(),s.bits.clone(),s.phase,s.stats.toffoli_gates);drop(s);let mut tail=[0;64];r.read(&mut tail);(x.0,x.1,x.2,x.3,tail)}
 fn compare(v:&[Op],w:&[Op]){for q in [0,u64::MAX,0x5555555555555555]{for c in [0,u64::MAX,0xaaaaaaaaaaaaaaaa]{for seed in 0..4{let a=simulate(v,q,c,seed);let z=simulate(w,q,c,seed);assert_eq!(a.0[0],z.0[0]);assert_eq!(a.1,z.1);assert_eq!(a.2,z.2);assert_eq!(a.3,z.3);assert_eq!(a.4,z.4);let mut aa=a.0[1..].to_vec();let mut zz=z.0[1..].to_vec();let width=aa.len().max(zz.len());aa.resize(width,0);zz.resize(width,0);aa.sort_unstable();zz.sort_unstable();assert_eq!(aa,zz);}}}}
 #[test]fn captured_guard_survives_mutation_and_frees_a_lane(){let v=capture_fixture();let(w,r,_)=color(&v);assert_eq!(r["recolored_Q"],2);assert_eq!(r["conditional_clean_releases"],1);compare(&v,&w);}
 #[test]fn different_reset_guard_does_not_free_a_dirty_branch(){let mut v=capture_fixture();let mut other=cr(2);other.r_target=RegisterId(2);v.insert(2,other);let pos=v.iter().position(|o|o.kind==K::Hmr).unwrap();v[pos].c_condition=BitId(2);let(_,r,_)=color(&v);assert_eq!(r["conditional_clean_releases"],0);}
 #[test]fn zero_measurements_and_resets_are_retained_even_when_inactive(){let mut h=op(K::Hmr,NO,2);h.c_target=BitId(1);h.c_condition=BitId(2);let mut r=op(K::R,NO,3);r.c_condition=BitId(2);let v=vec![qr(0),cr(0),h,r];let(w,_,_)=color(&v);assert_eq!(w.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count(),2);compare(&v,&w);}
 #[test]fn zero_quantum_controls_do_not_remove_a_scored_Toffoli(){let mut ccx=op(K::CCX,2,0);ccx.q_control2=QubitId(3);let v=vec![qr(0),cr(0),ccx];let(w,r,_)=color(&v);assert_eq!(r["recolored_Q"],3);assert_eq!(w.iter().filter(|o|o.kind==K::CCX).count(),1);compare(&v,&w);}
 #[test]fn late_register_annotations_are_inputs_from_op_zero(){let v=vec![op(K::X,NO,0),qr(0),cr(0)];let(w,_,_)=color(&v);compare(&v,&w);}
}
