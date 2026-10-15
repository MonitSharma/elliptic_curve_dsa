// Compact interpreter retaining exact value, phase, garbage and all RNG draws.
// Stats are intentionally omitted: final selected nonces use protected run_tests.
#[derive(Clone,Copy)]
#[repr(C)]
struct CompactOp { a:u16,b:u16,t:u16,c:u16,bt:u16,k:u8 }
struct Compact { ops:Vec<CompactOp>, rng_count:usize }
impl Compact {
 fn compile(ops:&[Op])->Self {
  let small=|x:u64|->u16{if x==u64::MAX {u16::MAX}else{x.try_into().expect("compact operand exceeds16bits")}};
  let mut rng_count=0;
  let ops=ops.iter().filter_map(|o| {
   use OperationType::*;
   if matches!(o.kind,Register|AppendToRegister|DebugPrint) {return None;}
   if matches!(o.kind,R|Hmr) {rng_count+=1;}
   Some(CompactOp {a:small(o.q_control1.0),b:small(o.q_control2.0),t:small(o.q_target.0),c:small(o.c_condition.0),bt:small(o.c_target.0),k:o.kind as u8})
  }).collect::<Vec<_>>();
  eprintln!("COMPACT ops={} bytes={} rng_words={rng_count}",ops.len(),ops.len()*std::mem::size_of::<CompactOp>());
  Self{ops,rng_count}
 }
}
struct FastSimulator<'a> {phase:u64,qubits:Vec<u64>,bits:Vec<u64>,xof:&'a mut sha3::Shake256Reader,words:Vec<u8>}
impl<'a> FastSimulator<'a> {
 fn new(nq:usize,nb:usize,xof:&'a mut sha3::Shake256Reader)->Self{Self{phase:0,qubits:vec![0;nq],bits:vec![0;nb],xof,words:Vec::new()}}
 fn clear_for_shot(&mut self){self.phase=0;self.qubits.fill(0);self.bits.fill(0);}
 fn qubit(&self,q:QubitId)->u64{self.qubits[q.0 as usize]}
 fn qubit_mut(&mut self,q:QubitId)->&mut u64{&mut self.qubits[q.0 as usize]}
 fn set_register(&mut self,r:&[QubitOrBit],v:U256,lane:usize){for(i,x)in r.iter().enumerate(){let p=match x{QubitOrBit::Qubit(q)=>&mut self.qubits[q.0 as usize],QubitOrBit::Bit(b)=>&mut self.bits[b.0 as usize]};*p=(*p&!(1<<lane))|((v.bit(i)as u64)<<lane);}}
 fn get_register(&self,r:&[QubitOrBit],lane:usize)->U256{let mut v=U256::ZERO;for(i,x)in r.iter().enumerate(){let p=match x{QubitOrBit::Qubit(q)=>self.qubits[q.0 as usize],QubitOrBit::Bit(b)=>self.bits[b.0 as usize]};if(p>>lane)&1!=0{v|=U256::from(1)<<i;}}v}
 fn apply(&mut self,p:&Compact){
  self.words.resize(p.rng_count*8,0);XofReader::read(self.xof,&mut self.words);let mut ri=0;let mut stack=Vec::new();let mut base=u64::MAX;
  for o in &p.ops {
   let c=base&if o.c==u16::MAX{u64::MAX}else{self.bits[o.c as usize]};let t=o.t as usize;let a=o.a as usize;let b=o.b as usize;let bt=o.bt as usize;
   match o.k {
    0=>self.phase^=c,
    3=>self.bits[bt]^=c,4=>self.bits[bt]&=!c,5=>self.bits[bt]|=c,
    6=>self.qubits[t]^=c,7=>self.phase^=c&self.qubits[t],
    8=>self.qubits[t]^=c&self.qubits[a],9=>self.phase^=c&self.qubits[a]&self.qubits[t],
    10=>{let d=c&(self.qubits[t]^self.qubits[a]);self.qubits[t]^=d;self.qubits[a]^=d;},
    11|12=>{let w=u64::from_le_bytes(self.words[ri..ri+8].try_into().unwrap());ri+=8;self.phase^=self.qubits[t]&w&c;self.qubits[t]&=!c;if o.k==12{self.bits[bt]=(self.bits[bt]&!c)^(w&c);}},
    13=>self.qubits[t]^=c&self.qubits[a]&self.qubits[b],14=>self.phase^=c&self.qubits[t]&self.qubits[a]&self.qubits[b],
    15=>{stack.push(base);base&=self.bits[o.c as usize];},16=>base=stack.pop().expect("condition stack underflow"),_=>unreachable!()
   }
  }
  assert_eq!(ri,p.rng_count*8);assert!(stack.is_empty());
 }
}
