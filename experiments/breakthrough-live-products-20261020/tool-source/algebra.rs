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
fn initial_inputs(ops:&[Op],nq:usize,nb:usize,alg:&mut Algebra)->(Vec<E>,Vec<E>){
 // Register annotations are metadata: inputs are loaded before op zero.
 let no=u64::MAX;let mut q=vec![E::new();nq];let mut c=vec![E::new();nb];
 let mut qs=HashSet::new();let mut cs=HashSet::new();
 for o in ops {if o.kind==K::AppendToRegister {
  if o.q_target.0!=no&&qs.insert(o.q_target.0){q[o.q_target.0 as usize]=alg.fresh();}
  if o.c_target.0!=no&&cs.insert(o.c_target.0){c[o.c_target.0 as usize]=alg.fresh();}
 }}(q,c)
}

