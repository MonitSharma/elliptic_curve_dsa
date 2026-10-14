// Canonical reduced ordered decision diagrams with u64 terminal masks.
// Every lane represents one fixed input; each variable is one independent
// measurement. Equality to zero is exact for all measurement assignments.
use std::cell::RefCell;
use std::collections::HashMap;

const NODE_CAP: usize = 1_000_000;
const DEPTH_CAP: usize = 2048;
#[derive(Clone,Copy,Debug)]
struct Node { var:u32, low:u32, high:u32, value:u64, size_bound:usize }
struct Manager {
    nodes:Vec<Node>, terminals:HashMap<u64,u32>,
    unique:HashMap<(u32,u32,u32),u32>, memo:HashMap<(u8,u32,u32),u32>, limit:usize,
}
impl Manager {
    fn new()->Self {
        let mut out=Self{nodes:Vec::new(),terminals:HashMap::new(),unique:HashMap::new(),memo:HashMap::new(),limit:NODE_CAP};
        assert_eq!(out.terminal(0),0);assert_eq!(out.terminal(u64::MAX),1);out
    }
    fn terminal(&mut self,value:u64)->u32 {
        if let Some(id)=self.terminals.get(&value){return *id}
        let id=self.nodes.len()as u32;
        self.nodes.push(Node{var:u32::MAX,low:0,high:0,value,size_bound:usize::from(value!=0)});
        self.terminals.insert(value,id);id
    }
    fn branch(&mut self,var:u32,low:u32,high:u32)->Result<u32,String> {
        if low==high{return Ok(low)}
        if let Some(id)=self.unique.get(&(var,low,high)){return Ok(*id)}
        if self.nodes.len()>=self.limit{return Err("inconclusive: decision diagram node cap".into())}
        let size_bound=1usize.saturating_add(self.nodes[low as usize].size_bound).saturating_add(self.nodes[high as usize].size_bound);
        let id=self.nodes.len()as u32;self.nodes.push(Node{var,low,high,value:0,size_bound});
        self.unique.insert((var,low,high),id);Ok(id)
    }
    fn apply(&mut self,kind:u8,mut a:u32,mut b:u32,depth:usize)->Result<u32,String> {
        if a>b{std::mem::swap(&mut a,&mut b)}
        if kind==0 {if a==b{return Ok(0)}if a==0{return Ok(b)}}
        else {if a==b{return Ok(a)}if a==0{return Ok(0)}if a==1{return Ok(b)}}
        let na=self.nodes[a as usize];let nb=self.nodes[b as usize];
        if na.var==u32::MAX && nb.var==u32::MAX {
            return Ok(self.terminal(if kind==0{na.value^nb.value}else{na.value&nb.value}))
        }
        if depth>=DEPTH_CAP{return Err("inconclusive: decision diagram recursion cap".into())}
        if let Some(id)=self.memo.get(&(kind,a,b)){return Ok(*id)}
        let var=na.var.min(nb.var);
        let (al,ah)=if na.var==var{(na.low,na.high)}else{(a,a)};
        let (bl,bh)=if nb.var==var{(nb.low,nb.high)}else{(b,b)};
        let low=self.apply(kind,al,bl,depth+1)?;let high=self.apply(kind,ah,bh,depth+1)?;
        let result=self.branch(var,low,high)?;self.memo.insert((kind,a,b),result);Ok(result)
    }
}
thread_local!{static GRAPH:RefCell<Manager>=RefCell::new(Manager::new());}
fn reset_manager(){GRAPH.with(|g|*g.borrow_mut()=Manager::new());}

#[derive(Clone,Copy,Debug,PartialEq,Eq)]
struct Poly(u32);
impl Poly {
    fn constant(value:u64)->Self{GRAPH.with(|g|Self(g.borrow_mut().terminal(value)))}
    fn variable(var:u32)->Result<Self,String>{GRAPH.with(|g|g.borrow_mut().branch(var,0,1).map(Self))}
    fn scalar(&self)->Option<u64>{GRAPH.with(|g|{let n=g.borrow().nodes[self.0 as usize];(n.var==u32::MAX).then_some(n.value)})}
    fn binary(&self,other:&Self,kind:u8)->Result<Self,String>{GRAPH.with(|g|{let mut graph=g.borrow_mut();if graph.memo.len()>800_000{graph.memo.clear();}graph.apply(kind,self.0,other.0,0).map(Self)})}
    fn xor(&self,other:&Self)->Result<Self,String>{self.binary(other,0)}
    fn and(&self,other:&Self)->Result<Self,String>{self.binary(other,1)}
    fn not(&self)->Result<Self,String>{self.xor(&Self::constant(u64::MAX))}
    fn complexity(&self)->usize{GRAPH.with(|g|g.borrow().nodes[self.0 as usize].size_bound)}
}
