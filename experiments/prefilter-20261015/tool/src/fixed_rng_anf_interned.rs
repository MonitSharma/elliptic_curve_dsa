
// Exact Boolean polynomial over unknown measurement words, with concrete64-bit
// input-mask coefficients. Capped expressions get fresh unconstrained symbols;
// the constant and conservative dependency-lane mask preserve known bits.
#[derive(Clone,PartialEq,Eq,PartialOrd,Ord,Hash)]struct Poly(Vec<(Vec<u32>,u64)>);
#[derive(Clone,PartialEq,Eq,Hash)]enum OpaqueKey{Norm(Poly),And(Poly,Poly)}
struct FixedAnf{next:u32,cap:usize,capped:usize,degree:usize,intern:std::collections::HashMap<OpaqueKey,(u32,u64)>,intern_bytes:usize,intern_hits:usize,intern_clears:usize}

impl Poly{fn constant(x:u64)->Self{if x==0{Self(Vec::new())}else{Self(vec![(Vec::new(),x)])}}fn summary(&self)->(u64,u64){let(mut c,mut d)=(0,0);for(k,v)in&self.0{if k.is_empty(){c^=*v}else{d|=*v}}(c,d)}fn known(&self)->(u64,u64){let(c,d)=self.summary();(c,!d)}}
impl FixedAnf{
 fn new(cap:usize,next:u32)->Self{Self{next,cap,capped:0,degree:16,intern:std::collections::HashMap::new(),intern_bytes:0,intern_hits:0,intern_clears:0}}
 fn key_bytes(key:&OpaqueKey)->usize{let p=|p:&Poly|64+p.0.iter().map(|(k,_)|40+k.len()*4).sum::<usize>();match key{OpaqueKey::Norm(a)=>p(a),OpaqueKey::And(a,b)=>p(a)+p(b)}}
 fn opaque_key(&mut self,c:u64,d:u64,key:OpaqueKey)->Poly{self.capped+=1;if d==0{return Poly::constant(c);}let(id,mask)=if let Some(pair)=self.intern.get(&key){self.intern_hits+=1;*pair}else{let id=self.next;self.next=self.next.checked_add(1).unwrap();let bytes=Self::key_bytes(&key);let budget=64*1024*1024;if bytes<=budget{if self.intern_bytes+bytes>budget{self.intern.clear();self.intern_bytes=0;self.intern_clears+=1;}self.intern_bytes+=bytes;self.intern.insert(key,(id,d));}(id,d)};assert_eq!(mask,d);let mut p=Poly::constant(c);p.0.push((vec![id],d));p}
 fn capped_terms(&mut self,mut terms:std::collections::BTreeMap<Vec<u32>,u64>)->Poly{let c=terms.remove(&Vec::new()).unwrap_or(0);let d=terms.values().fold(0,|a,b|a|b);self.opaque_key(c,d,OpaqueKey::Norm(Poly(terms.into_iter().collect())))}

