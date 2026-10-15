//! Conservative, exact classical guard expressions. Opaque nodes retain their
//! immutable meanings; only conjunction and complement contradictions prove
//! disjointness. This does not assume any sampled input distribution.
use crate::circuit::{Op,OperationType as K,QubitOrBit,NO_BIT,analyze_ops};
use std::collections::HashMap;
struct Dag{next:u64,factors:HashMap<u64,Vec<u64>>,ands:HashMap<Vec<u64>,u64>,xors:HashMap<(u64,u64),u64>}
impl Dag{
    fn fresh(&mut self)->u64{let id=self.next;self.next+=2;id}
    fn lits(&self,id:u64)->Vec<u64>{if id==1{vec![]}else if id&1==0{self.factors.get(&id).cloned().unwrap_or(vec![id])}else{vec![id]}}
    fn and(&mut self,a:u64,b:u64)->u64{
        if a==0||b==0{return 0;}if a==1{return b;}if b==1{return a;}
        let mut v=self.lits(a);v.extend(self.lits(b));v.sort_unstable();v.dedup();
        if v.iter().any(|x|v.binary_search(&(x^1)).is_ok()){return 0;}if v.len()==1{return v[0];}
        if let Some(&id)=self.ands.get(&v){return id;}let id=self.fresh();self.ands.insert(v.clone(),id);self.factors.insert(id,v);id
    }
    fn xor(&mut self,a:u64,b:u64)->u64{
        let c=(a^b)&1;let(mut a,mut b)=(a&!1,b&!1);if a>b{std::mem::swap(&mut a,&mut b);}
        if a==b{return c;}if a==0{return b^c;}
        let id=if let Some(&id)=self.xors.get(&(a,b)){id}else{let id=self.fresh();self.xors.insert((a,b),id);id};id^c
    }
}
pub fn build_guards(ops:&[Op])->Vec<Vec<u64>>{
    let(_,nb,_,regs)=analyze_ops(ops.iter());let mut dag=Dag{next:2,factors:HashMap::new(),ands:HashMap::new(),xors:HashMap::new()};
    let mut bits=vec![0;nb as usize];for reg in regs{for slot in reg{if let QubitOrBit::Bit(b)=slot{if bits[b.0 as usize]==0{bits[b.0 as usize]=dag.fresh();}}}}
    let mut base=1;let mut stack=vec![];let mut out=Vec::with_capacity(ops.len());
    for o in ops{
        if o.kind==K::PushCondition{stack.push(base);base=dag.and(base,bits[o.c_condition.0 as usize]);out.push(vec![]);continue;}
        if o.kind==K::PopCondition{base=stack.pop().unwrap();out.push(vec![]);continue;}
        let c=if o.c_condition==NO_BIT{base}else{dag.and(base,bits[o.c_condition.0 as usize])};out.push(dag.lits(c));
        let t=o.c_target.0 as usize;
        match o.kind{
            K::BitInvert=>bits[t]=dag.xor(bits[t],c),
            K::BitStore0=>bits[t]=dag.and(bits[t],c^1),
            K::BitStore1=>bits[t]=dag.and(bits[t]^1,c^1)^1,
            K::Hmr=>{let f=dag.fresh();let a=dag.and(c,f);let b=dag.and(c^1,bits[t]);bits[t]=dag.xor(a,b);},
            _=>{}
        }
    }
    assert!(stack.is_empty());println!("CLASSICAL_GUARDS immutable_nodes={} conjunction_nodes={}",dag.next/2,dag.factors.len());out
}
pub fn disjoint(a:&[u64],b:&[u64])->bool{a.contains(&0)||b.contains(&0)||a.iter().any(|x|b.binary_search(&(x^1)).is_ok())}
