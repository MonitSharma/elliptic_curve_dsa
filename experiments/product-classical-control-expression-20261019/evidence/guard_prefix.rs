// Conservative nonzero supports. Never use sampled inputs to choose a circuit.
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
