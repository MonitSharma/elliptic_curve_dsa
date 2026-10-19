mod io;
use quantum_ecc::circuit::{Op, OperationType as K, QubitId, BitId};
use std::collections::{HashMap, HashSet};
use sha3::{Digest,Sha3_256};

// Exact XOR expressions. Atom 0 means one; all other atoms denote Boolean
// functions. HashMap hashes are only indices: full keys are compared on lookup.
type E = Vec<u32>;
type Triple = [E;3];
#[derive(Clone)]struct Episode {start:usize,fill:Op,value:E,reads:Vec<(usize,u64)>}
struct Finished {ep:Episode,end:usize,phase:Option<usize>,valid:bool}
struct Unwrapper {active:Vec<Option<Episode>>,finished:Vec<Finished>,bits:HashMap<u64,usize>,inputs:HashSet<u64>}
impl Unwrapper {
 fn observe(&mut self,i:usize,o:&Op,eff:&E,q:&[E],c:&[E],alg:&mut Algebra){
  let no=u64::MAX;let always=eff==&vec![0];
  // A removed measurement must feed exactly its matching phase repair and
  // no other operation before an unconditional overwrite or end of stream.
  if let Some(&f)=self.bits.get(&o.c_condition.0){
   let ok=o.kind==K::CZ&&self.finished[f].phase.is_none()&&eff==&c[o.c_condition.0 as usize]
    &&alg.and(&q[o.q_control1.0 as usize],&q[o.q_target.0 as usize])==self.finished[f].ep.value;
   if ok{self.finished[f].phase=Some(i);}else{self.finished[f].valid=false;}
  }
  if eff.is_empty(){return;}
  if o.c_target.0!=no {
   if let Some(f)=self.bits.remove(&o.c_target.0){if !always{self.finished[f].valid=false;}}
  }
  let new=if always&&(o.kind==K::CX||o.kind==K::CCX)&&q[o.q_target.0 as usize].is_empty(){
   let value=if o.kind==K::CX{q[o.q_control1.0 as usize].clone()}else{alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize])};
   Some(Episode{start:i,fill:*o,value,reads:vec![]})
  }else{None};
  for wire in [o.q_control1.0,o.q_control2.0,o.q_target.0] {
   if wire==no{continue;}let w=wire as usize;
   if let Some(mut ep)=self.active[w].take(){
    if o.kind==K::Hmr&&o.q_target.0==wire&&always&&!ep.reads.is_empty()&&!self.inputs.contains(&o.c_target.0){
     let f=self.finished.len();self.finished.push(Finished{ep,end:i,phase:None,valid:true});self.bits.insert(o.c_target.0,f);
    }else if o.kind==K::CX&&o.q_control1.0==wire&&always&&ep.reads.len()<64{
     let current=if ep.fill.kind==K::CX{q[ep.fill.q_control1.0 as usize].clone()}else{alg.and(&q[ep.fill.q_control1.0 as usize],&q[ep.fill.q_control2.0 as usize])};
     if current==ep.value{ep.reads.push((i,o.q_target.0));self.active[w]=Some(ep);}
    }
    // Every other non-dead touch invalidates this proposed unwrapping.
   }
  }
  if let Some(ep)=new{self.active[o.q_target.0 as usize]=Some(ep);}
 }
 fn metadata_read(&mut self,o:&Op){if let Some(&f)=self.bits.get(&o.c_condition.0){self.finished[f].valid=false;}}
}
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
 let argv:Vec<_>=std::env::args().collect();assert_eq!(argv.len(),4);
 let ops=io::load_ops(&argv[1]);let rows:Vec<[u64;9]>=serde_json::from_str(&std::fs::read_to_string(&argv[2]).unwrap()).unwrap();
 let no=u64::MAX;let nq=ops.iter().flat_map(|o|[o.q_target.0,o.q_control1.0,o.q_control2.0]).filter(|&q|q!=no).max().unwrap()as usize+1;
 let nb=ops.iter().flat_map(|o|[o.c_target.0,o.c_condition.0]).filter(|&q|q!=no).max().unwrap()as usize+1;
 let body_hash=hash(&ops[..ops.len()-96]);assert_eq!(body_hash,"c143e90580bb0c6f6a12996a50147c179c4fdfe3a50d8af85350bf9e6d755e04");
 let mut alg=Algebra{next:1,products:HashMap::new(),cap:1024,truncations:0};
 let(mut q,mut c)=initial_inputs(&ops,nq,nb,&mut alg);let mut stack:Vec<E>=vec![];let mut base=vec![0];
 let starts:HashMap<_,_>=rows.iter().enumerate().map(|(j,s)|(s[0]as usize,j)).collect();
 let ends:HashMap<_,_>=rows.iter().enumerate().map(|(j,s)|(s[1]as usize,j)).collect();
 let mut active=HashMap::new();let mut reports:Vec<serde_json::Value>=rows.iter().map(|_|serde_json::json!({})).collect();
 for(i,o)in ops.iter().enumerate(){
  if matches!(o.kind,K::Register|K::AppendToRegister){continue;}
  if o.kind==K::PushCondition{stack.push(base.clone());base=alg.and(&base,&c[o.c_condition.0 as usize]);continue;}
  if o.kind==K::PopCondition{base=stack.pop().unwrap();continue;}
  let eff=if o.c_condition.0==no{base.clone()}else{alg.and(&base,&c[o.c_condition.0 as usize])};
  let(t,a,b,ct)=(o.q_target.0 as usize,o.q_control1.0 as usize,o.q_control2.0 as usize,o.c_target.0 as usize);
  let product=if o.kind==K::CCX{Some(alg.and(&q[a],&q[b]))}else{None};
  if let Some(&j)=starts.get(&i){
   let s=rows[j];assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);
   let mut qs=HashSet::new();let mut cs=HashSet::new();
   for p in &ops[i..=s[1]as usize]{for w in [p.q_control2.0,p.q_control1.0,p.q_target.0]{if w!=no{qs.insert(w);}}for w in [p.c_condition.0,p.c_target.0]{if w!=no{cs.insert(w);}}}
   let bq:std::collections::BTreeMap<_,_>=qs.iter().map(|&w|(w.to_string(),q[w as usize].clone())).collect();
   let bc:std::collections::BTreeMap<_,_>=cs.iter().map(|&w|(w.to_string(),c[w as usize].clone())).collect();
   let data=serde_json::json!({"status":"EXACT_ABSTRACT_BOUNDARY_OVERAPPROXIMATION","lease":j+1,"first":s[0],"last":s[1],"base_pre_tail_sha3_256":body_hash,"q":bq,"c":bc,"base":base,"stack":stack,"next_atom":alg.next,"expression_cap":alg.cap,"truncations_so_far":alg.truncations});
   let path=format!("{}/boundary-{:02}.json",argv[3],j+1);std::fs::write(&path,serde_json::to_vec(&data).unwrap()).unwrap();
   reports[j]=serde_json::json!({"lease":j+1,"start_guard_true":eff==vec![0],"donor_clean":q[s[2]as usize].is_empty(),"donor_untouched":true,"boundary_file":path});
   assert!(active.insert(s[2],j).is_none());
  }
  if !eff.is_empty(){for w in [o.q_control2.0,o.q_control1.0,o.q_target.0]{if let Some(&j)=active.get(&w){reports[j]["donor_untouched"]=serde_json::json!(false);}}}
  if let Some(&j)=ends.get(&i){let s=rows[j];assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);reports[j]["end_guard_true"]=serde_json::json!(eff==vec![0]);assert_eq!(active.remove(&s[2]),Some(j));}
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

  if i%2000000==0{eprintln!("export op {i}, truncated {}",alg.truncations);}
 }
 assert!(stack.is_empty()&&active.is_empty());
 std::fs::write(format!("{}/GLOBAL-PROPERTIES.json",argv[3]),serde_json::to_string_pretty(&reports).unwrap()).unwrap();
 println!("exported {} exact boundaries",reports.len());
}

