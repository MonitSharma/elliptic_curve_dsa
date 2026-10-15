
// Exact Boolean polynomial over unknown measurement words, with concrete64-bit
// input-mask coefficients. Capped expressions get fresh unconstrained symbols;
// the constant and conservative dependency-lane mask preserve known bits.
#[derive(Clone,PartialEq,Eq)]struct Poly(Vec<(Vec<u32>,u64)>);
struct FixedAnf{next:u32,cap:usize,capped:usize,degree:usize}
impl Poly{fn constant(x:u64)->Self{if x==0{Self(Vec::new())}else{Self(vec![(Vec::new(),x)])}}fn summary(&self)->(u64,u64){let(mut c,mut d)=(0,0);for(k,v)in&self.0{if k.is_empty(){c^=*v}else{d|=*v}}(c,d)}fn known(&self)->(u64,u64){let(c,d)=self.summary();(c,!d)}}
impl FixedAnf{
 fn fresh(&mut self,mask:u64)->Poly{if mask==0{return Poly::constant(0);}let id=self.next;self.next=self.next.checked_add(1).unwrap();Poly(vec![(vec![id],mask)])}
 fn opaque(&mut self,c:u64,d:u64)->Poly{self.capped+=1;let mut p=Poly::constant(c);let x=self.fresh(d);p.0.extend(x.0);p}
 fn xor(&mut self,a:&Poly,b:&Poly)->Poly{if a==b{return Poly::constant(0);}if a.0.is_empty(){return b.clone();}if b.0.is_empty(){return a.clone();}let mut terms=std::collections::BTreeMap::<Vec<u32>,u64>::new();for(k,v)in a.0.iter().chain(&b.0){let new=terms.get(k).copied().unwrap_or(0)^v;if new==0{terms.remove(k);}else{terms.insert(k.clone(),new);}}if terms.len()>self.cap{let mut c=0;let mut d=0;for(k,v)in terms{if k.is_empty(){c^=v}else{d|=v}}return self.opaque(c,d);}Poly(terms.into_iter().collect())}
 fn and(&mut self,a:&Poly,b:&Poly)->Poly{if a.0.is_empty()||b.0.is_empty(){return Poly::constant(0);}if a==b{return a.clone();}let(ac,ad)=a.summary();let(bc,bd)=b.summary();let fallback=|alg:&mut Self|alg.opaque(ac&bc,(ad&(bc|bd))|(bd&ac));if a.0.len()*b.0.len()>self.cap*self.cap{return fallback(self);}let mut terms=std::collections::BTreeMap::<Vec<u32>,u64>::new();for(ka,va)in&a.0{for(kb,vb)in&b.0{let coefficient=va&vb;if coefficient==0{continue;}let mut key=ka.clone();key.extend(kb);key.sort_unstable();key.dedup();if key.len()>self.degree{return fallback(self);}let old=terms.get(&key).copied().unwrap_or(0);let new=old^coefficient;if new==0{terms.remove(&key);}else{terms.insert(key,new);}}}if terms.len()>self.cap{let mut c=0;let mut d=0;for(k,v)in terms{if k.is_empty(){c^=v}else{d|=v}}return self.opaque(c,d);}Poly(terms.into_iter().collect())}
 fn not(&mut self,a:&Poly)->Poly{self.xor(a,&Poly::constant(u64::MAX))}
}
#[cfg(test)]mod fixed_anf_tests{use super::*;
 fn eval(p:&Poly,values:&[u64])->u64{p.0.iter().fold(0,|a,(key,v)|a^key.iter().fold(*v,|b,i|b&values[*i as usize]))}
 #[test]fn concrete_mask_rng_cancellation(){let mut a=FixedAnf{next:0,cap:32,capped:0,degree:16};let x=a.fresh(u64::MAX);let y=a.fresh(u64::MAX);let c=Poly::constant(0x9e3779b97f4a7c15);let xy=a.and(&x,&y);let f=a.xor(&xy,&c);let nf=a.not(&f);let z=a.and(&f,&nf);assert!(z.0.is_empty());let f2=a.and(&f,&f);assert!(f2==f);}
 #[test]fn all_two_variable_truth_assignments_and_mask_coefficients(){let mut a=FixedAnf{next:2,cap:32,capped:0,degree:16};let p=Poly(vec![(vec![],0xabababababababab),(vec![0],0xace02468ace02468),(vec![1],0x0123456789abcdef),(vec![0,1],0xf0f0f0f0f0f0f0f0)]);let q=Poly(vec![(vec![],0x5555555555555555),(vec![1],0xffff0000ffff0000)]);let and=a.and(&p,&q);let xor=a.xor(&p,&q);let not=a.not(&p);for i in 0..4{let values=[if i&1!=0{u64::MAX}else{0},if i&2!=0{u64::MAX}else{0}];assert_eq!(eval(&and,&values),eval(&p,&values)&eval(&q,&values));assert_eq!(eval(&xor,&values),eval(&p,&values)^eval(&q,&values));assert_eq!(eval(&not,&values),!eval(&p,&values));}}
 #[test]fn cap_retains_only_sound_known_lanes(){let mut a=FixedAnf{next:2,cap:1,capped:0,degree:16};let x=Poly(vec![(vec![],0xabc000),(vec![0],0xff),(vec![1],0xff00)]);let y=Poly(vec![(vec![],0x123456),(vec![1],0x0000ffff)]);let z=a.and(&x,&y);assert!(a.capped>0);let(c,k)=z.known();for i in 0..4{let values=[if i&1!=0{u64::MAX}else{0},if i&2!=0{u64::MAX}else{0}];assert_eq!((c^(eval(&x,&values)&eval(&y,&values)))&k,0);}let unknown=a.fresh(u64::MAX);assert_eq!(unknown.known().1,0);}
}
