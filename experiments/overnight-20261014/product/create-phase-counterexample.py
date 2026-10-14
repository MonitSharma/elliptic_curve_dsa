"""Demonstrate why parity-span phase rewrites need a separate phase premise."""
from pathlib import Path
import sys
base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve();dest.joinpath('src').mkdir(parents=True,exist_ok=True)
source=f'''use quantum_ecc::{{circuit,sim}};
#[allow(dead_code)] #[path="{(base/'src/point_add/pscan.rs').as_posix()}"] mod pscan;
'''+r'''
use circuit::{Op,OperationType as K,QubitId,BitId,RegisterId};
struct Fixed;impl sha3::digest::XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(255);}}
fn main(){
 std::env::set_var("SL_PSCAN_FIX","1");
 let mut ops=Vec::new();for q in 0..3{let mut o=Op::empty();o.kind=K::AppendToRegister;o.q_target=QubitId(q);o.r_target=RegisterId(0);ops.push(o);}
 let mut reg=Op::empty();reg.kind=K::Register;reg.r_target=RegisterId(0);ops.push(reg);
 let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(3);h.c_target=BitId(0);ops.push(h);
 let mut push=Op::empty();push.kind=K::PushCondition;push.c_condition=BitId(0);ops.push(push);
 let mut phase=Op::empty();phase.kind=K::CCZ;phase.q_control1=QubitId(0);phase.q_control2=QubitId(1);phase.q_target=QubitId(2);ops.push(phase);
 let mut pop=Op::empty();pop.kind=K::PopCondition;ops.push(pop);
 let mut clear=Op::empty();clear.kind=K::BitStore0;clear.c_target=BitId(0);ops.push(clear);
 for o in &ops{o.validate();}
 let revised=pscan::run(ops.clone());assert_eq!(revised.len()+3,ops.len(),"the existing pass must actually erase the phase block");
 let mut different=0;for input in 0..8{let mut ra=Fixed;let mut rb=Fixed;let mut a=sim::Simulator::new(4,1,&mut ra);let mut b=sim::Simulator::new(4,1,&mut rb);
  for q in 0..3{a.qubits[q]=(input>>q)&1;}b.qubits.clone_from(&a.qubits);
  a.apply_iter(ops.iter());b.apply_iter(revised.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);
  if a.phase!=b.phase{different+=1;println!("PHASE_COUNTEREXAMPLE input={input} original_phase={:#x} rewritten_phase={:#x} original_ops={} rewritten_ops={} score=NONE",a.phase,b.phase,ops.len(),revised.len());}
 }
 assert_eq!(different,1,"the all-one basis input must expose the missing phase premise");
}
'''
dest.joinpath('src/main.rs').write_text(source,newline='\n')
dest.joinpath('Cargo.toml').write_text(f'''[package]
name="product_phase_counterexample"
version="0.1.0"
edition="2021"
[dependencies]
quantum_ecc={{path="{base.as_posix()}"}}
sha3="0.10"
[profile.release]
opt-level=3
''',newline='\n')
