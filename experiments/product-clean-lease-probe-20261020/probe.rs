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
 fn impossible(&self,v:&[Id])->bool{if v.contains(&0){return true;}if v.iter().any(|&a|v.iter().any(|&b|self.opposite(a,b))){return true;}v.iter().any(|&x|if let B::Not(child)=self.nodes[x as usize]{self.factors(child).iter().all(|id|v.binary_search(id).is_ok())}else{false})}
 fn factors(&self,a:Id)->Vec<Id>{match &self.nodes[a as usize]{B::One=>vec![],B::And(v)=>v.clone(),_=>vec![a]}}
 fn and(&mut self,a:Id,b:Id)->Id{
  if a==0||b==0{return 0;}if a==1||a==b{return b;}if b==1{return a;}
  let mut v=self.factors(a);v.extend(self.factors(b));v.sort_unstable();v.dedup();
  if self.impossible(&v){return 0;}
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
   if d.impossible(&t){continue;}
   if t.len()>32{self.cuts+=1;return Support::yes();}if t.is_empty(){return Support::yes();}
   if out.iter().any(|old|Self::subset(old,&t)){continue;}out.retain(|old|!Self::subset(&t,old));out.push(t);if out.len()>16{self.cuts+=1;return Support::yes();}
  }out.sort();Support(out)
 }
 fn guard(&mut self,g:Id,d:&BoolDag)->Support{if g==0{Support::no()}else{self.normalize(vec![d.factors(g)],d)}}
 fn union(&mut self,a:&Support,b:&Support,d:&BoolDag)->Support{if a.is_yes()||b.is_no(){return a.clone();}if b.is_yes()||a.is_no(){return b.clone();}let mut v=a.0.clone();v.extend(b.0.clone());self.normalize(v,d)}
 fn and(&mut self,a:&Support,b:&Support,d:&BoolDag)->Support{if a.is_no()||b.is_no(){return Support::no();}if a.is_yes(){return b.clone();}if b.is_yes(){return a.clone();}let mut v=vec![];for x in &a.0{for y in &b.0{let mut t=x.clone();t.extend(y);v.push(t);}}self.normalize(v,d)}
 fn restrict(&mut self,a:&Support,g:Id,d:&BoolDag)->Support{let b=self.guard(g,d);self.and(a,&b,d)}
 fn reset(&mut self,a:&Support,g:Id,d:&mut BoolDag)->Support{if g==0||a.is_no(){return a.clone();}if g==1{return Support::no();}let factors=d.factors(g);let remaining=Support(a.0.iter().filter(|t|!Self::subset(&factors,t)).cloned().collect());let ng=d.not(g);self.restrict(&remaining,ng,d)}
 #[cfg(test)]fn eval(a:&Support,d:&BoolDag,x:u64)->bool{a.0.iter().any(|t|t.iter().all(|&id|d.eval(id,x)))}
}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn color(v:&[Op])->(Vec<Op>,serde_json::Value){
 let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;
 let mut d=BoolDag::new();let mut bounds=Bounds{cuts:0};let mut c=vec![0;nb];let mut q=vec![Support::no();nq];let mut registered=BTreeSet::new();
 for o in v{if o.kind==K::AppendToRegister{if o.q_target.0!=NO{registered.insert(o.q_target.0);q[o.q_target.0 as usize]=Support::yes();}if o.c_target.0!=NO{c[o.c_target.0 as usize]=d.node(B::Input(o.c_target.0));}}}
 let mut free:BTreeSet<u64>=(0..nq as u64).collect();let mut map=vec![NO;nq];let mut owner=vec![NO;nq];for &q in &registered{map[q as usize]=q;owner[q as usize]=q;free.remove(&q);}
 let mut stack=vec![];let mut base=1;let mut out=Vec::with_capacity(v.len()+registered.len());let mut peak=registered.iter().next_back().map_or(0,|q|q+1);let mut live_peak=registered.len();let mut rng_events=0u64;let mut zero_releases=0u64;let mut conditional_clean_releases=0u64;let mut registered_releases=0u64;let mut release_hash=Sha3_256::new();let mut examples=vec![];
 let high=nq-1;let high_enabled=!registered.contains(&(high as u64));let mut high_touches=vec![];let mut positions=vec![vec![];nq];for(i,o)in v.iter().enumerate(){let mut qs=[o.q_control1.0,o.q_control2.0,o.q_target.0];qs.sort_unstable();for(j,x)in qs.into_iter().enumerate(){if x!=NO&&(j==0||x!=qs[j-1]){positions[x as usize].push(i);}}}
 let mut high_epochs=vec![];let mut pending:Option<(usize,usize,Id)>=None;let mut first_full_state=None;
 for(i,original)in v.iter().enumerate(){let mut o=*original;
  if matches!(o.kind,K::Register|K::AppendToRegister){out.push(o);continue;}
  if o.kind==K::PushCondition{stack.push(base);base=d.and(base,c[o.c_condition.0 as usize]);out.push(o);continue;}
  if o.kind==K::PopCondition{base=stack.pop().expect("balanced guard stack");out.push(o);continue;}
  let eff=if o.c_condition.0==NO{base}else{d.and(base,c[o.c_condition.0 as usize])};
  let touched:BTreeSet<_>=[o.q_control1.0,o.q_control2.0,o.q_target.0].into_iter().filter(|&x|x!=NO).collect();
  if high_enabled&&touched.contains(&(high as u64)){high_touches.push(i);if pending.is_none(){assert!(q[high].is_no());pending=Some((i,stack.len(),eff));}}

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
    let was=q[t].clone();q[t]=bounds.reset(&q[t],eff,&mut d);
    if !was.is_no()&&q[t].is_no()&&eff!=1{conditional_clean_releases+=1;if examples.len()<128{examples.push(serde_json::json!({"op":i,"role":t,"guard_function":eff,"old_support":was.0}));}}
    if original.kind==K::Hmr{let fresh=d.node(B::Mr(rng_events));c[ct]=d.select(c[ct],fresh,eff);}rng_events+=1;
   },
   K::Swap=>{let olda=q[a].clone();let oldt=q[t].clone();if eff==1{q[a]=oldt;q[t]=olda;}else if olda==oldt{q[a]=olda;q[t]=oldt;}else{let ng=d.not(eff);let keepa=bounds.restrict(&olda,ng,&d);let keept=bounds.restrict(&oldt,ng,&d);let sa=bounds.restrict(&olda,eff,&d);let st=bounds.restrict(&oldt,eff,&d);q[a]=bounds.union(&keepa,&st,&d);q[t]=bounds.union(&keept,&sa,&d);}},
   K::BitInvert=>c[ct]=d.xor(c[ct],eff),
   K::BitStore0=>c[ct]=d.select(c[ct],0,eff),
   K::BitStore1=>c[ct]=d.select(c[ct],1,eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::DebugPrint=>{},
   _=>panic!("unhandled {:?}",original.kind)
  }
  for &role in &touched{let r=role as usize;if q[r].is_no(){let p=map[r];assert_ne!(p,NO);assert_eq!(owner[p as usize],role);assert!(free.insert(p));owner[p as usize]=NO;map[r]=NO;zero_releases+=1;if registered.contains(&role){registered_releases+=1;}for x in [i as u64,role,eff as u64]{release_hash.update(x.to_le_bytes());}}}
  if first_full_state.is_none()&&nq-free.len()==nq{first_full_state=Some(i);}
  if high_enabled&&touched.contains(&(high as u64))&&q[high].is_no(){let(start,depth,guard)=pending.take().unwrap();let mut donor_count=0;let mut examples=vec![];
   for role in 0..nq{if role==high||registered.contains(&(role as u64)){continue;}let p=&positions[role];let at=p.partition_point(|&x|x<start);if at==p.len()||p[at]>i{donor_count+=1;if examples.len()<8{examples.push(role);}}}
   let touch_count=high_touches.partition_point(|&x|x<=i)-high_touches.partition_point(|&x|x<start);
   high_epochs.push(serde_json::json!({"first":start,"last_proved_clean":i,"touches":touch_count,"ops":i-start+1,"start_scope_depth":depth,"end_scope_depth":stack.len(),"first_guard_id":guard,"last_guard_id":eff,"untouched_nonABI_donor_count":donor_count,"first8_untouched_donors":examples}));
  }
  if i%1_000_000==0{eprintln!("op={i} Q={peak} live={} conditional_clean={conditional_clean_releases} bool_nodes={} support_cuts={}",nq-free.len(),d.nodes.len(),bounds.cuts);}
 }
 assert!(stack.is_empty());let mut output_allocations=0;for &role in &registered{let r=role as usize;if map[r]==NO{assert!(q[r].is_no());let p=free.pop_first().unwrap();map[r]=p;owner[p as usize]=role;peak=peak.max(p+1);output_allocations+=1;}}
 let mut swaps=0;for &role in &registered{let r=role as usize;let p=map[r];if p!=role{let other=owner[r];let mut o=Op::empty();o.kind=K::Swap;o.q_control1=QubitId(p);o.q_target=QubitId(role);o.validate();out.push(o);owner[r]=role;map[r]=role;owner[p as usize]=other;if other!=NO{map[other as usize]=p;}swaps+=1;}}
 assert!(registered.iter().all(|&r|map[r as usize]==r));
 let result=serde_json::json!({"status":"TIGHT_GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE","lease_probe":{"highest_role":high,"enabled_nonABI":high_enabled,"touches":high_touches.len(),"first_full_width_post_state":first_full_state,"epochs":high_epochs,"trailing_unclosed":pending,"scope":"Read-only support boundaries and untouched-donor counts. Unknown donor values; no lease, new width or resource score."},"input_Q":nq,"recolored_Q":peak,"arithmetic_live_peak":live_peak,"input_count":v.len(),"output_count":out.len(),"all_original_operations_retained":true,"all_original_R_and_Hmr_events_retained":true,"all_original_Toffolis_retained":true,"rng_events":rng_events,"zero_role_releases":zero_releases,"conditional_clean_releases":conditional_clean_releases,"registered_releases":registered_releases,"output_zero_allocations":output_allocations,"output_restoration_swaps":swaps,"bool_nodes":d.nodes.len(),"bool_cuts":d.cuts,"support_cuts":bounds.cuts,"support_term_cap":16,"support_factor_cap":32,"release_event_sha3_256":format!("{:x}",release_hash.finalize()),"conditional_clean_examples":examples});(out,result)
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let mut v=io::load_ops(&a[1]);assert_eq!(hash(&v),a[3]);let tail=v.split_off(v.len()-96);for p in tail.chunks_exact(2){assert_eq!(p[0],p[1]);assert_eq!(p[0].kind,K::X);assert_eq!(p[0].c_condition.0,NO);}let(out,mut report)=color(&v);let mut out=out;out.extend(tail);report["input_full_sha3_256"]=serde_json::json!(a[3]);report["output_full_sha3_256"]=serde_json::json!(hash(&out));std::fs::write(&a[2],serde_json::to_string_pretty(&report).unwrap()).unwrap();}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{circuit::{BitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
 fn fixture_dag()->(BoolDag,Id,Id){let mut d=BoolDag::new();let g=d.node(B::Input(0));let h=d.node(B::Input(1));(d,g,h)}
 #[test]fn boolean_constructors_exhaustive_truth_tables(){let(mut d,g,h)=fixture_dag();let ng=d.not(g);let both=d.and(g,h);let xx=d.xor(g,h);let ids=[0,1,g,h,ng,both,xx];for &a in &ids{for &b in &ids{let ab=d.and(a,b);let xor=d.xor(a,b);for &e in &ids{let selected=d.select(a,b,e);for x in 0..4{assert_eq!(d.eval(ab,x),d.eval(a,x)&&d.eval(b,x));assert_eq!(d.eval(xor,x),d.eval(a,x)^d.eval(b,x));assert_eq!(d.eval(selected,x),d.eval(if d.eval(e,x){b}else{a},x));}}}}}
 #[test]fn support_rules_are_sound_for_all_two_variable_functions(){let(mut d,g,h)=fixture_dag();let ng=d.not(g);let nh=d.not(h);let minterms=[vec![ng,nh],vec![g,nh],vec![ng,h],vec![g,h]];let mut b=Bounds{cuts:0};let supports:Vec<_>=(0..16).map(|mask|b.normalize((0..4).filter(|i|mask>>i&1!=0).map(|i|minterms[i].clone()).collect(),&d)).collect();
  for sa in &supports{for sb in &supports{for st in &supports{for guard in [0,1,g,h]{let sguard=b.guard(guard,&d);let x=b.union(st,&sguard,&d);let ca=b.restrict(sa,guard,&d);let cx=b.union(st,&ca,&d);let ab=b.and(sa,sb,&d);let ab=b.restrict(&ab,guard,&d);let ccx=b.union(st,&ab,&d);let reset=b.reset(st,guard,&mut d);let olda=sa.clone();let oldt=st.clone();let ng=d.not(guard);let a_new=if guard==1{oldt.clone()}else{let extra=b.restrict(&oldt,guard,&d);let keep=b.restrict(&olda,ng,&d);b.union(&keep,&extra,&d)};let t_new=if guard==1{olda.clone()}else{let extra=b.restrict(&olda,guard,&d);let keep=b.restrict(&oldt,ng,&d);b.union(&keep,&extra,&d)};
   for assign in 0..4{let e=d.eval(guard,assign);let (aa,bb,tt)=(Bounds::eval(sa,&d,assign),Bounds::eval(sb,&d,assign),Bounds::eval(st,&d,assign));for bits in 0..8{let(a,v,t)=(bits&1!=0,bits&2!=0,bits&4!=0);if(a&&!aa)||(v&&!bb)||(t&&!tt){continue;}for(actual,support)in [(t^e,&x),(t^(a&&e),&cx),(t^(a&&v&&e),&ccx),(t&&!e,&reset),(if e{t}else{a},&a_new),(if e{a}else{t},&t_new)]{assert!(!actual||Bounds::eval(support,&d,assign));}}}
  }}}}assert_eq!(b.cuts,0);
 }
 #[test]fn nested_guard_reset_kills_the_entire_support(){let(mut d,g,h)=fixture_dag();let gh=d.and(g,h);let mut b=Bounds{cuts:0};let s=b.guard(gh,&d);assert!(b.reset(&s,g,&mut d).is_no());assert!(b.reset(&s,gh,&mut d).is_no());let only_g=b.guard(g,&d);assert!(!b.reset(&only_g,h,&mut d).is_no());}
 #[test]fn overflow_is_unknown_true_never_false(){let mut d=BoolDag::new();let vars:Vec<_>=(0..40).map(|i|d.node(B::Input(i))).collect();let mut b=Bounds{cuts:0};assert!(b.normalize(vec![vars.clone()],&d).is_yes());assert!(b.cuts>0);let mut and=1;for &v in &vars{and=d.and(and,v);}assert_ne!(and,0);assert!(d.cuts>0);let many:Vec<_>=(0..17).map(|i|vec![vars[i]]).collect();assert!(b.normalize(many,&d).is_yes());}
 fn op(k:K,a:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_target=QubitId(t);o}
 fn qr(q:u64)->Op{let mut o=op(K::AppendToRegister,NO,q);o.r_target=RegisterId(0);o}
 fn cr(c:u64)->Op{let mut o=Op::empty();o.kind=K::AppendToRegister;o.c_target=BitId(c);o.r_target=RegisterId(1);o}
 fn capture_fixture()->Vec<Op>{let mut push=Op::empty();push.kind=K::PushCondition;push.c_condition=BitId(0);let mut pop=Op::empty();pop.kind=K::PopCondition;let mut inv=Op::empty();inv.kind=K::BitInvert;inv.c_target=BitId(0);let mut h=op(K::Hmr,NO,2);h.c_target=BitId(1);vec![qr(0),cr(0),push,op(K::X,NO,2),inv,h,pop,op(K::X,NO,3),op(K::X,NO,3),op(K::R,NO,3)]}
 fn simulate(v:&[Op],qinput:u64,cinput:u64,seed:u64)->(Vec<u64>,Vec<u64>,u64,u64,[u8;64]){let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let mut h=Shake256::default();h.update(&seed.to_le_bytes());let mut r=h.finalize_xof();let mut s=Simulator::new(nq,nb,&mut r);s.qubits[0]=qinput;s.bits[0]=cinput;s.phase=0xaaaa5555aaaa5555;s.apply_iter(v.iter());let x=(s.qubits.clone(),s.bits.clone(),s.phase,s.stats.toffoli_gates);drop(s);let mut tail=[0;64];r.read(&mut tail);(x.0,x.1,x.2,x.3,tail)}
 fn compare(v:&[Op],w:&[Op]){for q in [0,u64::MAX,0x5555555555555555]{for c in [0,u64::MAX,0xaaaaaaaaaaaaaaaa]{for seed in 0..4{let a=simulate(v,q,c,seed);let z=simulate(w,q,c,seed);assert_eq!(a.0[0],z.0[0]);assert_eq!(a.1,z.1);assert_eq!(a.2,z.2);assert_eq!(a.3,z.3);assert_eq!(a.4,z.4);let mut aa=a.0[1..].to_vec();let mut zz=z.0[1..].to_vec();let width=aa.len().max(zz.len());aa.resize(width,0);zz.resize(width,0);aa.sort_unstable();zz.sort_unstable();assert_eq!(aa,zz);}}}}
 #[test]fn captured_guard_survives_mutation_and_frees_a_lane(){let v=capture_fixture();let(w,r)=color(&v);assert_eq!(r["recolored_Q"],2);assert_eq!(r["conditional_clean_releases"],1);compare(&v,&w);}
 #[test]fn different_reset_guard_does_not_free_a_dirty_branch(){let mut v=capture_fixture();let mut other=cr(2);other.r_target=RegisterId(2);v.insert(2,other);let pos=v.iter().position(|o|o.kind==K::Hmr).unwrap();v[pos].c_condition=BitId(2);let(_,r)=color(&v);assert_eq!(r["conditional_clean_releases"],0);}
 #[test]fn zero_measurements_and_resets_are_retained_even_when_inactive(){let mut h=op(K::Hmr,NO,2);h.c_target=BitId(1);h.c_condition=BitId(2);let mut r=op(K::R,NO,3);r.c_condition=BitId(2);let v=vec![qr(0),cr(0),h,r];let(w,_)=color(&v);assert_eq!(w.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count(),2);compare(&v,&w);}
 #[test]fn zero_quantum_controls_do_not_remove_a_scored_Toffoli(){let mut ccx=op(K::CCX,2,0);ccx.q_control2=QubitId(3);let v=vec![qr(0),cr(0),ccx];let(w,r)=color(&v);assert_eq!(r["recolored_Q"],3);assert_eq!(w.iter().filter(|o|o.kind==K::CCX).count(),1);compare(&v,&w);}
 #[test]fn late_register_annotations_are_inputs_from_op_zero(){let v=vec![op(K::X,NO,0),qr(0),cr(0)];let(w,_)=color(&v);compare(&v,&w);}
}

