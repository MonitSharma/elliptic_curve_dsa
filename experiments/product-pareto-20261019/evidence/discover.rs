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
fn local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{
 let no=u64::MAX;let mut alg=Algebra{next:1,products:HashMap::new(),cap:65536,truncations:0};
 let mut q:Vec<E>=(0..nq).map(|_|alg.fresh()).collect();let mut c:Vec<E>=(0..nb).map(|_|alg.fresh()).collect();
 let f=ops[first];let expected=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);
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
 let o=ops[last];stack.is_empty()&&base==vec![0]&&alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize])==expected
}
fn tri_and(a:i8,b:i8)->i8{if a==0||b==0{0}else if a==1&&b==1{1}else{-1}}
fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3,"input output-prefix");let no=u64::MAX;let ops=io::load_ops(&args[1]);let out=&args[2];
 let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|x|*x!=no).max().unwrap()as usize+1;
 let mut f=Fingerprints{next:0,products:HashMap::new()};let mut q=vec![0;nq];let mut c=vec![0;nb];let mut cv=vec![0i8;nb];let mut clean=vec![true;nq];
 for o in &ops{if o.kind==K::AppendToRegister{if o.q_target.0!=no{let t=o.q_target.0 as usize;q[t]=f.fresh();clean[t]=false;}if o.c_target.0!=no{let ct=o.c_target.0 as usize;c[ct]=f.fresh();cv[ct]=-1;}}}
 let mut base=1;let mut stack=vec![];let mut cb=1i8;let mut cs=vec![];
 let mut touches=vec![None;nq];let mut busy=vec![None;nq];let mut endpoints=HashSet::new();let mut uses:HashMap<[H;3],(usize,Op)>=HashMap::new();let mut leases=vec![];let mut rejected=vec![];let mut proposed=0;
 for(i,o)in ops.iter().enumerate(){
  let t=o.q_target.0 as usize;let a=o.q_control1.0 as usize;let b=o.q_control2.0 as usize;let ct=o.c_target.0 as usize;
  if o.kind==K::AppendToRegister{continue;}
  if o.kind==K::PushCondition{stack.push(base);base=f.and(base,c[o.c_condition.0 as usize]);cs.push(cb);cb=tri_and(cb,cv[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().unwrap();cb=cs.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base}else{f.and(base,c[o.c_condition.0 as usize])};let ce=if o.c_condition.0==no{cb}else{tri_and(cb,cv[o.c_condition.0 as usize])};
  // Donor proof uses exact three-valued guards, never fingerprints.
  if o.kind==K::CCX&&stack.is_empty()&&o.c_condition.0==no{
   let mut key=[q[a],q[b],1^q[a]^q[b]];key.sort();
   if let Some(&(first,p))=uses.get(&key){if !endpoints.contains(&first)&&!endpoints.contains(&i){
    let donor=(0..nq).find(|&d|d!=a&&d!=b&&d!=t&&clean[d]&&touches[d].is_none_or(|j|j<first)&&busy[d].is_none_or(|j|j<first));
    if let Some(d)=donor{proposed+=1;if local_proof(&ops,first,i,nq,nb){leases.push([first as u64,i as u64,d as u64,p.q_control2.0,p.q_control1.0,p.q_target.0,o.q_control2.0,o.q_control1.0,o.q_target.0]);busy[d]=Some(i);endpoints.insert(first);endpoints.insert(i);}else{rejected.push([first,i]);}}
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
 let result=serde_json::json!({"status":"LOCAL_EXACT_PROOFS_PASS_DIAGNOSTIC_ONLY","input":args[1],"input_count":ops.len(),"input_sha3_256":hash(&ops),"peak_qubits":nq,"classical_bits":nb,"leases":leases,"zero_products":[],"linear_products":{},"proposed":proposed,"rejected_unproven":rejected,"proof":"Each product equality proved with full expressions, arbitrary cut inputs and arbitrary measurement outcomes. Clean donors proved by exact constant guards and no intervening possible touches. Fingerprints only nominate pairs."});
 std::fs::write(format!("{out}.json"),serde_json::to_string_pretty(&result).unwrap()).unwrap();eprintln!("SUMMARY proposed={proposed} proven={} rejected={}",leases.len(),rejected.len());
 let starts:HashMap<_,_>=leases.iter().map(|s|(s[0]as usize,s)).collect();let ends:HashMap<_,_>=leases.iter().map(|s|(s[1]as usize,s)).collect();let mut rewritten=Vec::with_capacity(ops.len()+leases.len()*3);
 for(i,o)in ops.into_iter().enumerate(){if let Some(s)=starts.get(&i){let mut fill=o;fill.q_target=QubitId(s[2]);rewritten.push(fill);rewritten.push(make(K::CX,no,s[2],s[5],no,no));}else if let Some(s)=ends.get(&i){rewritten.push(make(K::CX,no,s[2],s[8],no,no));rewritten.push(make(K::Hmr,no,no,s[2],nb as u64,no));rewritten.push(make(K::CZ,no,s[6],s[7],no,nb as u64));}else{rewritten.push(o);}}
 io::save_ops(&format!("{out}.ops.bin"),&rewritten);
}

#[cfg(test)]mod tests{
 use super::*;
 #[test]fn local_proof_accepts_symmetric_triple_rejects_fault(){let n=u64::MAX;let mut ops=vec![make(K::CCX,0,1,2,n,n),make(K::CX,n,0,1,n,n),make(K::X,n,n,1,n,n),make(K::CCX,0,1,3,n,n)];assert!(local_proof(&ops,0,3,4,0));ops.remove(2);assert!(!local_proof(&ops,0,2,4,0));}
 #[test]fn unknown_guard_stays_unknown(){assert_eq!(tri_and(1,-1),-1);assert_eq!(tri_and(0,-1),0);}
}

