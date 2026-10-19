//! Exact local carry replacement. Research tool, never a scored result.
mod io;
use quantum_ecc::circuit::{Op,OperationType as K,QubitId};
use std::collections::{HashMap,HashSet};
const NO:u64=u64::MAX;
#[derive(Clone,Debug)]
struct Hold { start:usize,end:usize,a:u64,b:u64,c:u64,t:u64,bit:u64 }
fn cx(o:&Op,c:u64,t:u64)->bool {o.kind==K::CX&&o.q_control1.0==c&&o.q_target.0==t&&o.c_condition.0==NO}
fn pair(o:&Op,k:K,a:u64,b:u64)->bool {o.kind==k&&((o.q_control1.0==a&&o.q_control2.0==b)||(o.q_control1.0==b&&o.q_control2.0==a))}
fn opening(v:&[Op],i:usize)->Option<Hold>{
 let w=v.get(i..i+6)?; let(c,a,b,t)=(w[0].q_control1.0,w[0].q_target.0,w[1].q_target.0,w[2].q_target.0);
 if [a,b,c,t].iter().copied().collect::<HashSet<_>>().len()!=4||[a,b,c,t].contains(&NO){return None;}
 (cx(&w[0],c,a)&&cx(&w[1],c,b)&&pair(&w[2],K::CCX,a,b)&&w[2].c_condition.0==NO&&cx(&w[3],c,b)&&cx(&w[4],c,t)&&cx(&w[5],c,a)).then_some(Hold{start:i,end:0,a,b,c,t,bit:NO})
}
fn closing(v:&[Op],i:usize,s:&Hold)->Option<u64>{
 let w=v.get(i..i+9)?;let(a,b,c,t)=(s.a,s.b,s.c,s.t);let bit=w[3].c_target.0;
 (cx(&w[0],c,t)&&cx(&w[1],c,a)&&cx(&w[2],c,b)&&w[3].kind==K::Hmr&&w[3].q_target.0==t&&w[3].c_condition.0==NO&&w[4].kind==K::CZ&&((w[4].q_control1.0==a&&w[4].q_target.0==b)||(w[4].q_control1.0==b&&w[4].q_target.0==a))&&w[4].c_condition.0==bit&&cx(&w[5],c,b)&&cx(&w[6],c,a)&&cx(&w[7],b,a)&&cx(&w[8],c,a)).then_some(bit)
}
fn qubits(o:&Op)->impl Iterator<Item=u64>{[o.q_control2.0,o.q_control1.0,o.q_target.0].into_iter().filter(|&x|x!=NO)}
fn discover(v:&[Op],minimum:u64)->Vec<Hold>{
 let nq=v.iter().flat_map(qubits).max().unwrap()as usize+1;
 let pinned:HashSet<_>=v.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=NO).map(|o|o.q_target.0).collect();
 // Prove that the removed measurement's bit has no further reader before a
 // definite unconditional overwrite. Unknown enclosing guards are excluded.
 let nb=v.iter().flat_map(|o|[o.c_condition.0,o.c_target.0]).filter(|&x|x!=NO).max().unwrap_or(0)as usize+1;
 let mut depth=0;let mut depths=vec![0u16;v.len()];
 for(i,o)in v.iter().enumerate(){depths[i]=depth;if o.kind==K::PushCondition{depth+=1;}if o.kind==K::PopCondition{depth-=1;}}
 assert_eq!(depth,0);
 let mut safe=vec![true;nb];let mut hmr_safe=HashSet::new();
 for(i,o)in v.iter().enumerate().rev(){
  if o.kind==K::Hmr&&o.c_target.0!=NO&&i+1<v.len()&&v[i+1].kind==K::CZ&&v[i+1].c_condition.0==o.c_target.0 {
   // safe currently includes the one immediate CZ. Check its successor
   // separately below, where suffix safety is captured before that reader.
  }
  if i>0&&o.kind==K::CZ&&o.c_condition.0!=NO&&v[i-1].kind==K::Hmr&&v[i-1].c_target.0==o.c_condition.0&&safe[o.c_condition.0 as usize]{hmr_safe.insert(i-1);}
  if o.c_target.0!=NO {let b=o.c_target.0 as usize;safe[b]=matches!(o.kind,K::Hmr|K::BitStore0|K::BitStore1)&&depths[i]==0&&o.c_condition.0==NO;}
  if o.c_condition.0!=NO{safe[o.c_condition.0 as usize]=false;}
 }
 let mut known_zero=vec![true;nq];for &q in &pinned{known_zero[q as usize]=false;}
 let mut last=vec![None;nq];let mut open:HashMap<u64,Hold>=HashMap::new();let mut found=vec![];
 let mut pending:HashMap<usize,Hold>=HashMap::new();
 for(i,o)in v.iter().enumerate(){
  if let Some(s)=pending.remove(&i){open.insert(s.t,s);}
  if depths[i]==0&&o.kind==K::CX {
   let t=o.q_target.0;
   if let Some(s)=open.get(&t){
    if let Some(bit)=closing(v,i,s){
     if [s.a,s.b,s.c].iter().all(|&q|last[q as usize].map_or(true,|at|at<s.start+6))&&hmr_safe.contains(&(i+3)){
      let mut s=s.clone();s.end=i;s.bit=bit;found.push(s);
     }
    }
   }
  }
  if depths[i]==0 {if let Some(s)=opening(v,i){if s.t>=minimum&&!pinned.contains(&s.t)&&known_zero[s.t as usize]{pending.insert(i+6,s);}}}
  for q in qubits(o){last[q as usize]=Some(i);}
  if o.q_target.0!=NO {
   let t=o.q_target.0 as usize;
   if !matches!(o.kind,K::Register|K::AppendToRegister|K::Z|K::CZ|K::CCZ|K::DebugPrint){
    // A held carry must be read-only between its constructor and cleanup.
    open.remove(&(t as u64));
    known_zero[t]=matches!(o.kind,K::R|K::Hmr)&&depths[i]==0&&o.c_condition.0==NO;
   }
   if o.kind==K::Swap&&o.q_control1.0!=NO{known_zero[o.q_control1.0 as usize]=false;open.remove(&o.q_control1.0);}
  }
 }
 found.sort_by_key(|s|s.start);
 // Composition uses nested or disjoint scopes; crossing intervals are rejected.
 let mut accepted:Vec<Hold>=vec![];let mut ends=vec![];
 for s in found{while ends.last().is_some_and(|&e|e<s.start){ends.pop();}if ends.last().is_some_and(|&e|s.end+9>e){continue;}ends.push(s.end+9);accepted.push(s);}
 accepted
}
fn gate(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_target=QubitId(t);o.q_control1=QubitId(a);if k==K::CCX{o.q_control2=QubitId(b);}o.validate();o}
fn resolve(mut q:u64,m:&HashMap<u64,u64>)->u64{let mut n=0;while let Some(&p)=m.get(&q){q=p;n+=1;assert!(n<=m.len());}q}
fn rewrite(v:&[Op],ss:&[Hold])->Vec<Op>{
 let starts:HashMap<_,_>=ss.iter().map(|s|(s.start,s)).collect();let ends:HashMap<_,_>=ss.iter().map(|s|(s.end,s)).collect();let mut map=HashMap::new();let mut out=Vec::with_capacity(v.len());let mut i=0;
 while i<v.len(){
  if let Some(s)=starts.get(&i){
   let(a,b,c)=(resolve(s.a,&map),resolve(s.b,&map),resolve(s.c,&map));assert_ne!(b,c);assert_ne!(a,b);assert_ne!(a,c);
   out.extend([gate(K::CX,b,NO,a),gate(K::CX,b,NO,c),gate(K::CCX,a,c,b)]);
   assert!(map.insert(s.t,s.b).is_none());i+=6;
  }else if let Some(s)=ends.get(&i){
   let(a,b,c)=(resolve(s.a,&map),resolve(s.b,&map),resolve(s.c,&map));
   out.extend([gate(K::CCX,a,c,b),gate(K::CX,b,NO,c),gate(K::CX,c,NO,a)]);
   assert_eq!(map.remove(&s.t),Some(s.b));i+=9;
  }else{let mut o=v[i];o.q_control1=QubitId(resolve(o.q_control1.0,&map));o.q_control2=QubitId(resolve(o.q_control2.0,&map));o.q_target=QubitId(resolve(o.q_target.0,&map));o.validate();out.push(o);i+=1;}
 }
 assert!(map.is_empty());out
}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let v=io::load_ops(&a[1]);let minimum=a[2].parse().unwrap();let ss=discover(&v,minimum);let out=rewrite(&v,&ss);io::save_ops(&format!("{}.ops.bin",a[3]),&out);
 use sha3::{Digest,Sha3_256};let hash=|v:&[Op]|{let mut h=Sha3_256::new();for o in v{for x in [o.kind as u64,o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(x.to_le_bytes());}}format!("{:x}",h.finalize())};
 let data=serde_json::json!({"status":"EXACT_CARRY_BORROW_DIAGNOSTIC_NOT_A_SCORE","input":a[1],"input_count":v.len(),"input_sha3_256":hash(&v),"output_count":out.len(),"output_sha3_256":hash(&out),"minimum_carry_wire":minimum,"replaced_carries":ss.len(),"added_unconditional_Toffolis":ss.len(),"sites":ss.iter().map(|s|serde_json::json!({"start":s.start,"end":s.end,"a":s.a,"b":s.b,"c":s.c,"t":s.t,"removed_bit":s.bit})).collect::<Vec<_>>()});
 std::fs::write(format!("{}.json",a[3]),serde_json::to_string_pretty(&data).unwrap()).unwrap();println!("replaced={} added_T={} removed_ops={}",ss.len(),ss.len(),v.len()-out.len());
}
#[cfg(test)]mod tests{
 use super::*;use quantum_ecc::circuit::BitId;
 fn fixture()->Vec<Op>{let(a,b,c,t)=(0,1,2,3);let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(t);h.c_target=BitId(0);let mut z=Op::empty();z.kind=K::CZ;z.q_control1=QubitId(a);z.q_target=QubitId(b);z.c_condition=BitId(0);
 vec![gate(K::CX,c,NO,a),gate(K::CX,c,NO,b),gate(K::CCX,a,b,t),gate(K::CX,c,NO,b),gate(K::CX,c,NO,t),gate(K::CX,c,NO,a),gate(K::CX,t,NO,4),gate(K::CX,c,NO,t),gate(K::CX,c,NO,a),gate(K::CX,c,NO,b),h,z,gate(K::CX,c,NO,b),gate(K::CX,c,NO,a),gate(K::CX,b,NO,a),gate(K::CX,c,NO,a)]}
 fn simulate(v:&[Op],mut x:u64,m:bool)->(u64,bool){let mut phase=false;for o in v{let q=|i:u64|x>>i&1!=0;match o.kind{K::CX=>if q(o.q_control1.0){x^=1<<o.q_target.0},K::CCX=>if q(o.q_control1.0)&&q(o.q_control2.0){x^=1<<o.q_target.0},K::Hmr=>{phase^=m&&q(o.q_target.0);x&=!(1<<o.q_target.0)},K::CZ=>phase^=m&&q(o.q_control1.0)&&q(o.q_target.0),_=>panic!("unsupported")}}(x,phase)}
 #[test]fn exact_values_and_every_measurement_phase(){let v=fixture();let s=discover(&v,3);assert_eq!(s.len(),1);let w=rewrite(&v,&s);for x in 0..32{if x&8!=0{continue;}for m in [false,true]{assert_eq!(simulate(&v,x,m),simulate(&w,x,m));}}}
 #[test]fn missing_reverse_toffoli_is_detected(){let v=fixture();let ss=discover(&v,3);let mut w=rewrite(&v,&ss);w.remove(4);assert!((0..8).any(|x|simulate(&v,x,false)!=simulate(&w,x,false)));}
 #[test]fn operand_read_blocks_borrow(){let mut v=fixture();v.insert(7,gate(K::CX,1,NO,4));assert!(discover(&v,3).is_empty());}
 #[test]fn dirty_initial_carry_blocks_borrow(){let mut v=fixture();v.insert(0,gate(K::CX,0,NO,3));assert!(discover(&v,3).is_empty());}
 #[test]fn extra_classical_reader_blocks_borrow(){let mut v=fixture();let mut z=Op::empty();z.kind=K::Z;z.q_target=QubitId(4);z.c_condition=BitId(0);v.push(z);assert!(discover(&v,3).is_empty());}
 #[test]fn unconditional_bit_overwrite_allows_borrow(){let mut v=fixture();let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(4);h.c_target=BitId(0);v.push(h);assert_eq!(discover(&v,3).len(),1);}
 #[test]fn registered_carry_is_never_borrowed(){let mut v=fixture();let mut o=Op::empty();o.kind=K::AppendToRegister;o.q_target=QubitId(3);o.r_target=quantum_ecc::circuit::RegisterId(0);v.push(o);assert!(discover(&v,3).is_empty());}
}
