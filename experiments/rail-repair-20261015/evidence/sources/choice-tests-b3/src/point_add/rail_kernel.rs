//! Exact decision-diagram phase audit of all measurements on fixed inputlanes.
use crate::circuit::{analyze_ops, Op, OperationType as K, NO_BIT};
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

#[derive(Debug)]
pub struct Audit {
    pub qubits: Vec<u64>,
    pub measurements: u64,
    pub maximum_phase_size_bound: usize,
    pub maximum_quantum_size_bound: usize,
}

/// Classical slots start at the supplied constants, with remaining scratch 0.
/// Final quantum values must be independent of measurements. Classical scratch
/// may retain outcomes. This is a finite INPUT-domain proof, not a score.
pub fn audit(ops: &[Op], input: &[u64], initial_bits: &[u64]) -> Result<Audit, String> {
    reset_manager();
    let (nq, nb, _, _) = analyze_ops(ops.iter());
    if input.len() < nq as usize { return Err("input shorter than quantum allocation".into()); }
    let mut q: Vec<_> = input.iter().map(|v| Poly::constant(*v)).collect();
    let mut bits = vec![Poly::constant(0); (nb as usize).max(initial_bits.len())];
    for (bit, value) in initial_bits.iter().enumerate() { bits[bit] = Poly::constant(*value); }
    let mut phase = Poly::constant(0);
    let mut base = Poly::constant(u64::MAX);
    let mut stack = Vec::new();
    let mut next_measurement = 0u32;
    let (mut max_phase, mut max_quantum) = (0, 1);
    for (index, op) in ops.iter().enumerate() {
        if index%32768==0 {GRAPH.with(|g|{let mut m=g.borrow_mut();if m.alive>400_000 || m.memo.len()>500_000 {let mut roots:Vec<u32>=q.iter().chain(&bits).chain(&stack).map(|p|p.0).collect();roots.extend([phase.0,base.0]);m.collect(&roots);}});}

        let (a, b, t, bit) = (op.q_control1.0 as usize, op.q_control2.0 as usize,
                             op.q_target.0 as usize, op.c_target.0 as usize);
        let step = (|| -> Result<(), String> {
        let condition = if op.c_condition == NO_BIT { base.clone() }
            else { base.and(&bits[op.c_condition.0 as usize])? };
        match op.kind {
            K::PushCondition => { stack.push(std::mem::replace(&mut base,condition)); }
            K::PopCondition => { base = stack.pop().ok_or_else(|| format!("unbalanced pop at {index}"))?; }
            K::X => { q[t] = q[t].xor(&condition)?; }
            K::CX => { q[t] = q[t].xor(&condition.and(&q[a])?)?; }
            K::CCX => { q[t] = q[t].xor(&condition.and(&q[a].and(&q[b])?)?)?; }
            K::Swap => {
                let delta = condition.and(&q[a].xor(&q[t])?)?;
                q[a] = q[a].xor(&delta)?; q[t] = q[t].xor(&delta)?;
            }
            K::R | K::Hmr => {
                let m = Poly::variable(next_measurement)?;
                next_measurement = next_measurement.checked_add(1).ok_or("measurement id overflow")?;
                phase = phase.xor(&condition.and(&q[t].and(&m)?)?)?;
                if op.kind == K::Hmr {
                    bits[bit] = bits[bit].xor(&condition.and(&bits[bit].xor(&m)?)?)?;
                }
                q[t] = q[t].and(&condition.not()?)?;
            }
            K::BitInvert => { bits[bit] = bits[bit].xor(&condition)?; }
            K::BitStore0 => { bits[bit] = bits[bit].and(&condition.not()?)?; }
            K::BitStore1 => { bits[bit] = bits[bit].xor(&condition.and(&bits[bit].not()?)?)?; }
            K::Neg => { phase = phase.xor(&condition)?; }
            K::Z => { phase = phase.xor(&condition.and(&q[t])?)?; }
            K::CZ => { phase = phase.xor(&condition.and(&q[a].and(&q[t])?)?)?; }
            K::CCZ => { phase = phase.xor(&condition.and(&q[a].and(&q[b].and(&q[t])?)?)?)?; }
            K::Register | K::AppendToRegister | K::DebugPrint => {}
        }
        Ok(())
        })();
        step.map_err(|error| format!("{error}; operation={index} kind={:?} measurements={next_measurement} prior_phase_max={max_phase} prior_quantum_max={max_quantum}",op.kind))?;
        max_phase = max_phase.max(phase.complexity());
        match op.kind {
            K::X | K::CX | K::CCX | K::R | K::Hmr => { max_quantum = max_quantum.max(q[t].complexity()); }
            K::Swap => { max_quantum = max_quantum.max(q[t].complexity()).max(q[a].complexity()); }
            _ => {}
        }
    }
    if !stack.is_empty() { return Err("unclosed condition stack".into()); }
    if phase.scalar()!=Some(0) {
        return Err(format!("nonzero phase polynomial represented by exact decision diagram: root={} size_bound={}",phase.0,phase.complexity()));
    }
    let mut output = Vec::with_capacity(q.len());
    for (slot, value) in q.iter().enumerate() {
        output.push(value.scalar().ok_or_else(|| format!("measurement-dependent final quantum slot {slot}"))?);
    }
    Ok(Audit { qubits: output, measurements: next_measurement as u64,
               maximum_phase_size_bound: max_phase, maximum_quantum_size_bound: max_quantum })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{BitId, QubitId};
    fn native(ops: &[Op], input: &[u64], words: &[u64]) -> (Vec<u64>, u64) {
        struct Reader<'a> { words: &'a [u64], at: usize }
        impl sha3::digest::XofReader for Reader<'_> {
            fn read(&mut self, bytes: &mut [u8]) {
                assert_eq!(bytes.len(),8); bytes.copy_from_slice(&self.words[self.at].to_le_bytes()); self.at+=1;
            }
        }
        let (_,nb,_,_)=analyze_ops(ops.iter());let mut reader=Reader{words,at:0};
        let mut sim=quantum_ecc::sim::Simulator::new(input.len(),nb as usize,&mut reader);
        sim.qubits=input.to_vec();sim.apply_iter(ops.iter());(sim.qubits,sim.phase)
    }
    fn gate(k: K, a: Option<u64>, b: Option<u64>, t: Option<u64>, bit: Option<u64>, condition: Option<u64>) -> Op {
        let mut op = Op::empty(); op.kind = k;
        if let Some(a) = a { op.q_control1 = QubitId(a); }
        if let Some(b) = b { op.q_control2 = QubitId(b); }
        if let Some(t) = t { op.q_target = QubitId(t); }
        if let Some(bit) = bit { op.c_target = BitId(bit); }
        if let Some(c) = condition { op.c_condition = BitId(c); }
        op.validate(); op
    }
    #[test]
    fn snapshot_mutation_nested_push_and_phase_fault() {
        let mut ops = vec![
            gate(K::Hmr,None,None,Some(0),Some(0),None),
            gate(K::PushCondition,None,None,None,None,Some(0)),
            gate(K::BitInvert,None,None,None,Some(0),None),
            gate(K::BitStore1,None,None,None,Some(1),None),
            gate(K::PushCondition,None,None,None,None,Some(1)),
            gate(K::Z,None,None,Some(1),None,None),
            gate(K::PopCondition,None,None,None,None,None),
            gate(K::PopCondition,None,None,None,None,None),
        ];
        let mask=0x934ce2086ffa3145;let input=[mask,mask,!mask];
        let result=audit(&ops,&input,&[]).unwrap();assert_eq!(result.qubits,vec![0,mask,!mask]);assert_eq!(result.measurements,1);
        for m in [0,u64::MAX,0x682ab19376cdfe08] {let(q,phase)=native(&ops,&input,&[m]);assert_eq!(q,result.qubits);assert_eq!(phase,0);}
        ops[5].q_target=QubitId(2);
        assert!(audit(&ops,&input,&[]).unwrap_err().starts_with("nonzero phase polynomial"));
        assert_eq!(native(&ops,&input,&[u64::MAX]).1,u64::MAX);
    }
    #[test]
    fn conditional_hmr_boolean_idempotence_and_value_restoration() {
        let ops=vec![
            gate(K::Hmr,None,None,Some(0),Some(0),None),
            gate(K::PushCondition,None,None,None,None,Some(0)),
            gate(K::Hmr,None,None,Some(1),Some(1),None),
            gate(K::Z,None,None,Some(2),None,Some(1)),
            gate(K::CX,Some(2),None,Some(1),None,None),
            gate(K::PopCondition,None,None,None,None,None),
        ];
        let input=[0,0x123456789abcdef0,0x123456789abcdef0];
        let result=audit(&ops,&input,&[]).unwrap();assert_eq!(result.qubits,input);assert_eq!(result.measurements,2);
        assert!(result.maximum_quantum_size_bound>1);
        for m in [0,u64::MAX] {for n in [0,u64::MAX] {let(q,phase)=native(&ops,&input,&[m,n]);assert_eq!(q,input);assert_eq!(phase,0);}}
    }
    #[test]
    fn discarded_phase_only_block_is_detected() {
        let ops=vec![gate(K::Hmr,None,None,Some(0),Some(0),None),
            gate(K::PushCondition,None,None,None,None,Some(0)),
            gate(K::CCZ,Some(1),Some(2),Some(3),None,None),
            gate(K::PopCondition,None,None,None,None,None)];
        assert!(audit(&ops,&[0,u64::MAX,u64::MAX,u64::MAX],&[]).unwrap_err().starts_with("nonzero phase polynomial"));
        assert_eq!(native(&ops,&[0,u64::MAX,u64::MAX,u64::MAX],&[u64::MAX]).1,u64::MAX);
    }
    #[test]
    fn node_budget_is_inconclusive_and_boolean_identities_hold(){
        reset_manager();let a=Poly::variable(0).unwrap();let b=Poly::variable(1).unwrap();
        let f=a.xor(&b).unwrap();assert_eq!(f.and(&f).unwrap(),f);
        assert_eq!(f.and(&f.not().unwrap()).unwrap().scalar(),Some(0));
        GRAPH.with(|g|{let mut m=g.borrow_mut();m.limit=m.nodes.len()+2;});
        assert!(GRAPH.with(|g|{let mut m=g.borrow_mut();let _=m.branch(10,0,1)?;let _=m.branch(11,0,1)?;m.branch(12,0,1)}).unwrap_err().starts_with("inconclusive:"));
        reset_manager();
    }
}
