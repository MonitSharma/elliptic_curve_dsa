//! Structural feasibility only. No point-addition candidate is emitted here.
include!("detector.rs");
use std::collections::BTreeSet;
use sha3::{Digest,Sha3_256};
type Poly=BTreeSet<u64>;
fn poly(m:&[u64])->Poly{m.iter().copied().collect()}
fn mul(a:&Poly,b:&Poly)->Poly{let mut out=Poly::new();for &x in a{for &y in b{let m=x|y;if !out.remove(&m){out.insert(m);}}}out}
fn decode(q:u64,s:&Hold,external:&[u64])->Poly{
 if q==s.a{if s.compact{poly(&[1,4])}else{poly(&[1,2,5])}}
 else if q==s.b{if s.compact{poly(&[4])}else{poly(&[2,5])}}
 else if q==s.c{poly(&[4,2,5])}else if q==s.t{poly(&[2])}
 else{poly(&[1<<(3+external.binary_search(&q).unwrap())])}
}
fn query(o:&Op,s:&Hold)->Result<Vec<Op>,&'static str>{
 if matches!(o.kind,K::Register|K::AppendToRegister){return Ok(vec![*o]);}
 let core=[s.a,s.b,s.c,s.t];if !qubits(o).any(|q|core.contains(&q)){return Ok(vec![*o]);}
 let (phase,controls): (bool,Vec<u64>)=match o.kind{
  K::CX=>(false,vec![o.q_control1.0]),K::CCX=>(false,vec![o.q_control1.0,o.q_control2.0]),
  K::Z=>(true,vec![o.q_target.0]),K::CZ=>(true,vec![o.q_control1.0,o.q_target.0]),K::CCZ=>(true,vec![o.q_control1.0,o.q_control2.0,o.q_target.0]),
  _=>return Err("unsupported_operand_touch")};
 if !phase&&core.contains(&o.q_target.0){return Err("operand_or_carry_write");}
 let mut external:Vec<_>=qubits(o).filter(|q|!core.contains(q)).collect();external.sort_unstable();external.dedup();assert!(external.len()<=3);
 let mut p=poly(&[0]);for q in controls{p=mul(&p,&decode(q,s,&external));}
 if p.iter().any(|m|m.count_ones()>if phase{3}else{2}){return Err("unsupported_decoded_degree");}
 let mut ids=vec![s.a,s.b,s.c];ids.extend(external);let mut out=vec![];
 for mask in p{let qs:Vec<_>=(0..ids.len()).filter(|i|mask>>i&1!=0).map(|i|ids[i]).collect();let mut n=Op::empty();n.c_condition=o.c_condition;
  if phase{match qs.len(){0=>n.kind=K::Neg,1=>{n.kind=K::Z;n.q_target=QubitId(qs[0]);},2=>{n.kind=K::CZ;n.q_control1=QubitId(qs[0]);n.q_target=QubitId(qs[1]);},3=>{n.kind=K::CCZ;n.q_control2=QubitId(qs[0]);n.q_control1=QubitId(qs[1]);n.q_target=QubitId(qs[2]);},_=>unreachable!()}}
  else{n.q_target=o.q_target;match qs.len(){0=>n.kind=K::X,1=>{n.kind=K::CX;n.q_control1=QubitId(qs[0]);},2=>{n.kind=K::CCX;n.q_control2=QubitId(qs[0]);n.q_control1=QubitId(qs[1]);},_=>unreachable!()}}
  n.validate();out.push(n);
 }Ok(out)
}
fn tcost(v:&[Op])->usize{v.iter().filter(|o|matches!(o.kind,K::CCX|K::CCZ)).count()}
#[cfg(test)]fn capsule(v:&[Op],s:&Hold)->Vec<Op>{let mut out=v[..s.start].to_vec();out.extend([gate(K::CX,s.b,NO,s.a),gate(K::CX,s.b,NO,s.c),gate(K::CCX,s.a,s.c,s.b)]);for o in &v[s.start+s.forward_len()..s.end]{out.extend(query(o,s).unwrap());}out.extend([gate(K::CCX,s.a,s.c,s.b),gate(K::CX,s.b,NO,s.c),gate(K::CX,s.c,NO,s.a)]);out.extend_from_slice(&v[s.end+s.reverse_len()..]);out}
fn hash(v:&[Op])->String{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())}
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let v=io::load_ops(&args[1]);assert_eq!(hash(&v),"ebab2fda1ccaa1d08a2e804729e673c72a3db98078d5a69563031ca415bb3919");let candidates=discover(&v,0);let nq=v.iter().flat_map(qubits).max().unwrap_or(0)as usize+1;let mut touches:Vec<Vec<usize>>=vec![vec![];nq];for(i,o)in v.iter().enumerate(){for q in qubits(o){touches[q as usize].push(i);}}
 let mut eligible=vec![];let mut rejects:std::collections::BTreeMap<&str,usize>=std::collections::BTreeMap::new();let mut structurally_reading=0;
 for s in &candidates{let mut ids=vec![];for q in [s.a,s.b,s.c,s.t]{let t=&touches[q as usize];let lo=t.partition_point(|&i|i<s.start+s.forward_len());let hi=t.partition_point(|&i|i<s.end);ids.extend_from_slice(&t[lo..hi]);}ids.sort_unstable();ids.dedup();let mut cost=1;let mut operand_reads=0;let mut bad=None;
  for &i in &ids{if qubits(&v[i]).any(|q|[s.a,s.b,s.c].contains(&q)){operand_reads+=1;}match query(&v[i],s){Ok(w)=>{cost+=tcost(&w).saturating_sub(tcost(&[v[i]]));if cost>600{bad=Some("single_cell_over_budget");break;}},Err(e)=>{bad=Some(e);break;}}}
  if operand_reads>0{structurally_reading+=1;}if let Some(reason)=bad{*rejects.entry(reason).or_default()+=1;continue;}
  eligible.push(serde_json::json!({"start":s.start,"end":s.end,"full_end_exclusive":s.end+s.reverse_len(),"save_begin":s.start+2,"save_end":s.end+s.reverse_len()-1,"last_main_measurement":s.end+s.measurement_offset(),"a":s.a,"b":s.b,"c":s.c,"t":s.t,"removed_bit":s.bit,"compact":s.compact,"forward_length":s.forward_len(),"reverse_length":s.reverse_len(),"worst_case_added_T":cost,"body_queries":ids.len(),"operand_queries":operand_reads}));
 }
 let result=serde_json::json!({"status":"READ_ONLY_CARRY_STRUCTURAL_DIAGNOSTIC_NOT_A_SCORE","input":args[1],"input_count":v.len(),"input_sha3_256":hash(&v),"stable_operand_cells":candidates.len(),"cells_examined_with_operand_reads":structurally_reading,"eligible_cells":eligible.len(),"rejects":rejects,"whole_program_budget_T":600,"cells":eligible,"scope":"No full candidate emitted. Independent complete peak-cover and final measured width required."});std::fs::write(&args[2],serde_json::to_string_pretty(&result).unwrap()).unwrap();println!("stable={} eligible={} rejected={}",candidates.len(),result["eligible_cells"],result["rejects"]);
}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::{circuit::{BitId,RegisterId},sim::Simulator};use sha3::digest::XofReader;
 fn fixture(compact:bool,extra_reset:bool)->Vec<Op>{let(a,b,c,t)=(0,1,2,3);let mut v=vec![];for q in [0,1,2,4,5,6]{let mut r=Op::empty();r.kind=K::AppendToRegister;r.q_target=QubitId(q);r.r_target=RegisterId(0);v.push(r);}let mut cr=Op::empty();cr.kind=K::AppendToRegister;cr.c_target=BitId(1);cr.r_target=RegisterId(1);v.push(cr);
  if compact{v.extend([gate(K::CX,c,NO,b),gate(K::CX,c,NO,a),gate(K::CCX,a,b,t),gate(K::CX,c,NO,t)]);}else{v.extend([gate(K::CX,c,NO,a),gate(K::CX,c,NO,b),gate(K::CCX,a,b,t),gate(K::CX,c,NO,b),gate(K::CX,c,NO,t),gate(K::CX,c,NO,a)]);}
  for q in [a,b,c,t]{let mut o=gate(K::CX,q,NO,4);o.c_condition=BitId(1);v.push(o);}let mut cc=gate(K::CCX,a,b,6);cc.c_condition=BitId(1);v.push(cc);let mut z=Op::empty();z.kind=K::Z;z.q_target=QubitId(a);z.c_condition=BitId(1);v.push(z);for (x,y)in[(a,b),(c,5),(t,c)]{let mut z=Op::empty();z.kind=K::CZ;z.q_control1=QubitId(x);z.q_target=QubitId(y);z.c_condition=BitId(1);v.push(z);}
  v.push(gate(K::CX,c,NO,t));if !compact{v.extend([gate(K::CX,c,NO,a),gate(K::CX,c,NO,b)]);}let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(t);h.c_target=BitId(0);v.push(h);let mut phase=Op::empty();phase.kind=K::CZ;phase.q_control1=QubitId(a);phase.q_target=QubitId(b);phase.c_condition=BitId(0);v.push(phase);
  if compact{if extra_reset{let mut r=Op::empty();r.kind=K::R;r.q_target=QubitId(t);v.push(r);v.extend([gate(K::CX,c,NO,b),gate(K::CX,b,NO,a)]);}else{v.extend([gate(K::CX,b,NO,a),gate(K::CX,c,NO,b),gate(K::CX,c,NO,a)]);}}else{v.extend([gate(K::CX,c,NO,b),gate(K::CX,c,NO,a),gate(K::CX,b,NO,a),gate(K::CX,c,NO,a)]);}v.push(gate(K::CX,4,NO,5));v}
 struct Rng{data:Vec<u8>,at:usize}impl XofReader for Rng{fn read(&mut self,out:&mut[u8]){out.copy_from_slice(&self.data[self.at..self.at+out.len()]);self.at+=out.len();}}
 fn run(v:&[Op],bits:u64,flag:bool,m:bool,extra_reset:bool)->(Vec<u64>,u64,u64,u64,[u8;64]){let events=v.iter().filter(|o|matches!(o.kind,K::R|K::Hmr)).count();let mut data=vec![];for i in 0..events{data.extend((if if i==0{m}else{extra_reset}{u64::MAX}else{0}).to_le_bytes());}data.extend([0x5a;64]);let mut rng=Rng{data,at:0};let mut s=Simulator::new(7,2,&mut rng);for q in [0,1,2,4,5,6]{s.qubits[q]=if bits>>q&1!=0{u64::MAX}else{0};}s.bits[1]=if flag{u64::MAX}else{0};s.phase=0xaaaaffff55550000;s.apply_iter(v.iter());let state=(s.qubits.clone(),s.bits[1],s.phase,s.stats.toffoli_gates);drop(s);let mut after=[0;64];rng.read(&mut after);assert_eq!(rng.at,rng.data.len());(state.0,state.1,state.2,state.3,after)}
 #[test]fn complete_capsules_preserve_values_phase_registered_bits_and_rng_continuation(){for compact in [false,true]{for reset in [false,true]{if !compact&&reset{continue;}let v=fixture(compact,reset);let holds=discover(&v,0);assert_eq!(holds.len(),1);let s=&holds[0];let w=capsule(&v,s);let cost=1+v[s.start+s.forward_len()..s.end].iter().map(|o|tcost(&query(o,s).unwrap()).saturating_sub(tcost(&[*o]))).sum::<usize>();for bits in 0..128{if bits&8!=0{continue;}for flag in [false,true]{for m in [false,true]{for r in [false,true]{let a=run(&v,bits,flag,m,r);let b=run(&w,bits,flag,m,r);assert_eq!(a.0,b.0);assert_eq!(a.1,b.1);assert_eq!(a.2,b.2);assert_eq!(a.4,b.4);assert!(b.3<=a.3+64*cost as u64);}}}}}}}
 #[test]fn unsupported_cubic_xor_query_rejects(){let v=fixture(false,false);let s=discover(&v,0).pop().unwrap();assert_eq!(query(&gate(K::CCX,s.a,5,6),&s),Err("unsupported_decoded_degree"));}
 #[test]fn a_body_operand_write_blocks_discovery(){let mut v=fixture(true,false);v.insert(12,gate(K::CX,5,NO,0));assert!(discover(&v,0).is_empty());}
 #[test]fn registered_classical_cleanup_destination_is_rejected(){let mut v=fixture(true,false);let mut r=Op::empty();r.kind=K::AppendToRegister;r.c_target=BitId(0);r.r_target=RegisterId(2);v.insert(0,r);assert!(discover(&v,0).is_empty());}
 #[test]fn later_private_measurement_reader_is_rejected(){let mut v=fixture(true,false);let mut z=Op::empty();z.kind=K::Z;z.q_target=QubitId(5);z.c_condition=BitId(0);v.push(z);assert!(discover(&v,0).is_empty());}
}