#[cfg(test)]mod tests{
 use super::*;
 fn alg()->Algebra{Algebra{next:3,products:HashMap::new(),cap:128,truncations:0}}
 #[test]fn triple_and_complement(){let mut a=alg();let x=vec![1];let y=vec![2];let z=vec![0,1,2];let xy=a.and(&x,&y);assert_eq!(xy,a.and(&x,&z));assert_eq!(xy,a.and(&y,&z));assert_eq!(a.and(&x,&vec![0,1]),E::new());}
 #[test]fn unknown_guard_is_not_assumed_true(){let mut a=alg();let v=a.select(&vec![],&vec![0],&vec![1]);assert_eq!(v,vec![1]);assert_ne!(v,vec![0]);}
 #[test]fn truncation_is_fresh(){let mut a=alg();a.cap=1;assert_ne!(a.xor(&vec![1],&vec![2]),a.xor(&vec![1],&vec![2]));}
 #[test]fn late_register_annotations_are_initial_inputs(){let mut a=alg();let mut r=Op::empty();r.kind=K::AppendToRegister;r.q_target=QubitId(0);r.r_target.0=0;let x=make(K::X,u64::MAX,u64::MAX,0,u64::MAX,u64::MAX);let (q,_)=initial_inputs(&[x,r,r],2,0,&mut a);assert!(!q[0].is_empty());assert_eq!(q[0].len(),1);assert!(q[1].is_empty());assert_eq!(a.next,4);}
 fn check_episode(change_control:bool,extra_reader:bool)->usize{
  let n=u64::MAX;let mut a=Algebra{next:4,products:HashMap::new(),cap:128,truncations:0};
  let mut q=vec![vec![1],vec![2],vec![],vec![3]];let mut c=vec![vec![],vec![]];
  let mut w=Unwrapper{active:vec![None;4],finished:vec![],bits:HashMap::new(),inputs:HashSet::new()};
  let fill=make(K::CCX,0,1,2,n,n);w.observe(0,&fill,&vec![0],&q,&c,&mut a);q[2]=a.and(&q[0],&q[1]);
  if change_control{q[0]=a.fresh();}
  let read=make(K::CX,n,2,3,n,n);w.observe(1,&read,&vec![0],&q,&c,&mut a);q[3]=a.xor(&q[3],&q[2]);
  let h=make(K::Hmr,n,n,2,0,n);w.observe(2,&h,&vec![0],&q,&c,&mut a);q[2]=vec![];c[0]=a.fresh();
  let z=make(K::CZ,n,0,1,n,0);w.observe(3,&z,&c[0].clone(),&q,&c,&mut a);
  if extra_reader{let x=make(K::X,n,n,3,n,0);w.observe(4,&x,&c[0].clone(),&q,&c,&mut a);}
  w.finished.iter().filter(|f|f.valid&&f.phase.is_some()).count()
 }
 
 #[test]fn two_reads_are_retained_and_third_control_change_rejected(){
  let n=u64::MAX;let mut a=Algebra{next:5,products:HashMap::new(),cap:128,truncations:0};
  let mut q=vec![vec![1],vec![2],vec![],vec![3],vec![4]];let mut c=vec![vec![]];
  let mut w=Unwrapper{active:vec![None;5],finished:vec![],bits:HashMap::new(),inputs:HashSet::new()};
  let fill=make(K::CCX,0,1,2,n,n);w.observe(0,&fill,&vec![0],&q,&c,&mut a);q[2]=a.and(&q[0],&q[1]);
  for (i,t) in [(1,3),(2,4)]{let x=make(K::CX,n,2,t,n,n);w.observe(i,&x,&vec![0],&q,&c,&mut a);q[t as usize]=a.xor(&q[t as usize],&q[2]);}
  assert_eq!(w.active[2].as_ref().unwrap().reads.len(),2);
  let mut bad=w.active[2].clone();assert!(bad.is_some());
  let h=make(K::Hmr,n,n,2,0,n);w.observe(3,&h,&vec![0],&q,&c,&mut a);q[2]=vec![];c[0]=a.fresh();
  let z=make(K::CZ,n,0,1,n,0);w.observe(4,&z,&c[0].clone(),&q,&c,&mut a);assert!(w.finished[0].valid&&w.finished[0].phase.is_some());
  w.active[2]=bad.take();q[0]=a.fresh();let x=make(K::CX,n,2,3,n,n);w.observe(5,&x,&vec![0],&q,&c,&mut a);assert!(w.active[2].is_none());
 }

 #[test]fn unwrap_proves_only_isolated_repaired_measurements(){assert_eq!(check_episode(false,false),1);assert_eq!(check_episode(true,false),0);assert_eq!(check_episode(false,true),0);}
}

