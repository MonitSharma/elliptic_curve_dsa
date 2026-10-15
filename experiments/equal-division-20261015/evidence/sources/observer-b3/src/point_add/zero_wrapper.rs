//! Reversible zero-payload extension for a nonzero, phase-correct field oracle.
use super::builder::Builder;
use crate::circuit::QubitId;
use alloy_primitives::U256;
fn modulus()->U256{U256::MAX-U256::from(0x1000003d0u64)}
fn equality_xor(c:&mut Builder,word:&[QubitId],pattern:U256,flag:QubitId){
 assert!(!word.is_empty());
 for(i,&q)in word.iter().enumerate(){if !pattern.bit(i){c.x(q);}}
 if word.len()==1 {c.cx(word[0],flag);} else {
  let mut prior=word[0];let mut chain=Vec::new();
  for &q in &word[1..word.len()-1]{let out=c.alloc_qubit();c.ccx(prior,q,out);chain.push((out,prior,q));prior=out;}
  c.ccx(prior,word[word.len()-1],flag);
  for(out,a,b)in chain.into_iter().rev(){let bit=c.alloc_bit();c.hmr(out,bit);c.cz_if(a,b,bit);c.free_bit(bit);c.release_clean(out);}
 }
 for(i,&q)in word.iter().enumerate(){if !pattern.bit(i){c.x(q);}}
}
fn xor_constant(c:&mut Builder,control:QubitId,y:&[QubitId],value:U256){for(i,&q)in y.iter().enumerate(){if value.bit(i){c.cx(control,q);}}}
pub fn apply(c:&mut Builder,y:&[QubitId],x:&[QubitId],divide:bool){
 assert_eq!(y.len(),256);assert_eq!(x.len(),256);assert!(!super::leapfrog::seams());assert!(!super::leapfrog::t6_seedfuse());
 let before=c.active_qubits();let z0=c.alloc_qubit();let zp=c.alloc_qubit();
 equality_xor(c,y,U256::ZERO,z0);equality_xor(c,y,modulus(),zp);
 c.cx(zp,z0);xor_constant(c,zp,y,modulus());
 if divide{for(&a,&b)in x.iter().zip(y){c.ccx(z0,a,b);}}else{c.cx(z0,y[0]);}
 if divide{super::leapfrog::divide(c,y,x);}else{super::leapfrog::multiply(c,y,x);}
 if divide{c.cx(z0,y[0]);}else{for(&a,&b)in x.iter().zip(y){c.ccx(z0,a,b);}}
 xor_constant(c,zp,y,modulus());c.cx(zp,z0);
 equality_xor(c,y,U256::ZERO,z0);equality_xor(c,y,modulus(),zp);
 c.release_clean(zp);c.release_clean(z0);assert_eq!(c.active_qubits(),before);
}
#[cfg(test)]
mod tests{
 use super::*;
 use crate::circuit::{analyze_ops,OperationType};
 #[test]
 fn exhaustive_equality_all_measurements(){
  let(mut cases,mut batches)=(0usize,0usize);
  for n in 1..=8{for pattern in 0..(1usize<<n){
   let mut c=Builder::new();let word=c.alloc_qubits(n);let flag=c.alloc_qubit();equality_xor(&mut c,&word,U256::from(pattern),flag);let ops=c.take_ops();let(nq,_,_,_)=analyze_ops(ops.iter());
   for base in (0..(2usize<<n)).step_by(64){let mut input=vec![0u64;nq as usize];let mut expected=input.clone();
    for lane in 0..64{let sample=(base+lane)%(2usize<<n);let value=sample>>1;let dirty=sample&1;for i in 0..n{if(value>>i)&1==1{input[word[i].0 as usize]|=1u64<<lane;}}if dirty==1{input[flag.0 as usize]|=1u64<<lane;}expected.clone_from(&input);}
    expected.clone_from(&input);
    for lane in 0..64{let sample=(base+lane)%(2usize<<n);if sample>>1==pattern{expected[flag.0 as usize]^=1u64<<lane;}}
    let audited=super::super::zero_proof::audit(&ops,&input,&[]).unwrap();assert_eq!(audited.qubits,expected);batches+=1;cases+=64.min((2usize<<n)-base);
   }
  }}
  eprintln!("ZERO_EQUALITY_PROOF cases={cases} batches={batches} all_measurements=true score=NONE");
 }
 #[test]
 fn missing_measurement_correction_is_rejected(){
  let mut c=Builder::new();let word=c.alloc_qubits(3);let flag=c.alloc_qubit();equality_xor(&mut c,&word,U256::from(7),flag);let mut ops=c.take_ops();let at=ops.iter().position(|op|op.kind==OperationType::CZ).unwrap();ops.remove(at);let(nq,_,_,_)=analyze_ops(ops.iter());let mut input=vec![0;nq as usize];for q in word{input[q.0 as usize]=u64::MAX;}assert!(super::super::zero_proof::audit(&ops,&input,&[]).is_err());
 }
}
