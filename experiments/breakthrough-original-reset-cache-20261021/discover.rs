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

// Fingerprints propose pairs only. No rewrite is accepted on fingerprints:
// local_proof uses full exact expressions and arbitrary values at the cut.
type H=u128;
struct Fingerprints{next:u64,products:HashMap<[H;3],H>}
impl Fingerprints{
 fn fresh(&mut self)->H{self.next+=1;let mut h=Sha3_256::new();h.update(b"pareto-discovery-not-proof-v1");h.update(self.next.to_le_bytes());u128::from_le_bytes(h.finalize()[..16].try_into().unwrap())}
 fn and(&mut self,a:H,b:H)->H{if a==0||b==0{return 0;}if a==1{return b;}if b==1||a==b{return a;}let mut k=[a,b,1^a^b];k.sort();if k[0]==0{return 0;}if let Some(&p)=self.products.get(&k){return p;}let p=self.fresh();self.products.insert(k,p);p}
 fn select(&mut self,old:H,new:H,cond:H)->H{old^self.and(cond,old^new)}
}
fn local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{if last-first>200000{return false;}
 let no=u64::MAX;let mut alg=Algebra{next:1,products:HashMap::new(),cap:65536,truncations:0};
 let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();
 let f=ops[first];let product=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);let expected=if f.c_condition.0==no{product}else{alg.and(&product,&c[f.c_condition.0 as usize])};
 let mut base=vec![0];let mut stack=vec![];
 for o in &ops[first..last]{
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=match stack.pop(){Some(x)=>x,None=>return false};continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},
   _=>return false,
  }
 }
 let o=ops[last];let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};stack.is_empty()&&base==vec![0]&&actual==expected
}
fn exact_proof_from(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize,start:usize)->bool{if last-first>200000{return false;}
 let no=u64::MAX;let mut alg=Algebra{next:1,products:HashMap::new(),cap:65536,truncations:0};
 let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();
 let mut expected=None;
 let mut base=vec![0];let mut stack=vec![];
 for (i,o) in ops[start..last].iter().enumerate(){
  if start+i==first{if !stack.is_empty()||base!=vec![0]{return false;}let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);expected=Some(if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])});}
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=match stack.pop(){Some(x)=>x,None=>return false};continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},
   _=>return false,
  }
 }
 let o=ops[last];let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};stack.is_empty()&&base==vec![0]&&Some(actual)==expected
}

fn exact_zero_donors_from(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize,start:usize)->Option<Vec<bool>>{if last-first>200000{return None;}
 let no=u64::MAX;let mut alg=Algebra{next:1,products:HashMap::new(),cap:65536,truncations:0};
 let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();
 let mut expected=None;let mut zeros=None;
 let mut base=vec![0];let mut stack=vec![];
 for (i,o) in ops[start..last].iter().enumerate(){
  if start+i==first{if !stack.is_empty()||base!=vec![0]{return None;}zeros=Some(q.iter().map(|e|e.is_empty()).collect());let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);expected=Some(if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])});}
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=match stack.pop(){Some(x)=>x,None=>return None};continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},
   _=>return None,
  }
 }
 let o=ops[last];let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};if stack.is_empty()&&base==vec![0]&&Some(actual)==expected{zeros}else{None}
}