 fn fresh(&mut self,mask:u64)->Poly{if mask==0{return Poly::constant(0);}let id=self.next;self.next=self.next.checked_add(1).unwrap();Poly(vec![(vec![id],mask)])}
 fn opaque(&mut self,c:u64,d:u64)->Poly{self.capped+=1;let mut p=Poly::constant(c);let x=self.fresh(d);p.0.extend(x.0);p}
 fn xor(&mut self,a:&Poly,b:&Poly)->Poly{if a==b{return Poly::constant(0);}if a.0.is_empty(){return b.clone();}if b.0.is_empty(){return a.clone();}let mut terms=std::collections::BTreeMap::<Vec<u32>,u64>::new();for(k,v)in a.0.iter().chain(&b.0){let new=terms.get(k).copied().unwrap_or(0)^v;if new==0{terms.remove(k);}else{terms.insert(k.clone(),new);}}if terms.len()-usize::from(terms.contains_key(&Vec::new()))>self.cap{return self.capped_terms(terms);}Poly(terms.into_iter().collect())}
 fn and(&mut self,a:&Poly,b:&Poly)->Poly{if a.0.is_empty()||b.0.is_empty(){return Poly::constant(0);}if a==b{return a.clone();}let(ac,ad)=a.summary();let(bc,bd)=b.summary();let fallback=|alg:&mut Self|{let(x,y)=if a<=b{(a.clone(),b.clone())}else{(b.clone(),a.clone())};alg.opaque_key(ac&bc,(ad&(bc|bd))|(bd&ac),OpaqueKey::And(x,y))};if a.0.len()*b.0.len()>(self.cap+1)*(self.cap+1){return fallback(self);}let mut terms=std::collections::BTreeMap::<Vec<u32>,u64>::new();for(ka,va)in&a.0{for(kb,vb)in&b.0{let coefficient=va&vb;if coefficient==0{continue;}let mut key=ka.clone();key.extend(kb);key.sort_unstable();key.dedup();if key.len()>self.degree{return fallback(self);}let old=terms.get(&key).copied().unwrap_or(0);let new=old^coefficient;if new==0{terms.remove(&key);}else{terms.insert(key,new);}}}if terms.len()-usize::from(terms.contains_key(&Vec::new()))>self.cap{return self.capped_terms(terms);}Poly(terms.into_iter().collect())}
 fn not(&mut self,a:&Poly)->Poly{self.xor(a,&Poly::constant(u64::MAX))}
}
#[cfg(test)]mod fixed_anf_tests{use super::*;
 fn eval(p:&Poly,values:&[u64])->u64{p.0.iter().fold(0,|a,(key,v)|a^key.iter().fold(*v,|b,i|b&values[*i as usize]))}
 #[test]fn concrete_mask_rng_cancellation(){let mut a=FixedAnf::new(32,0);let x=a.fresh(u64::MAX);let y=a.fresh(u64::MAX);let c=Poly::constant(0x9e3779b97f4a7c15);let xy=a.and(&x,&y);let f=a.xor(&xy,&c);let nf=a.not(&f);let z=a.and(&f,&nf);assert!(z.0.is_empty());let f2=a.and(&f,&f);assert!(f2==f);}
 #[test]fn all_two_variable_truth_assignments_and_mask_coefficients(){let mut a=FixedAnf::new(32,2);let p=Poly(vec![(vec![],0xabababababababab),(vec![0],0xace02468ace02468),(vec![1],0x0123456789abcdef),(vec![0,1],0xf0f0f0f0f0f0f0f0)]);let q=Poly(vec![(vec![],0x5555555555555555),(vec![1],0xffff0000ffff0000)]);let and=a.and(&p,&q);let xor=a.xor(&p,&q);let not=a.not(&p);for i in 0..4{let values=[if i&1!=0{u64::MAX}else{0},if i&2!=0{u64::MAX}else{0}];assert_eq!(eval(&and,&values),eval(&p,&values)&eval(&q,&values));assert_eq!(eval(&xor,&values),eval(&p,&values)^eval(&q,&values));assert_eq!(eval(&not,&values),!eval(&p,&values));}}
 #[test]fn cap_retains_only_sound_known_lanes(){let mut a=FixedAnf::new(1,2);let x=Poly(vec![(vec![],0xabc000),(vec![0],0xff),(vec![1],0xff00)]);let y=Poly(vec![(vec![],0x123456),(vec![1],0x0000ffff)]);let z=a.and(&x,&y);assert!(a.capped>0);let(c,k)=z.known();for i in 0..4{let values=[if i&1!=0{u64::MAX}else{0},if i&2!=0{u64::MAX}else{0}];assert_eq!((c^(eval(&x,&values)&eval(&y,&values)))&k,0);}let unknown=a.fresh(u64::MAX);assert_eq!(unknown.known().1,0);}
}

#[cfg(test)]mod intern_tests{use super::*;
 #[test]fn retained_nonconstant_key_cancels_across_different_constants(){let mut a=FixedAnf::new(1,0);let x=a.fresh(u64::MAX);let y=a.fresh(u64::MAX);let u=a.xor(&x,&y);let mut literal=Poly(vec![(vec![0],u64::MAX),(vec![1],u64::MAX)]);let c=Poly::constant(0x9e3779b97f4a7c15);let v=a.xor(&literal,&c);let z=a.xor(&u,&v);assert_eq!(z.known(),(0x9e3779b97f4a7c15,u64::MAX));assert!(a.intern_hits>0);let old_next=a.next;a.intern.clear();a.intern_bytes=0;literal.0.push((vec![],1));let _=a.xor(&literal,&c);assert!(a.next>old_next,"eviction must never recycle symbolic IDs");}
}
