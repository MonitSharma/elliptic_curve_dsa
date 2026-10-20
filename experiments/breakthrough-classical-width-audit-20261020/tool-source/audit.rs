mod io;
use quantum_ecc::circuit::{OperationType as K,Op,NO_BIT,NO_QUBIT,analyze_ops,QubitOrBit};
use serde_json::json;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]enum V{Zero,One,Classical,Quantum}
fn and(a:V,b:V)->V{use V::*;match(a,b){(Zero,_)|(_,Zero)=>Zero,(One,x)|(x,One)=>x,(Quantum,_)|(_,Quantum)=>Quantum,_=>Classical}}
fn xor(a:V,b:V)->V{use V::*;match(a,b){(Zero,x)|(x,Zero)=>x,(One,One)=>Zero,(Quantum,_)|(_,Quantum)=>Quantum,_=>Classical}}
fn inv(x:V)->V{xor(x,V::One)}
fn mux(old:V,new:V,c:V)->V{if c==V::One{new}else if c==V::Zero||old==new&&matches!(old,V::Zero|V::One){old}else if old!=V::Quantum&&new!=V::Quantum{V::Classical}else{V::Quantum}}
struct State{q:Vec<V>,b:Vec<V>,stack:Vec<V>,base:V}
impl State{
fn apply(&mut self,o:&Op){let cond=if o.c_condition==NO_BIT||o.kind==K::PushCondition{self.base}else{and(self.base,self.b[o.c_condition.0 as usize])};let t=o.q_target.0 as usize;match o.kind{
K::X=>self.q[t]=xor(self.q[t],cond),K::CX=>self.q[t]=xor(self.q[t],and(cond,self.q[o.q_control1.0 as usize])),K::CCX=>self.q[t]=xor(self.q[t],and(cond,and(self.q[o.q_control1.0 as usize],self.q[o.q_control2.0 as usize]))),
K::Swap=>{let a=o.q_control1.0 as usize;let(x,y)=(self.q[a],self.q[t]);self.q[a]=mux(x,y,cond);self.q[t]=mux(y,x,cond);},
K::R|K::Hmr=>{self.q[t]=mux(self.q[t],V::Zero,cond);if o.kind==K::Hmr{let b=o.c_target.0 as usize;self.b[b]=mux(self.b[b],V::Classical,cond);}},
K::BitStore0|K::BitStore1|K::BitInvert=>{let b=o.c_target.0 as usize;let v=match o.kind{K::BitStore0=>V::Zero,K::BitStore1=>V::One,_=>inv(self.b[b])};self.b[b]=mux(self.b[b],v,cond);},
K::PushCondition=>{self.stack.push(self.base);self.base=and(self.base,self.b[o.c_condition.0 as usize]);},K::PopCondition=>self.base=self.stack.pop().unwrap(),_=>{}}}
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let(nq,nb,_,regs)=analyze_ops(ops.iter());let n=nq as usize;let high=n-1;let mut inputs=vec![false;n];let mut s=State{q:vec![V::Zero;n],b:vec![V::Zero;nb as usize],stack:vec![],base:V::One};for reg in regs{for slot in reg{match slot{QubitOrBit::Qubit(q)=>{inputs[q.0 as usize]=true;s.q[q.0 as usize]=V::Quantum;},QubitOrBit::Bit(b)=>s.b[b.0 as usize]=V::Classical}}}
let mut touches=vec![Vec::<usize>::new();n];for(k,o)in ops.iter().enumerate(){for q in[o.q_control2,o.q_control1,o.q_target]{if q!=NO_QUBIT{touches[q.0 as usize].push(k);}}}for t in &mut touches{t.dedup();}
let mut ends=Vec::new();for &k in &touches[high]{let o=ops[k];if o.q_target.0 as usize==high&&matches!(o.kind,K::R|K::Hmr)&&o.c_condition==NO_BIT{ends.push(k);}}
let mut rows=Vec::new();let mut begin=None;let mut snapshot=Vec::<(usize,V)>::new();let mut last_end=None;let mut stack_depth=0i32;
for(k,o)in ops.iter().enumerate(){let touches_high=[o.q_control2,o.q_control1,o.q_target].iter().any(|q|q.0 as usize==high);if touches_high&&begin.is_none(){begin=Some(k);snapshot=(512..high).filter(|&q|!inputs[q]&&s.q[q]!=V::Quantum).map(|q|(q,s.q[q])).collect();}
let unconditional_reset=touches_high&&o.q_target.0 as usize==high&&matches!(o.kind,K::R|K::Hmr)&&o.c_condition==NO_BIT&&stack_depth==0;
if unconditional_reset{let start=begin.take().unwrap();let candidates:Vec<_>=snapshot.iter().filter_map(|&(q,v)|{let pos=touches[q].partition_point(|&x|x<start);let next=touches[q].get(pos).copied().unwrap_or(ops.len());(next>k).then(||json!({"wire":q,"kind":format!("{:?}",v),"next_quantum_touch":next}))}).collect();rows.push(json!({"start":start,"end":k,"operations":k-start+1,"next_previous_interval_end":last_end,"idle_classical_or_zero_donors":candidates}));last_end=Some(k);}
s.apply(o);match o.kind{K::PushCondition=>stack_depth+=1,K::PopCondition=>stack_depth-=1,_=>{}}}
assert_eq!(stack_depth,0);let with_donors=rows.iter().filter(|r|!r["idle_classical_or_zero_donors"].as_array().unwrap().is_empty()).count();let result=json!({"status":"READ_ONLY_CONSERVATIVE_NOMINATION_NOT_A_WIDTH_BOUND_OR_REWRITE","operations":ops.len(),"qubits":nq,"highest_wire":high,"highest_wire_touches":touches[high].len(),"closed_intervals":rows.len(),"closed_intervals_with_nominees":with_donors,"unclosed_interval_start":begin,"intervals":rows,"scope":"Classical taint and unconditional-reset delimiters are conservative. No quantum rank/correctness/benchmark claim. Need separate exact snapshot and full remapping proof before any rewrite."});std::fs::write(&a[2],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("{}",json!({"highest_wire":high,"intervals":rows.len(),"with_nominees":with_donors,"unclosed":begin}));}
#[cfg(test)]mod tests{use super::*;use quantum_ecc::circuit::{QubitId,BitId};fn state()->State{State{q:vec![V::Quantum,V::Classical,V::Zero],b:vec![V::Classical,V::Zero],stack:vec![],base:V::One}}
#[test]fn conditional_reset_never_proves_an_unknown_input_zero(){let mut s=state();let mut o=Op::empty();o.kind=K::R;o.q_target=QubitId(0);o.c_condition=BitId(0);s.apply(&o);assert_eq!(s.q[0],V::Quantum);o.c_condition=NO_BIT;s.apply(&o);assert_eq!(s.q[0],V::Zero);}
#[test]fn conditional_swap_with_quantum_operand_taints_both(){let mut s=state();let mut o=Op::empty();o.kind=K::Swap;o.q_control1=QubitId(0);o.q_target=QubitId(1);o.c_condition=BitId(0);s.apply(&o);assert_eq!(s.q[..2],[V::Quantum,V::Quantum]);}
#[test]fn classical_copy_and_false_control_remain_classical(){let mut s=state();let mut o=Op::empty();o.kind=K::CX;o.q_control1=QubitId(1);o.q_target=QubitId(2);s.apply(&o);assert_eq!(s.q[2],V::Classical);o.q_control1=QubitId(0);o.c_condition=BitId(1);s.apply(&o);assert_eq!(s.q[2],V::Classical);}
}