#[cfg(test)]mod tight_controls{use super::*;use quantum_ecc::{circuit::{BitId,RegisterId},sim::Simulator};use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
fn compare(v:&[Op],w:&[Op]){for qi in [0,u64::MAX,0x5555555555555555]{for ci in [0,u64::MAX,0xaaaaaaaaaaaaaaaa]{for seed in 0u64..4{let calc=|v:&[Op]|{let nq=v.iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&q|q!=NO).max().unwrap_or(0)as usize+1;let mut h=Shake256::default();Update::update(&mut h,&seed.to_le_bytes());let mut rng=h.finalize_xof();let mut sim=Simulator::new(nq,nb,&mut rng);sim.qubits[0]=qi;sim.bits[0]=ci;sim.phase=0x5555aaaa5555aaaa;sim.apply_iter(v.iter());let mut scratch=sim.qubits[1..].to_vec();scratch.resize(8,0);scratch.sort_unstable();let result=(sim.qubits[0],sim.bits.clone(),sim.phase,sim.stats.toffoli_gates,scratch);drop(sim);let mut continuation=[0u8;64];rng.read(&mut continuation);(result,continuation)};assert_eq!(calc(v),calc(w));}}}}
fn op(k:K,a:u64,t:u64)->Op{let mut x=Op::empty();x.kind=k;x.q_control1=QubitId(a);x.q_target=QubitId(t);x}
fn regs()->Vec<Op>{let mut q=op(K::AppendToRegister,NO,0);q.r_target=RegisterId(0);let mut c=Op::empty();c.kind=K::AppendToRegister;c.c_target=BitId(0);c.r_target=RegisterId(1);vec![q,c]}
fn invert()->Op{let mut x=Op::empty();x.kind=K::BitInvert;x.c_target=BitId(0);x}
fn reset(q:u64)->Op{let mut x=op(K::R,NO,q);x.c_condition=BitId(0);x}
#[test]fn complementary_resets_prove_clean_without_an_unconditional_reset(){let mut v=regs();v.extend([reset(0),invert(),reset(0),op(K::X,NO,3),op(K::X,NO,3),op(K::R,NO,3)]);let(w,r)=color(&v);assert_eq!(r["recolored_Q"],1);assert!(r["conditional_clean_releases"].as_u64().unwrap()>0);compare(&v,&w);}
#[test]fn conditional_swap_transfers_the_dirty_support_to_the_other_branch(){let mut v=regs();let mut swap=op(K::Swap,0,2);swap.c_condition=BitId(0);v.extend([swap,invert(),reset(0),op(K::X,NO,3),op(K::X,NO,3),op(K::R,NO,3),invert(),reset(2)]);let(w,r)=color(&v);assert_eq!(r["recolored_Q"],2);assert!(r["conditional_clean_releases"].as_u64().unwrap()>=2);compare(&v,&w);}
#[test]fn negated_conjunction_conflict_is_recognized(){let mut d=BoolDag::new();let a=d.node(B::Input(0));let b=d.node(B::Input(1));let ab=d.and(a,b);let nab=d.not(ab);assert_eq!(d.and(ab,nab),0);let mut bounds=Bounds{cuts:0};assert!(bounds.normalize(vec![vec![a,b,nab]],&d).is_no());}
}

