use crate::circuit::{Op,OperationType as K,QubitId,BitId,analyze_ops};
use sha3::{Digest,Sha3_256};
use std::collections::HashMap;
const LEASES:&[[u64;9]]=&[__TABLE__];
fn op(kind:K,a:u64,b:u64,t:u64,ct:u64,cc:u64)->Op{let mut o=Op::empty();o.kind=kind;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o.c_target=BitId(ct);o.c_condition=BitId(cc);o.validate();o}
fn rewrite(ops:Vec<Op>,leases:&[[u64;9]],bit:u64)->Vec<Op>{
 let no=u64::MAX;let starts:HashMap<_,_>=leases.iter().map(|row|(row[0]as usize,row)).collect();let ends:HashMap<_,_>=leases.iter().map(|row|(row[1]as usize,row)).collect();let mut out=Vec::with_capacity(ops.len()+3*leases.len());
 for(i,o)in ops.into_iter().enumerate(){if let Some(s)=starts.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!(o.c_condition.0,no);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);let mut fill=o;fill.q_target=QubitId(s[2]);out.push(fill);out.push(op(K::CX,s[2],no,s[5],no,no));}else if let Some(s)=ends.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!(o.c_condition.0,no);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);out.push(op(K::CX,s[2],no,s[8],no,no));out.push(op(K::Hmr,no,no,s[2],bit,no));out.push(op(K::CZ,s[6],no,s[7],no,bit));}else{out.push(o);}}
 out
}
pub(super)fn run(ops:Vec<Op>)->Vec<Op>{
 assert_eq!(ops.len(),__COUNT__);let mut hash=Sha3_256::new();for o in &ops{for v in[o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{hash.update(v.to_le_bytes());}}assert_eq!(format!("{:x}",hash.finalize()),"__HASH__","Frozen exact154 input prefix");let(_,nb,_,_)=analyze_ops(ops.iter());let out=rewrite(ops,LEASES,nb);let(nq,nb,_,_)=analyze_ops(out.iter());eprintln!("EXACT154_CACHE leases={} operations={} qubits={} bits={} diagnostic_toffoli_saving=154",LEASES.len(),out.len(),nq,nb);out
}
#[cfg(test)]mod tests{
 use super::*;use crate::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 #[test]fn exact154_rewrite_preserves_all_small_values_phase_cleanup_cost_and_detects_bad_repair(){let no=u64::MAX;let ops=vec![op(K::CCX,1,0,2,no,no),op(K::CX,0,no,1,no,no),op(K::X,no,no,1,no,no),op(K::CCX,1,0,3,no,no)];let out=rewrite(ops.clone(),&[[0,3,4,0,1,2,0,1,3]],0);let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();let mut caught=0;
  for word in[0,255,0xa5,0x5a]{let mut ar=Fixed(word);let mut br=Fixed(word);let mut cr=Fixed(word);let mut a=Simulator::new(5,1,&mut ar);let mut b=Simulator::new(5,1,&mut br);let mut c=Simulator::new(5,1,&mut cr);for lane in 0..64{for q in 0..4{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}}b.qubits.clone_from(&a.qubits);c.qubits.clone_from(&a.qubits);a.apply_iter(ops.iter());b.apply_iter(out.iter());c.apply_iter(faulty.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.phase,b.phase);assert_eq!(b.qubits[4],0);assert_eq!(a.stats.toffoli_gates-b.stats.toffoli_gates,64);caught+=usize::from(a.phase!=c.phase);}
  assert!(caught>0);
 }
}