fn context_start(ops:&[Op],first:usize)->usize{
 let floor=first.saturating_sub(16384);let mut depth=0usize;let mut start=first;
 for i in(floor..first).rev(){match ops[i].kind{K::PopCondition=>depth+=1,K::PushCondition=>{if depth==0{break;}depth-=1;},_=>{}}if depth==0{start=i;}}
 start
}
fn context_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{
 if local_proof(ops,first,last,nq,nb){return true;}
 let start=context_start(ops,first);start<first&&exact_proof_from(ops,first,last,nq,nb,start)
}
fn tri_and(a:i8,b:i8)->i8{if a==0||b==0{0}else if a==1&&b==1{1}else{-1}}
fn legacy_main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3,"input output-prefix");let no=u64::MAX;let ops=io::load_ops(&args[1]);let out=&args[2];
 let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|x|*x!=no).max().unwrap()as usize+1;let extra=std::env::var("RESEARCH_EXTRA_DONORS").expect("explicit donor budget").parse::<usize>().unwrap();assert!([0,16,64].contains(&extra));let nq=nq+extra;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let mut f=Fingerprints{next:0,products:HashMap::new()};let mut q=vec![0;nq];let mut c=vec![0;nb];let mut cv=vec![0i8;nb];let mut clean=vec![true;nq];
 for o in &ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no{let t=o.q_target.0 as usize;q[t]=f.fresh();clean[t]=false;}if o.c_target.0!=no{let ct=o.c_target.0 as usize;c[ct]=f.fresh();cv[ct]=-1;}}}
 let mut base=1;let mut stack=vec![];let mut cb=1i8;let mut cs=vec![];let mut scope=Vec::<usize>::new();let mut lease_scopes=Vec::<Vec<usize>>::new();let mut saved_proxy=0f64;
 let mut touches=vec![None;nq];let mut busy=vec![None;nq];let mut endpoints=HashSet::new();let mut uses:HashMap<(Vec<usize>,H),(usize,Op)>=HashMap::new();let mut leases=vec![];let mut rejected=vec![];let mut proposed=0;
 for(i,o)in ops.iter().enumerate(){
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::AppendToRegister{continue;}
  if o.kind==K::PushCondition{scope.push(i);stack.push(base);base=f.and(base,c[o.c_condition.0 as usize]);cs.push(cb);cb=tri_and(cb,cv[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{scope.pop().unwrap();base=stack.pop().unwrap();cb=cs.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base}else{f.and(base,c[o.c_condition.0 as usize])};let ce=if o.c_condition.0==no{cb}else{tri_and(cb,cv[o.c_condition.0 as usize])};
  // Donor proof uses exact three-valued guards, never fingerprints.
  if o.kind==K::CCX&&ce!=0{
   let product=f.and(q[a],q[b]);let key=(scope.clone(),f.and(eff,product));
   if let Some(&(first,p))=uses.get(&key){if !endpoints.contains(&first)&&!endpoints.contains(&i){
    let idle=|d:usize|d!=a&&d!=b&&d!=t&&touches[d].is_none_or(|j|j<first)&&busy[d].is_none_or(|j|j<first);
    let mut donor=(0..nq).find(|&d|idle(d)&&clean[d]);let mut context_zero_proved=false;
    if donor.is_none(){let cut=context_start(&ops,first);if cut<first&&(0..nq).any(|d|idle(d)&&touches[d].is_some_and(|j|j>=cut)){if let Some(zero)=exact_zero_donors_from(&ops,first,i,nq,nb,cut){donor=(0..nq).find(|&d|idle(d)&&zero[d]);context_zero_proved=donor.is_some();}}}
    if let Some(d)=donor{proposed+=1;if context_zero_proved||context_proof(&ops,first,i,nq,nb){leases.push([first as u64,i as u64,d as u64,p.q_control2.0,p.q_control1.0,p.q_target.0,o.q_control2.0,o.q_control1.0,o.q_target.0]);lease_scopes.push(scope.clone());saved_proxy+=2f64.powi(-(scope.len()as i32)-i32::from(o.c_condition.0!=no));busy[d]=Some(i);endpoints.insert(first);endpoints.insert(i);}else{rejected.push([first,i]);}}
   }}uses.insert(key,(i,*o));
  }
  if ce!=0{
   for w in [o.q_control1.0,o.q_control2.0,o.q_target.0]{if w!=no{touches[w as usize]=Some(i);}}
   if o.q_target.0!=no&&matches!(o.kind,K::X|K::CX|K::CCX|K::Swap|K::R|K::Hmr){clean[t]=matches!(o.kind,K::R|K::Hmr)&&ce==1;}
   if o.kind==K::Swap{clean[a]=false;}
   if o.c_target.0!=no{
    let old=cv[ct];cv[ct]=match o.kind{K::BitStore0=>if ce==1||old==0{0}else{-1},K::BitStore1=>if ce==1||old==1{1}else{-1},K::BitInvert=>if ce==1&&old!=-1{1-old}else{-1},K::Hmr=>-1,_=>old};
   }
  }
  match o.kind{
   K::X=>q[t]^=eff,
   K::CX=>q[t]^=f.and(q[a],eff),
   K::CCX=>{let v=f.and(q[a],q[b]);q[t]^=f.and(v,eff);},
   K::Swap=>{let v=f.and(q[a]^q[t],eff);q[a]^=v;q[t]^=v;},
   K::R|K::Hmr=>{q[t]=f.select(q[t],0,eff);if o.kind==K::Hmr{let v=f.fresh();c[ct]=f.select(c[ct],v,eff);}},
   K::BitInvert=>c[ct]^=eff,
   K::BitStore0=>c[ct]=f.select(c[ct],0,eff),
   K::BitStore1=>c[ct]=f.select(c[ct],1,eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::DebugPrint=>{},_=>panic!("unhandled op")
  }
  if i%2000000==0{eprintln!("op {i}, proposed {proposed}, proven {}, rejected {}",leases.len(),rejected.len());}
 }
 let result=serde_json::json!({"status":"LOCAL_EXACT_PROOFS_PASS_DIAGNOSTIC_ONLY","input":args[1],"input_count":ops.len(),"input_sha3_256":hash(&ops),"peak_qubits":nq,"classical_bits":nb,"leases":leases,"lease_scopes":lease_scopes,"depth_weight_saving_diagnostic":saved_proxy,"zero_products":[],"linear_products":{},"proposed":proposed,"rejected_unproven":rejected,"proof":"Within the same lexical outer scope, cofactor the common outer guard true; false skips both endpoints with donor zero. Effective per-op products proved with full expressions and arbitrary cut data/classical values/measurement outcomes. Clean donors and no touches/overlap proved conservatively. Fingerprints only nominate. Depth weights diagnostic only."});
 std::fs::write(format!("{out}.json"),serde_json::to_string_pretty(&result).unwrap()).unwrap();eprintln!("SUMMARY proposed={proposed} proven={} rejected={}",leases.len(),rejected.len());
 let rewritten=rewrite_ops(ops,&leases,nb);io::save_ops(&format!("{out}.ops.bin"),&rewritten);
}
fn rewrite_ops(ops:Vec<Op>,leases:&[[u64;9]],nb:usize)->Vec<Op>{
 let no=u64::MAX;let starts:HashMap<_,_>=leases.iter().map(|s|(s[0]as usize,s)).collect();let ends:HashMap<_,_>=leases.iter().map(|s|(s[1]as usize,s)).collect();let mut rewritten=Vec::with_capacity(ops.len()+leases.len()*5);
 for(i,o)in ops.into_iter().enumerate(){if let Some(s)=starts.get(&i){let mut fill=o;fill.q_target=QubitId(s[2]);rewritten.push(fill);rewritten.push(make(K::CX,no,s[2],s[5],no,o.c_condition.0));}else if let Some(s)=ends.get(&i){
  if o.c_condition.0!=no{rewritten.push(make(K::PushCondition,no,no,no,no,o.c_condition.0));}
  rewritten.push(make(K::CX,no,s[2],s[8],no,no));rewritten.push(make(K::Hmr,no,no,s[2],nb as u64,no));rewritten.push(make(K::CZ,no,s[6],s[7],no,nb as u64));
  if o.c_condition.0!=no{rewritten.push(make(K::PopCondition,no,no,no,no,no));}
 }else{rewritten.push(o);}}
 rewritten
}

#[cfg(test)]mod tests{
 use super::*;
 #[test]fn local_proof_accepts_symmetric_triple_rejects_fault(){let n=u64::MAX;let mut ops=vec![make(K::CCX,0,1,2,n,n),make(K::CX,n,0,1,n,n),make(K::X,n,n,1,n,n),make(K::CCX,0,1,3,n,n)];assert!(local_proof(&ops,0,3,4,0));ops.remove(2);assert!(!local_proof(&ops,0,2,4,0));}
 #[test]fn unknown_guard_stays_unknown(){assert_eq!(tri_and(1,-1),-1);assert_eq!(tri_and(0,-1),0);}
}


#[cfg(test)]mod guarded_tests{
 use super::*;use quantum_ecc::circuit::RegisterId;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 #[test]fn effective_per_op_guards_are_proved_and_mismatches_rejected(){let n=u64::MAX;let a=make(K::CCX,0,1,2,n,0);let b=make(K::CCX,0,1,3,n,0);assert!(local_proof(&[a,b],0,1,4,2));let mut bad=b;bad.c_condition=BitId(1);assert!(!local_proof(&[a,bad],0,1,4,2));let inv=make(K::BitInvert,n,n,n,0,n);assert!(!local_proof(&[a,inv,b],0,2,4,2));}
 fn fixture(inner:bool,mutate_outer:bool)->(Vec<Op>,usize,usize){let n=u64::MAX;let mut ops=Vec::new();for q in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);ops.push(o);}for b in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(1);o.c_target=BitId(b);ops.push(o);}ops.push(make(K::R,n,n,4,n,n));ops.push(make(K::PushCondition,n,n,n,n,0));let first=ops.len();ops.push(make(K::CCX,0,1,2,n,if inner{1}else{n}));if mutate_outer{ops.push(make(K::BitInvert,n,n,n,0,n));}ops.push(make(K::CX,n,0,1,n,n));ops.push(make(K::X,n,n,1,n,n));let last=ops.len();ops.push(make(K::CCX,0,1,3,n,if inner{1}else{n}));ops.push(make(K::PopCondition,n,n,n,n,n));(ops,first,last)}
 #[test]fn guarded_cache_preserves_all_values_phase_and_executed_cost_and_detects_bad_repair(){let mut caught=0;
  for inner in[false,true]{for mutate in[false,true]{let(ops,first,last)=fixture(inner,mutate);assert!(local_proof(&ops,first,last,5,2));let f=ops[first];let l=ops[last];let lease=[first as u64,last as u64,4,f.q_control2.0,f.q_control1.0,f.q_target.0,l.q_control2.0,l.q_control1.0,l.q_target.0];let out=rewrite_ops(ops.clone(),&[lease],2);let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();
   for pattern in[0u8,255,0xa5,0x5a]{let mut ra=Fixed(pattern);let mut rb=Fixed(pattern);let mut rf=Fixed(pattern);let mut a=Simulator::new(5,3,&mut ra);let mut b=Simulator::new(5,3,&mut rb);let mut bad=Simulator::new(5,3,&mut rf);for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}a.bits[0]|=((lane>>4&1)as u64)<<lane;a.bits[1]|=((lane>>5&1)as u64)<<lane;}b.qubits.clone_from(&a.qubits);bad.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);bad.bits.clone_from(&a.bits);let effective=a.bits[0]&if inner{a.bits[1]}else{u64::MAX};a.apply_iter(ops.iter());b.apply_iter(out.iter());bad.apply_iter(faulty.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits[..2],b.bits[..2]);assert_eq!(a.phase,b.phase);assert_eq!(a.stats.toffoli_gates-b.stats.toffoli_gates,effective.count_ones()as u64);assert_eq!(b.qubits[4],0);caught+=u64::from(a.phase!=bad.phase);}
  }}assert!(caught>0);
 }
}