#[cfg(test)]mod lease_tests{
 use super::*;use quantum_ecc::circuit::{BitId,QubitId};
 fn op(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);if k==K::Hmr{o.c_target=BitId(1);}o}
 fn input()->Op{let mut o=Op::empty();o.kind=K::AppendToRegister;o.c_target=BitId(0);o.r_target.0=0;o}
 #[test]fn conditional_writes_and_matching_reset_close_a_global_zero_epoch(){let mut x=op(K::X,NO,NO,4);x.c_condition=BitId(0);let mut h=op(K::Hmr,NO,NO,4);h.c_condition=BitId(0);let(_,r)=color(&[input(),x,h]);let p=&r["lease_probe"];assert_eq!(p["epochs"].as_array().unwrap().len(),1);assert!(p["trailing_unclosed"].is_null());assert_eq!(p["epochs"][0]["last_proved_clean"],2);}
 #[test]fn partial_reset_cannot_close_an_unconditionally_dirty_epoch(){let mut h=op(K::Hmr,NO,NO,4);h.c_condition=BitId(0);let(_,r)=color(&[input(),op(K::X,NO,NO,4),h]);assert!(r["lease_probe"]["epochs"].as_array().unwrap().is_empty());assert!(!r["lease_probe"]["trailing_unclosed"].is_null());}
 #[test]fn intervening_phase_touches_are_not_idle_donors(){let(_,r)=color(&[op(K::X,NO,NO,4),op(K::CCZ,1,2,3),op(K::R,NO,NO,4)]);let e=&r["lease_probe"]["epochs"][0];assert_eq!(e["untouched_nonABI_donor_count"],1);assert_eq!(e["first8_untouched_donors"],serde_json::json!([0]));}
}
