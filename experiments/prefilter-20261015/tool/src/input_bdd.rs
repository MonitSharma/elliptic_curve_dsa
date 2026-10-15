// Exact ROBDD algebra over classical input bits only. Node-budget failures
// return None and never produce a claimed equality or constant.
#[derive(Clone,Copy)]struct BddNode{var:u16,lo:u32,hi:u32}
struct InputBdd{nodes:Vec<BddNode>,unique:std::collections::HashMap<(u16,u32,u32),u32>,memo:std::collections::HashMap<(u8,u32,u32),u32>,cap:usize,failures:usize}
impl InputBdd{
 fn new(cap:usize)->Self{Self{nodes:vec![BddNode{var:u16::MAX,lo:0,hi:0},BddNode{var:u16::MAX,lo:1,hi:1}],unique:std::collections::HashMap::new(),memo:std::collections::HashMap::new(),cap,failures:0}}
 fn node(&mut self,var:u16,lo:u32,hi:u32)->Option<u32>{if lo==hi{return Some(lo);}let key=(var,lo,hi);if let Some(id)=self.unique.get(&key){return Some(*id);}if self.nodes.len()>=self.cap{self.failures+=1;return None;}let id=self.nodes.len().try_into().unwrap();self.nodes.push(BddNode{var,lo,hi});self.unique.insert(key,id);Some(id)}
 fn variable(&mut self,var:u16)->Option<u32>{self.node(var,0,1)}
 fn apply(&mut self,k:u8,a:u32,b:u32)->Option<u32>{let(a,b)=if a<=b{(a,b)}else{(b,a)};match k{3=>{if a==b{return Some(0);}if a==0{return Some(b);}},4=>{if a==0{return Some(0);}if a==1{return Some(b);}if a==b{return Some(a);}},_=>panic!()}let key=(k,a,b);if let Some(id)=self.memo.get(&key){return Some(*id);}let aa=self.nodes[a as usize];let bb=self.nodes[b as usize];let var=aa.var.min(bb.var);assert_ne!(var,u16::MAX);let(al,ah)=if aa.var==var{(aa.lo,aa.hi)}else{(a,a)};let(bl,bh)=if bb.var==var{(bb.lo,bb.hi)}else{(b,b)};let lo=self.apply(k,al,bl)?;let hi=self.apply(k,ah,bh)?;let out=self.node(var,lo,hi)?;if self.memo.len()>=2000000{self.memo.clear();}self.memo.insert(key,out);Some(out)}
 #[cfg(test)]fn eval(&self,mut id:u32,assignment:u64)->bool{while id>1{let n=self.nodes[id as usize];assert!(n.var<64);id=if assignment>>n.var&1!=0{n.hi}else{n.lo};}id==1}
}
#[cfg(test)]mod bdd_tests{use super::*;
 #[test]fn exact_boolean_truth_tables_and_cancellation(){let mut b=InputBdd::new(100000);let x=b.variable(0).unwrap();let y=b.variable(1).unwrap();let nx=b.apply(3,x,1).unwrap();let ny=b.apply(3,y,1).unwrap();let inputs=[0,1,x,y,nx,ny];for a in inputs{for c in inputs{for k in [3,4]{let z=b.apply(k,a,c).unwrap();for v in 0..4{assert_eq!(b.eval(z,v),if k==3{b.eval(a,v)^b.eval(c,v)}else{b.eval(a,v)&b.eval(c,v)});}}}}let z=b.apply(4,x,nx).unwrap();assert_eq!(z,0);}
 #[test]fn exhausted_budget_returns_unknown_without_wrong_node(){let mut b=InputBdd::new(4);let x=b.variable(0).unwrap();let y=b.variable(1).unwrap();assert_eq!(b.apply(4,x,y),None);assert_eq!(b.nodes.len(),4);for a in 0..4{assert_eq!(b.eval(x,a),a&1!=0);assert_eq!(b.eval(y,a),a&2!=0);}}
}
