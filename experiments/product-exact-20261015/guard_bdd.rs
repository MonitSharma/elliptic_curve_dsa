//! Exact Boolean guards; uniform-input probabilities are ranking heuristics.
//! This module never rewrites operations. Bounded tables fail explicitly.
use crate::circuit::{Op,OperationType as K,NO_BIT};
use std::collections::HashMap;
#[derive(Clone,Copy)]
struct Node {var:u32,low:u32,high:u32,prob:f64}
struct Bdd {nodes:Vec<Node>,unique:HashMap<(u32,u32,u32),u32>,apply:HashMap<(u8,u32,u32),u32>,next_var:u32}
impl Bdd {
    fn new()->Self {Self {nodes:vec![Node{var:u32::MAX,low:0,high:0,prob:0.0},Node{var:u32::MAX,low:1,high:1,prob:1.0}],unique:HashMap::new(),apply:HashMap::new(),next_var:0}}
    fn node(&mut self,var:u32,low:u32,high:u32)->u32 {
        if low==high{return low;}
        if let Some(&n)=self.unique.get(&(var,low,high)){return n;}
        assert!(self.nodes.len()<5_000_000,"guard BDD explicit five-million-node resource cap");
        assert!(var<self.nodes[low as usize].var && var<self.nodes[high as usize].var);
        let id=self.nodes.len()as u32;
        let prob=0.5*(self.nodes[low as usize].prob+self.nodes[high as usize].prob);
        self.nodes.push(Node{var,low,high,prob});self.unique.insert((var,low,high),id);id
    }
    fn fresh(&mut self)->u32 {let v=self.next_var;self.next_var+=1;self.node(v,0,1)}
    fn op(&mut self,kind:u8,a:u32,b:u32)->u32 {self.rec(kind,a,b,0)}
    fn rec(&mut self,kind:u8,mut a:u32,mut b:u32,depth:usize)->u32 {
        assert!(depth<2048,"guard BDD explicit recursion cap");
        if a>b {std::mem::swap(&mut a,&mut b);}
        match kind {
            0=>{if a==0{return 0;}if a==1{return b;}if a==b{return a;}},
            1=>{if b==1||a==1{return 1;}if a==0{return b;}if a==b{return a;}},
            2=>{if a==0{return b;}if a==b{return 0;}},
            _=>unreachable!()
        }
        if let Some(&n)=self.apply.get(&(kind,a,b)){return n;}
        let na=self.nodes[a as usize];let nb=self.nodes[b as usize];let var=na.var.min(nb.var);
        let (al,ah)=if na.var==var {(na.low,na.high)}else{(a,a)};
        let (bl,bh)=if nb.var==var {(nb.low,nb.high)}else{(b,b)};
        let low=self.rec(kind,al,bl,depth+1);let high=self.rec(kind,ah,bh,depth+1);
        let n=self.node(var,low,high);
        if self.apply.len()>=1_000_000 {self.apply.clear();}
        self.apply.insert((kind,a,b),n);n
    }
    fn and(&mut self,a:u32,b:u32)->u32 {self.op(0,a,b)}
    fn or(&mut self,a:u32,b:u32)->u32 {self.op(1,a,b)}
    fn xor(&mut self,a:u32,b:u32)->u32 {self.op(2,a,b)}
    fn not(&mut self,a:u32)->u32 {self.xor(a,1)}
    fn select(&mut self,g:u32,t:u32,f:u32)->u32 {
        let a=self.and(g,t);let ng=self.not(g);let b=self.and(ng,f);self.or(a,b)
    }
}
pub struct GuardWeights {pub weights:Vec<f64>,predicates:Vec<u32>,bdd:Bdd}
impl GuardWeights {
    pub fn union_probability(&mut self,uses:&[usize])->f64 {
        let mut union=0;
        for &i in uses {union=self.bdd.or(union,self.predicates[i]);if union==1{break;}}
        self.bdd.nodes[union as usize].prob
    }
}
pub fn analyze(ops:&[Op])->GuardWeights {
    let nb=ops.iter().flat_map(|o|[o.c_target,o.c_condition]).filter(|b|*b!=NO_BIT).map(|b|b.0 as usize).max().map_or(0,|b|b+1);
    let mut bdd=Bdd::new();let mut bits=vec![0;nb];let mut input=vec![false;nb];
    for o in ops {if o.kind==K::AppendToRegister&&o.c_target!=NO_BIT {input[o.c_target.0 as usize]=true;}}
    for (i,is_input) in input.into_iter().enumerate() {if is_input {bits[i]=bdd.fresh();}}
    let mut stack=vec![];let mut weights=vec![0.0;ops.len()];let mut predicates=vec![0;ops.len()];
    for (i,o) in ops.iter().enumerate() {
        if o.kind==K::PopCondition {assert!(stack.pop().is_some());continue;}
        let outer=*stack.last().unwrap_or(&1);
        let direct=if o.c_condition==NO_BIT {1}else{bits[o.c_condition.0 as usize]};
        let g=bdd.and(outer,direct);
        if o.kind==K::CCX {predicates[i]=g;weights[i]=bdd.nodes[g as usize].prob;}
        match o.kind {
            K::PushCondition=>stack.push(g),
            K::BitStore0=>{let ng=bdd.not(g);bits[o.c_target.0 as usize]=bdd.and(bits[o.c_target.0 as usize],ng);},
            K::BitStore1=>{bits[o.c_target.0 as usize]=bdd.or(bits[o.c_target.0 as usize],g);},
            K::BitInvert=>{bits[o.c_target.0 as usize]=bdd.xor(bits[o.c_target.0 as usize],g);},
            K::Hmr=>{let fresh=bdd.fresh();let j=o.c_target.0 as usize;bits[j]=bdd.select(g,fresh,bits[j]);},
            _=>{}
        }
    }
    assert!(stack.is_empty());
    eprintln!("GUARD_BDD nodes={} variables={} input_bits={} classical_slots={nb}",bdd.nodes.len(),bdd.next_var,ops.iter().filter(|o|o.kind==K::AppendToRegister&&o.c_target!=NO_BIT).count());
    GuardWeights {weights,predicates,bdd}
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{BitId,QubitId,RegisterId};
    use quantum_ecc::sim::Simulator;
    fn op(k:K,b:Option<u64>,c:Option<u64>)->Op {let mut o=Op::empty();o.kind=k;o.c_target=BitId(b.unwrap_or(u64::MAX));o.c_condition=BitId(c.unwrap_or(u64::MAX));o}
    fn cc(c:Option<u64>)->Op {let mut o=op(K::CCX,None,c);o.q_control1=QubitId(0);o.q_control2=QubitId(1);o.q_target=QubitId(2);o}
    struct Words {words:Vec<u64>,i:usize}
    impl sha3::digest::XofReader for Words {fn read(&mut self,out:&mut [u8]) {assert_eq!(out.len(),8);out.copy_from_slice(&self.words[self.i].to_le_bytes());self.i+=1;}}
    #[test]
    fn snapshot_and_conditional_store_hmr_weights_match_native() {
        let mut ops=vec![];let mut r=Op::empty();r.kind=K::Register;r.r_target=RegisterId(0);ops.push(r);
        for b in 0..2 {let mut a=op(K::AppendToRegister,Some(b),None);a.r_target=RegisterId(0);ops.push(a);}
        ops.extend([op(K::PushCondition,None,Some(0)),op(K::BitInvert,Some(0),None),cc(Some(1)),op(K::PopCondition,None,None)]);
        let mut h=op(K::Hmr,Some(2),Some(1));h.q_target=QubitId(2);ops.push(h);
        ops.extend([op(K::BitStore1,Some(3),Some(2)),op(K::BitInvert,Some(3),Some(0)),op(K::PushCondition,None,Some(3)),cc(None),op(K::BitStore0,Some(3),None),cc(Some(1)),op(K::PopCondition,None,None)]);
        h.c_target=BitId(4);h.c_condition=NO_BIT;ops.push(h);ops.extend([op(K::BitInvert,Some(4),Some(1)),cc(Some(4))]);
        let guards=analyze(&ops);assert!((guards.weights.iter().sum::<f64>()-1.25).abs()<1e-12);
        let plane=|bit:usize| (0..64).fold(0u64,|v,l|v|((((l%16)>>bit)&1)as u64)<<l);
        let mut words=Words{words:vec![plane(2),plane(3)],i:0};let mut sim=Simulator::new(3,8,&mut words);
        sim.bits[0]=plane(0);sim.bits[1]=plane(1);sim.apply_iter(ops.iter());
        assert_eq!(sim.stats.toffoli_gates,80);
    }
    #[test]
    fn union_eliminates_mutually_exclusive_proxy_profit() {
        let mut b=Bdd::new();let x=b.fresh();let nx=b.not(x);let y=b.fresh();
        assert_eq!(b.or(x,nx),1);let u=b.or(x,y);assert_eq!(b.nodes[u as usize].prob,0.75);
        let mut g=GuardWeights{weights:vec![0.5,0.5],predicates:vec![x,nx],bdd:b};
        assert_eq!(g.weights.iter().sum::<f64>()-g.union_probability(&[0,1]),0.0);
    }
}
