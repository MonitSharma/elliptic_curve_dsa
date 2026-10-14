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
    free:Vec<u32>, alive:usize,
}
impl Manager {
    fn new()->Self {
        let mut out=Self{nodes:Vec::new(),terminals:HashMap::new(),unique:HashMap::new(),memo:HashMap::new(),limit:NODE_CAP,free:Vec::new(),alive:0};
        assert_eq!(out.terminal(0),0);assert_eq!(out.terminal(u64::MAX),1);out
    }
    fn terminal(&mut self,value:u64)->u32 {
        if let Some(id)=self.terminals.get(&value){return *id}
        let id=self.insert(Node{var:u32::MAX,low:0,high:0,value,size_bound:usize::from(value!=0)});
        self.terminals.insert(value,id);id
    }
    fn branch(&mut self,var:u32,low:u32,high:u32)->Result<u32,String> {
        if low==high{return Ok(low)}
        if let Some(id)=self.unique.get(&(var,low,high)){return Ok(*id)}
        if self.alive>=self.limit{return Err("inconclusive: decision diagram node cap".into())}
        let size_bound=1usize.saturating_add(self.nodes[low as usize].size_bound).saturating_add(self.nodes[high as usize].size_bound);
        let id=self.insert(Node{var,low,high,value:0,size_bound});
        self.unique.insert((var,low,high),id);Ok(id)
    }
    fn insert(&mut self,node:Node)->u32 {
        self.alive+=1;
        if let Some(id)=self.free.pop(){self.nodes[id as usize]=node;id}
        else{let id=self.nodes.len()as u32;self.nodes.push(node);id}
    }
    fn collect(&mut self,roots:&[u32]) {
        let mut marks=vec![false;self.nodes.len()];let mut todo=roots.to_vec();todo.extend([0,1]);
        while let Some(id)=todo.pop(){if marks[id as usize]{continue}marks[id as usize]=true;let n=self.nodes[id as usize];if n.var!=u32::MAX{todo.extend([n.low,n.high]);}}
        self.memo.clear();self.unique.retain(|_,id|marks[*id as usize]);self.terminals.retain(|_,id|marks[*id as usize]);
        self.free=(0..self.nodes.len()).filter(|&i|!marks[i]).map(|i|i as u32).collect();self.alive=self.nodes.len()-self.free.len();
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

#[cfg(test)]
mod decision_truth_tests {
    use super::*;
    #[test]
    fn graph_truth_tables_and_collection_are_exact(){
        reset_manager();let mut seed=0x8325bda9741920f1u64;
        let mut rng=||{seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;seed};
        let mut values:Vec<(Poly,Vec<u64>)>=(0..6).map(|var|(Poly::variable(var).unwrap(),(0..64).map(|m|if(m>>var)&1!=0{u64::MAX}else{0}).collect())).collect();
        for _ in 0..4{let mask=rng();values.push((Poly::constant(mask),vec![mask;64]));}
        for _ in 0..80{let a=rng()as usize%values.len();let b=rng()as usize%values.len();let and=rng()&1!=0;let p=if and{values[a].0.and(&values[b].0)}else{values[a].0.xor(&values[b].0)}.unwrap();let truth=(0..64).map(|i|if and{values[a].1[i]&values[b].1[i]}else{values[a].1[i]^values[b].1[i]}).collect();values.push((p,truth));}
        fn evaluate(p:Poly,assignment:usize)->u64{GRAPH.with(|g|{let m=g.borrow();let mut id=p.0;loop{let n=m.nodes[id as usize];if n.var==u32::MAX{return n.value;}id=if assignment>>n.var&1==0{n.low}else{n.high};}})}
        for(p,truth)in &values{for i in 0..64{assert_eq!(evaluate(*p,i),truth[i]);}}
        let keep=values[values.len()-1].clone();GRAPH.with(|g|g.borrow_mut().collect(&[keep.0.0]));
        for var in 20..60{let _=Poly::variable(var).unwrap();let _=Poly::constant(rng());}
        for i in 0..64{assert_eq!(evaluate(keep.0,i),keep.1[i]);}
        reset_manager();
    }
}