#[cfg(test)]mod context_tests{
 use super::*;use quantum_ecc::circuit::RegisterId;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 fn fixture(outer:bool,inner:bool)->(Vec<Op>,usize,usize){let n=u64::MAX;let mut ops=vec![];for q in 0..5{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);ops.push(o);}for b in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(1);o.c_target=BitId(b);ops.push(o);}ops.push(make(K::R,n,n,5,n,n));if outer{ops.push(make(K::PushCondition,n,n,n,n,0));}ops.push(make(K::R,n,n,2,n,n));ops.push(make(K::CX,n,0,2,n,n));let first=ops.len();ops.push(make(K::CCX,0,1,3,n,if inner{1}else{n}));ops.push(make(K::X,n,n,4,n,n));let last=ops.len();ops.push(make(K::CCX,2,1,4,n,if inner{1}else{n}));if outer{ops.push(make(K::PopCondition,n,n,n,n,n));}(ops,first,last)}
 #[test]fn context_proves_prepared_alias_but_rejects_broken_relation(){for outer in[false,true]{for inner in[false,true]{let(mut ops,first,last)=fixture(outer,inner);assert!(!local_proof(&ops,first,last,6,2));assert!(context_proof(&ops,first,last,6,2));ops[first-1].q_control1=QubitId(1);assert!(!context_proof(&ops,first,last,6,2));}}}
 #[test]fn context_never_crosses_enclosing_scope_or_unbalanced_guard(){let n=u64::MAX;let ops=vec![make(K::R,n,n,2,n,n),make(K::CX,n,0,2,n,n),make(K::PushCondition,n,n,n,n,0),make(K::CCX,0,1,3,n,n),make(K::CCX,2,1,4,n,n),make(K::PopCondition,n,n,n,n,n)];assert_eq!(context_start(&ops,3),3);assert!(!context_proof(&ops,3,4,6,1));let bad=vec![make(K::CCX,0,1,2,n,n),make(K::PopCondition,n,n,n,n,n),make(K::CCX,0,1,3,n,n)];assert!(!context_proof(&bad,0,2,4,0));}
 #[test]fn context_lease_preserves_full_basis_phase_guards_and_cost_detects_missing_phase(){let mut caught=0;for outer in[false,true]{for inner in[false,true]{let(ops,first,last)=fixture(outer,inner);assert!(context_proof(&ops,first,last,6,2));let f=ops[first];let l=ops[last];let lease=[first as u64,last as u64,5,f.q_control2.0,f.q_control1.0,f.q_target.0,l.q_control2.0,l.q_control1.0,l.q_target.0];let out=rewrite_ops(ops.clone(),&[lease],2);let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();for pattern in[0u8,255,0xa5,0x5a]{for high in[false,true]{let mut ra=Fixed(pattern);let mut rb=Fixed(pattern);let mut rf=Fixed(pattern);let mut a=Simulator::new(6,3,&mut ra);let mut b=Simulator::new(6,3,&mut rb);let mut bad=Simulator::new(6,3,&mut rf);for lane in 0..64{for q in 0..5{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}a.bits[0]|=((lane>>5&1)as u64)<<lane;a.bits[1]|=((if high{lane^0b10101}else{lane}>>4&1)as u64)<<lane;}b.qubits.clone_from(&a.qubits);bad.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);bad.bits.clone_from(&a.bits);let eff=(if outer{a.bits[0]}else{u64::MAX})&(if inner{a.bits[1]}else{u64::MAX});a.apply_iter(ops.iter());b.apply_iter(out.iter());bad.apply_iter(faulty.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits[..2],b.bits[..2]);assert_eq!(a.phase,b.phase);assert_eq!(a.stats.toffoli_gates-b.stats.toffoli_gates,eff.count_ones()as u64);assert_eq!(b.qubits[5],0);caught+=u64::from(a.phase!=bad.phase);}}}}assert!(caught>0);}
}

