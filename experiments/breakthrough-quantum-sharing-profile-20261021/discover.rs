mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId,BitId};
use std::collections::{HashMap,HashSet,BTreeSet};
use sha3::{Digest,Sha3_256};
type E=u32;
// Exact semantic keys for small classical Boolean supports. Large functions
// remain opaque symbols of their actual immutable expressions; no sampling.
#[derive(Clone,Debug,PartialEq,Eq,Hash)]struct SemTruth{atoms:Vec<u32>,table:u64}
impl SemTruth{
 fn mask(n:usize)->u64{if n==6{u64::MAX}else{(1u64<<(1usize<<n))-1}}
 fn complement(&self)->Self{Self{atoms:self.atoms.clone(),table:self.table^Self::mask(self.atoms.len())}}
 fn shrink(mut self)->Self{let mut bit=0;while bit<self.atoms.len(){let n=self.atoms.len();let step=1usize<<bit;let independent=(0..1usize<<n).filter(|r|r&step==0).all(|r|(self.table>>r)&1==(self.table>>(r|step))&1);if independent{let mut out=0u64;for row in 0..1usize<<(n-1){let old=(row&(step-1))|((row&!(step-1))<<1);out|=((self.table>>old)&1)<<row;}self.atoms.remove(bit);self.table=out;}else{bit+=1;}}self}
 fn key(&self)->(Self,u32){let neg=(self.table&1)as u32;if neg==0{(self.clone(),0)}else{(self.complement(),1)}}
}
impl Expr{
 fn semantic(&self,v:u32)->SemTruth{if v<=1{return SemTruth{atoms:vec![],table:v as u64};}let t=&self.truths[(v/2-1)as usize];if v&1==0{t.clone()}else{t.complement()}}
 fn combine_semantic(&self,k:u8,a:u32,b:u32)->Option<SemTruth>{let a=self.semantic(a);let b=self.semantic(b);let mut atoms=a.atoms.clone();atoms.extend_from_slice(&b.atoms);atoms.sort_unstable();atoms.dedup();if atoms.len()>6{return None;}let ap:Vec<_>=a.atoms.iter().map(|v|atoms.binary_search(v).unwrap()).collect();let bp:Vec<_>=b.atoms.iter().map(|v|atoms.binary_search(v).unwrap()).collect();let project=|row:usize,positions:&[usize]|positions.iter().enumerate().fold(0usize,|v,(i,&bit)|v|(((row>>bit)&1)<<i));let mut table=0;for row in 0..1usize<<atoms.len(){let av=(a.table>>project(row,&ap))&1;let bv=(b.table>>project(row,&bp))&1;table|=(if k==1{av&bv}else{av^bv})<<row;}Some(SemTruth{atoms,table}.shrink())}
 fn semantic_node(&mut self,k:u8,a:u32,b:u32)->u32{let summary=self.combine_semantic(k,a,b);if let Some(t)=&summary{if t.atoms.is_empty(){return(t.table&1)as u32;}let(key,neg)=t.key();if let Some(&v)=self.canonical.get(&key){return v^neg;}}let id=self.atom();*self.nodes.last_mut().unwrap()=(k,a,b);if let Some(t)=summary{let(key,neg)=t.key();*self.truths.last_mut().unwrap()=t;self.canonical.insert(key,id^neg);}id}
}

