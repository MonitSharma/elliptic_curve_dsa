use quantum_ecc::circuit::{Op,OperationType as K,QubitId,BitId};
use quantum_ecc::sim::Simulator;
use sha3::digest::XofReader;

struct Words {word:u64, draws:usize}
impl XofReader for Words {fn read(&mut self,o:&mut[u8]){assert_eq!(o.len(),8);o.copy_from_slice(&self.word.to_le_bytes());self.draws+=1;}}
fn op(k:K,a:Option<usize>,b:Option<usize>,t:Option<usize>,bc:Option<usize>,bt:Option<usize>)->Op{
 let mut o=Op::empty();o.kind=k;
 if let Some(v)=a{o.q_control1=QubitId(v as u64)}if let Some(v)=b{o.q_control2=QubitId(v as u64)}
 if let Some(v)=t{o.q_target=QubitId(v as u64)}if let Some(v)=bc{o.c_condition=BitId(v as u64)}if let Some(v)=bt{o.c_target=BitId(v as u64)}o.validate();o
}
fn cx(v:&mut Vec<Op>,a:usize,t:usize){if a!=t{v.push(op(K::CX,Some(a),None,Some(t),None,None));}}
fn ccx(v:&mut Vec<Op>,a:usize,b:usize,t:usize){v.push(op(K::CCX,Some(a),Some(b),Some(t),None,None));}
fn x(v:&mut Vec<Op>,a:usize){v.push(op(K::X,None,None,Some(a),None,None));}
fn make(clean:bool,alias:Option<bool>,bad:bool)->Vec<Op>{
 let mut v=Vec::new();let(a,b,c,t,u,d)=(0,1,2,3,4,5);
 // Two actual Push snapshots, independent mixed classical entry masks.
 for i in 0..2{v.push(op(K::PushCondition,None,None,None,Some(i),None));}
 // Deliberately overwrite the outer guard after Push: snapshot semantics.
 v.push(op(K::BitInvert,None,None,None,None,Some(0)));
 let conj=|v:&mut Vec<Op>|{match alias{None=>{cx(v,b,t);cx(v,c,t)},Some(false)=>{},Some(true)=>x(v,t)}};
 if clean{
  ccx(&mut v,a,b,d);cx(&mut v,b,d);conj(&mut v);ccx(&mut v,d,t,u);conj(&mut v);cx(&mut v,b,d);cx(&mut v,d,t);
  v.push(op(K::Hmr,None,None,Some(d),None,Some(2)));
  if !bad{v.push(op(K::CZ,Some(a),None,Some(b),Some(2),None));}
 }else{
  x(&mut v,a);conj(&mut v);
  for _ in 0..2{ccx(&mut v,a,b,d);ccx(&mut v,d,t,u)}
  conj(&mut v);x(&mut v,a);ccx(&mut v,a,b,t);
 }
 for _ in 0..2{v.push(op(K::PopCondition,None,None,None,None,None));}
 // A framed bit after Pop detects leaked guard scopes.
 v.push(op(K::BitInvert,None,None,None,None,Some(3)));v
}
fn next(s:&mut u64)->u64{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;*s}
fn square(inv:bool,bad:bool,dirty:bool)->Vec<Op>{
 let mut v=Vec::new();for i in 0..2{v.push(op(K::PushCondition,None,None,None,Some(i),None));}
 // q0=p, q1=a, q3=T, q4=U, q5=clean donor.
 if inv{x(&mut v,1);x(&mut v,3);}
 if dirty{
  for i in 0..2{ccx(&mut v,0,1,5);if !bad||i==0{ccx(&mut v,5,3,4);}}
  ccx(&mut v,0,1,3);
 }else{
  ccx(&mut v,0,1,5);ccx(&mut v,5,3,4);cx(&mut v,5,3);
  v.push(op(K::Hmr,None,None,Some(5),None,Some(2)));
  if !bad{v.push(op(K::CZ,Some(0),None,Some(1),Some(2),None));}
 }
 cx(&mut v,0,1);if inv{x(&mut v,1);x(&mut v,3);}
 for _ in 0..2{v.push(op(K::PopCondition,None,None,None,None,None));}v
}
fn main(){
 let mut cases=0;let mut negative_hits=0;let mut state=0x769a111df31997;
 for clean in [false,true]{for alias in [None,Some(false),Some(true)]{
  let ops=make(clean,alias,false);
  for case in 0..4096{
   let mut iq:[u64;8]=std::array::from_fn(|_|next(&mut state));
   let mut ib:[u64;5]=std::array::from_fn(|_|next(&mut state));
   if clean{iq[5]=0;}
   // Constant guards plus arbitrary bit planes; every case keeps unrelated
   // q/b dirty and initial phase arbitrary.
   if case<4{ib[0]=if case&1==0{0}else{u64::MAX};ib[1]=if case&2==0{0}else{u64::MAX};}
   let g=ib[0]&ib[1];let initial_phase=next(&mut state);let mr=next(&mut state);
   let c=match alias{None=>iq[2],Some(false)=>iq[1],Some(true)=>!iq[1]};
   let a=iq[0]^c;let sign=iq[1]^c;
   // Independent arithmetic oracle: two majority carries, not the emitted
   // factored terminal formula.
   let majority=|a:u64,b:u64,c:u64|(a&b)^(a&c)^(b&c);
   let lower=majority(a,sign,c);let upper=majority(iq[3],sign,lower);
   let mut eq=iq;eq[3]^=g&iq[0]&iq[1];eq[4]^=g&(upper^sign);
   let mut eb=ib;eb[0]^=g;eb[3]=!eb[3];if clean{eb[2]=(ib[2]&!g)^(mr&g);}
   let mut rng=Words{word:mr,draws:0};let mut s=Simulator::new(8,5,&mut rng);
   s.qubits.copy_from_slice(&iq);s.bits.copy_from_slice(&ib);s.phase=initial_phase;s.apply_iter(ops.iter());
   assert_eq!(s.qubits,eq,"all quantum outputs");assert_eq!(s.bits,eb,"all classical outputs");assert_eq!(s.phase,initial_phase,"exact phase");
   drop(s);assert_eq!(rng.draws,usize::from(clean),"inactive R/HMR draw count");cases+=64;
   if clean{
    let bad=make(clean,alias,true);let mut r=Words{word:mr,draws:0};let mut s=Simulator::new(8,5,&mut r);
    s.qubits.copy_from_slice(&iq);s.bits.copy_from_slice(&ib);s.phase=initial_phase;s.apply_iter(bad.iter());
    negative_hits+=(s.phase^initial_phase).count_ones() as usize;
   }
  }
 }}
 let mut square_cases=0;let mut square_negative_hits=0;
 for dirty in [false,true]{for inv in [false,true]{for _ in 0..4096{
  let mut iq:[u64;8]=std::array::from_fn(|_|next(&mut state));if !dirty{iq[5]=0;}
  let ib:[u64;5]=std::array::from_fn(|_|next(&mut state));let phase=next(&mut state);let mr=next(&mut state);let g=ib[0]&ib[1];let mut eq=iq;
  // Independent 3-bit integer signed +/- carry-in oracle per protected lane.
  for lane in 0..64{if g>>lane&1!=0{
   let a=(iq[1]>>lane)&1;let t=(iq[3]>>lane)&1;let u=(iq[4]>>lane)&1;let p=(iq[0]>>lane)&1;
   let x=a|(t<<1)|(u<<2);let y=if inv{x.wrapping_sub(p)&7}else{(x+p)&7};
   for(q,k)in [(1,0),(3,1),(4,2)]{eq[q]=(eq[q]&!(1u64<<lane))|(((y>>k)&1)<<lane);}
  }}
  let mut eb=ib;if !dirty{eb[2]=(ib[2]&!g)^(mr&g);}let mut rng=Words{word:mr,draws:0};let mut s=Simulator::new(8,5,&mut rng);
  s.qubits.copy_from_slice(&iq);s.bits.copy_from_slice(&ib);s.phase=phase;s.apply_iter(square(inv,false,dirty).iter());
  assert_eq!(s.qubits,eq);assert_eq!(s.bits,eb);assert_eq!(s.phase,phase);drop(s);assert_eq!(rng.draws,usize::from(!dirty));square_cases+=64;
  let mut rng=Words{word:mr,draws:0};let mut s=Simulator::new(8,5,&mut rng);s.qubits.copy_from_slice(&iq);s.bits.copy_from_slice(&ib);s.phase=phase;s.apply_iter(square(inv,true,dirty).iter());square_negative_hits+=if dirty{s.qubits.iter().zip(eq.iter()).map(|(a,b)|(a^b).count_ones()as usize).sum()}else{(s.phase^phase).count_ones()as usize};
 }}}
 assert!(negative_hits>0&&square_negative_hits>0);println!("{{\"protected_cases\":{cases},\"square_add_sub_protected_cases\":{square_cases},\"every_quantum_bit_classical_bit_phase_and_draw_count\":true,\"missing_CZ_negative_hits\":{negative_hits},\"square_missing_CZ_negative_hits\":{square_negative_hits},\"status\":\"PASS\"}}");
}