#[cfg(test)]mod donor_zero_tests{
use super::*;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
fn fixture(outer:bool)->(Vec<Op>,usize,usize){let n=u64::MAX;let mut ops=vec![];if outer{ops.push(make(K::PushCondition,n,n,n,n,0));}ops.extend([make(K::R,n,n,5,n,n),make(K::X,n,n,5,n,n),make(K::X,n,n,5,n,n),make(K::R,n,n,2,n,n),make(K::CX,n,0,2,n,n)]);let first=ops.len();ops.push(make(K::CCX,0,1,3,n,n));ops.push(make(K::X,n,n,4,n,n));let last=ops.len();ops.push(make(K::CCX,2,1,4,n,n));if outer{ops.push(make(K::PopCondition,n,n,n,n,n));}(ops,first,last)}
#[test]fn exact_context_zero_requires_reset_and_all_cancellations(){for outer in[false,true]{let(ops,first,last)=fixture(outer);let cut=context_start(&ops,first);let zeros=exact_zero_donors_from(&ops,first,last,6,1,cut).unwrap();assert!(zeros[5]);assert!(!zeros[0]&&!zeros[1]);let mut bad=ops.clone();bad[usize::from(outer)+2].kind=K::Z;bad[usize::from(outer)+2].validate();assert!(!exact_zero_donors_from(&bad,first,last,6,1,cut).unwrap()[5]);let mut bad=ops.clone();bad[usize::from(outer)].kind=K::X;bad[usize::from(outer)].validate();assert!(!exact_zero_donors_from(&bad,first,last,6,1,cut).unwrap()[5]);}}
#[test]fn context_zero_borrow_preserves_values_phase_and_zero_width_and_detects_bad_fix(){let mut caught=0;for outer in[false,true]{let(ops,first,last)=fixture(outer);let cut=context_start(&ops,first);assert!(exact_zero_donors_from(&ops,first,last,6,1,cut).unwrap()[5]);let f=ops[first];let l=ops[last];let lease=[first as u64,last as u64,5,f.q_control2.0,f.q_control1.0,f.q_target.0,l.q_control2.0,l.q_control1.0,l.q_target.0];let out=rewrite_ops(ops.clone(),&[lease],1);assert!(out.iter().flat_map(|o|[o.q_control2.0,o.q_control1.0,o.q_target.0]).all(|q|q==u64::MAX||q<6));let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();for pattern in[0u8,255,0xa5,0x5a]{let mut ra=Fixed(pattern);let mut rb=Fixed(pattern);let mut rf=Fixed(pattern);let mut a=Simulator::new(6,2,&mut ra);let mut b=Simulator::new(6,2,&mut rb);let mut bad=Simulator::new(6,2,&mut rf);for lane in 0..64{for q in 0..6{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}a.bits[0]|=((lane>>5&1)as u64)<<lane;}b.qubits.clone_from(&a.qubits);bad.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);bad.bits.clone_from(&a.bits);a.apply_iter(ops.iter());b.apply_iter(out.iter());bad.apply_iter(faulty.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.phase,b.phase);assert_eq!(a.bits[..1],b.bits[..1]);caught+=u64::from(a.phase!=bad.phase);}}assert!(caught>0);}
}