#[derive(Default)]struct Expr{restricting:bool,truths:Vec<SemTruth>,canonical:HashMap<SemTruth,u32>,nodes:Vec<(u8,u32,u32)>,implications:HashMap<(u32,u32),bool>,next:u32,and:HashMap<(u32,u32),u32>,xor:HashMap<(u32,u32),u32>}
impl Expr{
 fn atom(&mut self)->u32{self.next+=2;self.nodes.push((0,0,0));let t=SemTruth{atoms:vec![self.next],table:2};self.truths.push(t.clone());self.canonical.insert(t,self.next);self.next}
 fn and(&mut self,mut a:u32,mut b:u32)->u32{if a==0||b==0{return 0;}if a==1{return b;}if b==1||a==b{return a;}if a==b^1{return 0;}if a>b{std::mem::swap(&mut a,&mut b);}if let Some(&v)=self.and.get(&(a,b)){return v;}if !self.restricting{self.restricting=true;let mut result=None;if let Some(v)=self.cofactor(b,a,6){if v!=b{result=Some(self.and(a,v));}}if result.is_none(){if let Some(v)=self.cofactor(a,b,6){if v!=a{result=Some(self.and(b,v));}}}self.restricting=false;if let Some(v)=result{self.and.insert((a,b),v);return v;}}let v=self.semantic_node(1,a,b);self.and.insert((a,b),v);v}
 fn or(&mut self,a:u32,b:u32)->u32{self.and(a^1,b^1)^1}
 fn xor(&mut self,mut a:u32,mut b:u32)->u32{if a==0{return b;}if b==0{return a;}if a==1{return b^1;}if b==1{return a^1;}if a==b{return 0;}if a==b^1{return 1;}let neg=(a^b)&1;a&=!1;b&=!1;if a>b{std::mem::swap(&mut a,&mut b);}if let Some(&v)=self.xor.get(&(a,b)){return v^neg;}let v=self.semantic_node(2,a,b);self.xor.insert((a,b),v);v^neg}
 fn ite(&mut self,g:u32,new:u32,old:u32)->u32{if g==0||new==old{return old;}if g==1{return new;}if old==0{return self.and(g,new);}if new==0{return self.and(g^1,old);}if old==1{return self.or(g^1,new);}if new==1{return self.or(g,old);}if new==old^1{return self.xor(g,old);}let a=self.and(g,new);let b=self.and(g^1,old);self.or(a,b)}
}
impl Expr{
 fn quick_implies(&self,a:u32,b:u32,depth:usize)->bool{if a==0||b==1||a==b{return true;}if depth==0||a<=1||b==0{return false;}let an=self.nodes[(a/2-1)as usize];if an.0==1{if a&1==0{if self.quick_implies(an.1,b,depth-1)||self.quick_implies(an.2,b,depth-1){return true;}}else if self.quick_implies(an.1^1,b,depth-1)&&self.quick_implies(an.2^1,b,depth-1){return true;}}let bn=self.nodes[(b/2-1)as usize];if bn.0==1{if b&1==0{return self.quick_implies(a,bn.1,depth-1)&&self.quick_implies(a,bn.2,depth-1);}return self.quick_implies(a,bn.1^1,depth-1)||self.quick_implies(a,bn.2^1,depth-1);}false}
 fn implies(&mut self,a:u32,b:u32)->bool{if self.quick_implies(a,b,12){return true;}if let Some(&v)=self.implications.get(&(a,b)){return v;}let root=self.and(a,b^1);let answer=self.zero_truth_table(root);self.implications.insert((a,b),answer);answer}
 fn zero_truth_table(&self,root:u32)->bool{if root<=1{return root==0;}let mut pending=vec![root&!1];let mut visited=BTreeSet::new();let mut atoms=BTreeSet::new();while let Some(id)=pending.pop(){if id<=1||!visited.insert(id){continue;}if visited.len()>4096{return false;}let(k,a,b)=self.nodes[(id/2-1)as usize];if k==0{atoms.insert(id);if atoms.len()>10{return false;}}else{pending.push(a&!1);pending.push(b&!1);}}
  let ord:HashMap<_,_>=atoms.into_iter().enumerate().map(|(i,v)|(v,i)).collect();let cases=1usize<<ord.len();let words=cases.div_ceil(64);let mut table:HashMap<u32,Vec<u64>>=HashMap::new();let get=|lit:u32,table:&HashMap<u32,Vec<u64>>,j:usize|if lit<=1{if lit==1{u64::MAX}else{0}}else{let v=table[&(lit&!1)][j];if lit&1!=0{!v}else{v}};
  for id in visited{let(k,a,b)=self.nodes[(id/2-1)as usize];let mut row=vec![0;words];if k==0{let shift=ord[&id];for assignment in 0..cases{row[assignment/64]|=(((assignment>>shift)&1)as u64)<<(assignment%64);}}else{for j in 0..words{let x=get(a,&table,j);let y=get(b,&table,j);row[j]=if k==1{x&y}else{x^y};}}table.insert(id,row);}
  let last_mask=if cases<64{(1u64<<cases)-1}else{u64::MAX};(0..words).all(|j|get(root,&table,j)&if j+1==words{last_mask}else{u64::MAX}==0)
 }
}
impl Expr{fn cofactor(&mut self,expression:u32,assumed:u32,depth:usize)->Option<u32>{if expression==assumed{return Some(1);}if expression==assumed^1{return Some(0);}if expression<=1||depth==0{return None;}let(k,a,b)=self.nodes[(expression/2-1)as usize];if k==0{return None;}let left=self.cofactor(a,assumed,depth-1);let right=self.cofactor(b,assumed,depth-1);if left.is_none()&&right.is_none(){return None;}let a=left.unwrap_or(a);let b=right.unwrap_or(b);let value=if k==1{self.and(a,b)}else{self.xor(a,b)};Some(value^(expression&1))}}