fn reset_probe_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize,start:usize,probe:Op)->bool{if last-first>200000{return false;}
 let no=u64::MAX;let mut alg=Algebra{next:1,products:HashMap::new(),cap:65536,truncations:0};
 let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();
 let mut expected=None;
 let mut base=vec![0];let mut stack=vec![];
 for (i,o) in ops[start..last].iter().enumerate(){
  if start+i==first{if !stack.is_empty()||base!=vec![0]{return false;}let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);expected=Some(if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])});}
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=match stack.pop(){Some(x)=>x,None=>return false};continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};if eff.is_empty(){continue;}
  match o.kind{
   K::X=>q[t]=alg.xor(&q[t],&eff),
   K::CX=>{let v=alg.and(&q[a],&eff);q[t]=alg.xor(&q[t],&v);},
   K::CCX=>{let v=alg.and(&q[a],&q[b]);let v=alg.and(&v,&eff);q[t]=alg.xor(&q[t],&v);},
   K::Swap=>{let v=alg.xor(&q[a],&q[t]);let v=alg.and(&v,&eff);q[a]=alg.xor(&q[a],&v);q[t]=alg.xor(&q[t],&v);},
   K::R|K::Hmr=>{q[t]=alg.select(&q[t],&vec![],&eff);if o.kind==K::Hmr{let v=alg.fresh();c[ct]=alg.select(&c[ct],&v,&eff);}},
   K::BitInvert=>c[ct]=alg.xor(&c[ct],&eff),
   K::BitStore0=>c[ct]=alg.select(&c[ct],&vec![],&eff),
   K::BitStore1=>c[ct]=alg.select(&c[ct],&vec![0],&eff),
   K::Neg|K::Z|K::CZ|K::CCZ|K::Register|K::AppendToRegister|K::DebugPrint=>{},
   _=>return false,
  }
 }
 let o=probe;let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);let actual=if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])};stack.is_empty()&&base==vec![0]&&Some(actual)==expected
}

// Reuse the ORIGINAL donor reset and its ORIGINAL random word. No new RNG event.
// row = original nine-column lease, reset index, phase-probe per-op condition.
fn delayed_rewrite(ops:&[Op],rows:&[[u64;11]],nb:usize)->Vec<Op>{
 let no=u64::MAX;let starts:HashMap<_,_>=rows.iter().map(|s|(s[0]as usize,s)).collect();let ends:HashMap<_,_>=rows.iter().map(|s|(s[1]as usize,s)).collect();let resets:HashMap<_,_>=rows.iter().map(|s|(s[9]as usize,s)).collect();assert_eq!(starts.len(),rows.len());assert_eq!(ends.len(),rows.len());assert_eq!(resets.len(),rows.len());let mut out=Vec::with_capacity(ops.len()+4*rows.len());
 for(i,&o)in ops.iter().enumerate(){
  if let Some(s)=starts.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);let mut fill=o;fill.q_target=QubitId(s[2]);fill.validate();out.push(fill);out.push(make(K::CX,no,s[2],s[5],no,o.c_condition.0));}
  else if let Some(s)=ends.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);out.push(make(K::CX,no,s[2],s[8],no,o.c_condition.0));}
  else if let Some(s)=resets.get(&i){assert!(matches!(o.kind,K::R|K::Hmr));assert_eq!(o.q_target.0,s[2]);assert_eq!(o.c_condition.0,no);let mut reset=o;let bit=if o.kind==K::Hmr{o.c_target.0}else{nb as u64};assert_ne!(bit,s[10]);reset.kind=K::Hmr;reset.c_target=BitId(bit);reset.validate();out.push(reset);out.push(make(K::PushCondition,no,no,no,no,bit));out.push(make(K::CZ,no,s[6],s[7],no,s[10]));out.push(make(K::PopCondition,no,no,no,no,no));}
  else{out.push(o);}
 }out
}
fn delayed_conflict(a:&[u64;11],b:&[u64;11])->bool{
 let overlaps=|lo:u64,hi:u64,x:u64|lo<=x&&x<=hi;
 (a[2]==b[2]&&a[0]<=b[9]&&b[0]<=a[9])||([a[6],a[7]].contains(&b[2])&&overlaps(b[0],b[9],a[9]))||([b[6],b[7]].contains(&a[2])&&overlaps(a[0],a[9],b[9]))
}
fn main(){
 legacy_main();let args:Vec<_>=std::env::args().collect();let ops=io::load_ops(&args[1]);let proof:serde_json::Value=serde_json::from_slice(&std::fs::read(format!("{}.json",args[2])).unwrap()).unwrap();let nq=proof["peak_qubits"].as_u64().unwrap()as usize;let nb=proof["classical_bits"].as_u64().unwrap()as usize;let leases:Vec<[u64;9]>=serde_json::from_value(proof["leases"].clone()).unwrap();let scopes:Vec<Vec<usize>>=serde_json::from_value(proof["lease_scopes"].clone()).unwrap();let no=u64::MAX;
 let by_end:HashMap<usize,usize>=leases.iter().enumerate().map(|(j,s)|(s[1]as usize,j)).collect();let mut next=vec![None;nq];let mut at_reset=vec![None;leases.len()];
 for(i,o)in ops.iter().enumerate().rev(){if let Some(&j)=by_end.get(&i){at_reset[j]=next[leases[j][2]as usize];}if !matches!(o.kind,K::AppendToRegister|K::Register){for w in[o.q_control2.0,o.q_control1.0,o.q_target.0]{if w!=no{next[w as usize]=Some(i);}}}}
 let wanted:HashSet<usize>=at_reset.iter().flatten().copied().collect();let mut reset_scopes=HashMap::new();let mut scope=vec![];for(i,o)in ops.iter().enumerate(){if wanted.contains(&i){reset_scopes.insert(i,scope.clone());}match o.kind{K::PushCondition=>scope.push(i),K::PopCondition=>{scope.pop().unwrap();},_=>{}}}assert!(scope.is_empty());
 let mut accepted=vec![];let mut rejected=vec![];
 for(j,s)in leases.iter().enumerate(){
  let Some(reset)=at_reset[j]else{rejected.push(serde_json::json!({"lease":j,"reason":"no later donor touch"}));continue;};let o=ops[reset];
  let reason=if !matches!(o.kind,K::R|K::Hmr)||o.q_target.0!=s[2]{Some("next donor use is not a reset")}else if o.c_condition.0!=no{Some("reset has per-op guard")}else if reset_scopes[&reset]!=scopes[j]{Some("reset outside same captured lexical scope")}else if o.kind==K::Hmr&&o.c_target==ops[s[1]as usize].c_condition{Some("measurement overwrites phase-probe guard")}else{None};
  if let Some(reason)=reason{rejected.push(serde_json::json!({"lease":j,"reset":reset,"reason":reason}));continue;}
  let probe=ops[s[1]as usize];let cut=context_start(&ops,s[0]as usize);if !reset_probe_proof(&ops,s[0]as usize,reset,nq,nb,cut,probe){rejected.push(serde_json::json!({"lease":j,"reset":reset,"reason":"exact captured product not available at reset"}));continue;}
  let row=[s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],s[8],reset as u64,probe.c_condition.0];if accepted.iter().any(|old|delayed_conflict(old,&row)){rejected.push(serde_json::json!({"lease":j,"reset":reset,"reason":"extended borrow or extra phase probe conflicts"}));continue;}accepted.push(row);
 }
 let out=delayed_rewrite(&ops,&accepted,nb);let mut kinds_original:Vec<_>=ops.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).map(|o|(o.q_target.0,o.c_condition.0)).collect();let kinds_new:Vec<_>=out.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).map(|o|(o.q_target.0,o.c_condition.0)).collect();assert_eq!(kinds_original,kinds_new);kinds_original.clear();let(nq2,nb2,_,_)=quantum_ecc::circuit::analyze_ops(out.iter());assert_eq!(nq2 as usize,nq);
 let result=serde_json::json!({"status":"DELAYED_ORIGINAL_RESET_CACHE_COMPONENT_NOT_SCORED","input_records_sha3":hash(&ops),"output_records_sha3":hash(&out),"original_leases":leases.len(),"accepted":accepted,"rejected":rejected,"original_qubits":nq,"emitted_qubits":nq2,"emitted_classical_bits":nb2,"original_measurement_events":kinds_new.len(),"same_measurement_count_wire_guard_order":true,"scope":"Existing native9 exact endpoint/zero-donor proofs plus exact product proof through first original donor reset, same captured outer scope, unchanged original random-word order. Additional probes included in borrow conflict checks. No point inputs/finalgate/nonce/benchmark or resource score. Full protected development required."});std::fs::write(format!("{}-DELAYED.json",args[2]),serde_json::to_string_pretty(&result).unwrap()+"\n").unwrap();io::save_ops(&format!("{}-DELAYED.ops.bin",args[2]),&out);println!("DELAYED accepted={} nominees={}",accepted.len(),leases.len());
}
#[cfg(test)]mod delayed_tests{
 use super::*;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
 struct Words{pattern:u64,at:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){assert_eq!(b.len(),8);let w=self.pattern.rotate_left((self.at%64)as u32);b.copy_from_slice(&w.to_le_bytes());self.at+=1;}}
 fn fixture(outer:bool,inner:bool,hmr:bool)->(Vec<Op>,[u64;11]){let n=u64::MAX;let mut ops=vec![];for q in 0..4{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=quantum_ecc::circuit::RegisterId(0);o.q_target=QubitId(q);ops.push(o);}for c in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=quantum_ecc::circuit::RegisterId(1);o.c_target=BitId(c);ops.push(o);}ops.push(make(K::R,n,n,4,n,n));if outer{ops.push(make(K::PushCondition,n,n,n,n,0));}let first=ops.len();let cc=if inner{1}else{n};ops.extend([make(K::CCX,0,1,2,n,cc),make(K::CX,n,0,1,n,n),make(K::X,n,n,1,n,n)]);let end=ops.len();ops.push(make(K::CCX,0,1,3,n,cc));ops.push(make(K::X,n,n,5,n,n));let reset=ops.len();ops.push(make(if hmr{K::Hmr}else{K::R},n,n,4,if hmr{0}else{n},n));if outer{ops.push(make(K::PopCondition,n,n,n,n,n));}let row=[first as u64,end as u64,4,0,1,2,0,1,3,reset as u64,cc];(ops,row)}
 #[test]fn original_rng_values_phase_classical_and_exact_saving_preserved_missing_repair_detected(){let mut caught=0;for outer in[false,true]{for inner in[false,true]{for hmr in[false,true]{let(ops,row)=fixture(outer,inner,hmr);assert!(context_proof(&ops,row[0]as usize,row[1]as usize,6,2));assert!(reset_probe_proof(&ops,row[0]as usize,row[9]as usize,6,2,context_start(&ops,row[0]as usize),ops[row[1]as usize]));let out=delayed_rewrite(&ops,&[row],2);let fault:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();for pattern in[0,u64::MAX,0xa55a_dd33_1188_ee01]{let(mut ra,mut rb,mut rf)=(Words{pattern,at:0},Words{pattern,at:0},Words{pattern,at:0});let(mut a,mut b,mut f)=(Simulator::new(6,3,&mut ra),Simulator::new(6,3,&mut rb),Simulator::new(6,3,&mut rf));for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}for c in 0..2{a.bits[c]|=((lane>>(c+4)&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);f.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);f.bits.clone_from(&a.bits);let active=(if outer{a.bits[0]}else{u64::MAX})&(if inner{a.bits[1]}else{u64::MAX});a.apply_iter(ops.iter());b.apply_iter(out.iter());f.apply_iter(fault.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits[..2],b.bits[..2]);assert_eq!(a.phase,b.phase);assert_eq!(a.stats.toffoli_gates-b.stats.toffoli_gates,active.count_ones()as u64);caught+=usize::from(a.phase!=f.phase);drop((a,b,f));assert_eq!(ra.at,rb.at);assert_eq!(ra.at,rf.at);}}}}assert!(caught>0);}
 #[test]fn changed_reset_product_and_extended_donor_probe_overlap_are_rejected(){let(mut ops,row)=fixture(false,true,false);let reset=row[9]as usize;ops.insert(reset,make(K::BitInvert,u64::MAX,u64::MAX,u64::MAX,1,u64::MAX));assert!(!reset_probe_proof(&ops,row[0]as usize,reset+1,6,2,context_start(&ops,row[0]as usize),ops[row[1]as usize]));let a=[1,2,4,0,1,2,0,1,3,8,u64::MAX];let b=[3,4,5,0,1,2,4,1,3,6,u64::MAX];assert!(delayed_conflict(&a,&b));let mut good=b;good[6]=2;assert!(!delayed_conflict(&a,&good));}
}