struct Algebra{inner:Expr}
impl Algebra{fn fresh(&mut self)->E{self.inner.atom()}fn and(&mut self,a:&E,b:&E)->E{self.inner.and(*a,*b)}fn xor(&mut self,a:&E,b:&E)->E{self.inner.xor(*a,*b)}fn select(&mut self,old:&E,new:&E,cond:&E)->E{self.inner.ite(*cond,*new,*old)}}
fn initial_inputs(ops:&[Op],nq:usize,nb:usize,alg:&mut Algebra)->(Vec<E>,Vec<E>){let no=u64::MAX;let(mut q,mut c)=(vec![0;nq],vec![0;nb]);let(mut qs,mut cs)=(HashSet::new(),HashSet::new());for o in ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no&&qs.insert(o.q_target.0){q[o.q_target.0 as usize]=alg.fresh();}if o.c_target.0!=no&&cs.insert(o.c_target.0){c[o.c_target.0 as usize]=alg.fresh();}}}(q,c)}
fn hash(ops:&[Op])->String {
 let mut h=Sha3_256::new();for o in ops {h.update((o.kind as u64).to_le_bytes());
 for v in [o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}
 format!("{:x}",h.finalize())
}
fn make(k:K,c2:u64,c1:u64,t:u64,ct:u64,cc:u64)->Op {
 let mut o=Op::empty();o.kind=k;o.q_control2=QubitId(c2);o.q_control1=QubitId(c1);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o.validate();o
}
// Read-only storage projection: equal reachable quantum values can share a
// representative after exact reversible compression; no emitter exists here.
fn sharing_profile(ops:&[Op])->serde_json::Value{
 let no=u64::MAX;let(nq,nb,_,_)=quantum_ecc::circuit::analyze_ops(ops.iter());let(nq,nb)=(nq as usize,nb as usize);let mut alg=Algebra{inner:Expr::default()};let(mut q,mut c)=initial_inputs(ops,nq,nb,&mut alg);let pinned:HashSet<usize>=ops.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=no).map(|o|o.q_target.0 as usize).collect();let mut classes=HashMap::<u32,[usize;2]>::new();let mut extra=0usize;
 fn change(classes:&mut HashMap<u32,[usize;2]>,extra:&mut usize,value:u32,is_pinned:bool,add:bool){if value==0{return;}let row=classes.entry(value).or_default();if row[0]==0&&row[1]>0{*extra-=1;}let index=usize::from(!is_pinned);if add{row[index]+=1;}else{assert!(row[index]>0);row[index]-=1;}if row[0]==0&&row[1]>0{*extra+=1;}if row==&[0,0]{classes.remove(&value);}}
 for(i,&v)in q.iter().enumerate(){change(&mut classes,&mut extra,v,pinned.contains(&i),true);}
 let(mut base,mut stack)=(1,vec![]);let(mut peak,mut peak_at,mut conservative,mut at_conservative)=(pinned.len()+extra,0,pinned.len()+extra,0);let mut shared_writes=0usize;let mut peak_snapshot=serde_json::Value::Null;
 for(i,o)in ops.iter().enumerate(){if o.kind==K::PushCondition{stack.push(base);base=alg.inner.and(base,c[o.c_condition.0 as usize]);continue;}if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}let g=if o.c_condition.0==no{base}else{alg.inner.and(base,c[o.c_condition.0 as usize])};let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);let mut affected=vec![];if matches!(o.kind,K::X|K::CX|K::CCX|K::Swap|K::R|K::Hmr){affected.push(t);if o.kind==K::Swap{affected.push(a);}}
  let old_pressure=pinned.len()+extra;let needs_copy=affected.iter().filter(|&&j|q[j]!=0&&classes[&q[j]].iter().sum::<usize>()>1).count();shared_writes+=needs_copy;let transient=old_pressure+needs_copy;if transient>conservative{conservative=transient;at_conservative=i;}
  for &j in &affected{change(&mut classes,&mut extra,q[j],pinned.contains(&j),false);}
  match o.kind{
   K::X=>q[t]=alg.inner.xor(q[t],g),K::CX=>{let v=alg.inner.and(q[a],g);q[t]=alg.inner.xor(q[t],v);},K::CCX=>{let v=alg.inner.and(q[a],q[b]);let v=alg.inner.and(g,v);q[t]=alg.inner.xor(q[t],v);},K::Swap=>{let v=alg.inner.xor(q[a],q[t]);let v=alg.inner.and(g,v);q[a]=alg.inner.xor(q[a],v);q[t]=alg.inner.xor(q[t],v);},K::R|K::Hmr=>{q[t]=alg.inner.and(q[t],g^1);if o.kind==K::Hmr{let r=alg.inner.atom();c[ct]=alg.inner.ite(g,r,c[ct]);}},K::BitInvert=>c[ct]=alg.inner.xor(c[ct],g),K::BitStore0=>c[ct]=alg.inner.and(c[ct],g^1),K::BitStore1=>c[ct]=alg.inner.or(c[ct],g),K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},_=>unreachable!()
  }
  for &j in &affected{change(&mut classes,&mut extra,q[j],pinned.contains(&j),true);}
  let pressure=pinned.len()+extra;if pressure>peak{peak=pressure;peak_at=i;let helpers_nonzero=(0..nq).filter(|j|!pinned.contains(j)&&q[*j]!=0).count();peak_snapshot=serde_json::json!({"nonzero_helper_logical_wires":helpers_nonzero,"helper_classes_without_pinned_representative":extra,"copies_compressed":helpers_nonzero-extra});}if pressure>conservative{conservative=pressure;at_conservative=i;}
  if i%1000000==0{eprintln!("SHARING_PROFILE op={i} distinct_peak={peak} conservative_copy_peak={conservative} current={pressure} nodes={}",alg.inner.nodes.len());}
 }
 assert!(stack.is_empty());serde_json::json!({"status":"READ_ONLY_EXACT_VALUE_SHARING_PROJECTION_NOT_A_CIRCUIT_OR_SCORE","original_qubits":nq,"pinned_quantum_register_wires":pinned.len(),"peak_pinned_plus_distinct_nonzero_helper_functions":peak,"peak_at_operation":peak_at,"peak_snapshot":peak_snapshot,"conservative_copy_on_write_projection":conservative,"conservative_peak_at":at_conservative,"shared_target_write_events":shared_writes,"semantic_nodes":alg.inner.nodes.len(),"input_records_sha3":hash(ops),"scope":"Global exact value equality only, initial helperszero and arbitrary registered input/measurement values. Count helper classes not represented by pinned quantum wires; estimate transient copies conservatively. NOT an emitted allocation or proved achievable width. Guard flattening, reversible compression/decompression, repeated-operand gate lowering, shared-target measurement phase/RNG handling and full protected qualification required for any candidate. No point/gate/nonce/benchmark."})
}
#[cfg(test)]mod sharing_tests{use super::*;
 fn metadata()->Vec<Op>{(0..4).map(|q|{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=quantum_ecc::circuit::RegisterId(0);o.q_target=QubitId(q);o}).collect()}
 #[test]fn duplicate_helper_values_share_registered_representative_but_mutation_needs_new_class(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::CX,n,0,4,n,n),make(K::CX,n,0,5,n,n)]);let s=sharing_profile(&ops);assert_eq!(s["original_qubits"],6);assert_eq!(s["peak_pinned_plus_distinct_nonzero_helper_functions"],4);ops.push(make(K::X,n,n,4,n,n));let s=sharing_profile(&ops);assert_eq!(s["peak_pinned_plus_distinct_nonzero_helper_functions"],5);}
 #[test]fn changing_pinned_source_preserves_old_helper_value_as_separate_class(){let n=u64::MAX;let mut ops=metadata();ops.extend([make(K::CX,n,0,4,n,n),make(K::X,n,n,0,n,n)]);let s=sharing_profile(&ops);assert_eq!(s["peak_pinned_plus_distinct_nonzero_helper_functions"],5);assert_eq!(s["conservative_copy_on_write_projection"],5);}
}
#[cfg(test)]mod semantic_algebra_controls{use super::*;
 #[test]fn distributivity_and_unused_support_are_exact(){let mut e=Expr::default();let a=e.atom();let b=e.atom();let ab=e.and(a,b);let anb=e.and(a,b^1);assert_eq!(e.xor(ab,anb),a);let or=e.or(a,b);assert_eq!(e.and(or,a),a);assert_ne!(or,a);}
 #[test]fn above_six_atom_cofactor_has_disabled_negative_control(){fn run(enabled:bool)->(u32,u32){let mut e=Expr::default();e.restricting=!enabled;let mut g=1;let mut old=1;for _ in 0..6{let a=e.atom();g=e.and(g,a);let b=e.atom();old=e.and(old,b);}assert_eq!(e.semantic(g).atoms.len(),6);assert_eq!(e.semantic(old).atoms.len(),6);let r=e.atom();let v=e.ite(g,r,old);let actual=e.and(g,v);let expected=e.and(g,r);(actual,expected)}let no=run(false);assert_ne!(no.0,no.1);let yes=run(true);assert_eq!(yes.0,yes.1);}
 #[test]fn complete_six_atom_expression_truths_match_original_functions(){fn get(e:&Expr,v:u32,assignment:usize,atoms:&[u32])->bool{if v<=1{return v==1;}let(k,a,b)=e.nodes[(v/2-1)as usize];let value=match k{0=>assignment>>atoms.iter().position(|&a|a==v&!1).unwrap()&1!=0,1=>get(e,a,assignment,atoms)&get(e,b,assignment,atoms),_=>get(e,a,assignment,atoms)^get(e,b,assignment,atoms)};value^(v&1!=0)}let mut e=Expr::default();let atoms:Vec<_>=(0..6).map(|_|e.atom()).collect();let mut pool=atoms.clone();let mut seed=0xa8d7135f23649b01u64;for _ in 0..500{seed=seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);let(a,b,g)=(pool[seed as usize%pool.len()],pool[(seed>>17)as usize%pool.len()],pool[(seed>>33)as usize%pool.len()]);let kind=seed%3;let v=match kind{0=>e.and(a,b),1=>e.xor(a,b),_=>e.ite(g,a,b)};for assignment in 0..64{let(a,b,g)=(get(&e,a,assignment,&atoms),get(&e,b,assignment,&atoms),get(&e,g,assignment,&atoms));let want=match kind{0=>a&b,1=>a^b,_=>if g{a}else{b}};assert_eq!(get(&e,v,assignment,&atoms),want);}pool.push(v);if pool.len()>64{pool.remove(6);}}}
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let r=sharing_profile(&ops);std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&r).unwrap()+"\n").unwrap();println!("{r}");}
