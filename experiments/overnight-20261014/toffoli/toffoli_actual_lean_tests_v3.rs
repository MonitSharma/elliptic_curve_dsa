//! Narrowed fin3 source-caller and all-input/all-MR native phase fixtures.
use super::*;
use crate::circuit::{analyze_ops,Op,OperationType};
use crate::sim::Simulator;
use sha3::digest::XofReader;
type Layout=(Vec<Op>,Vec<QubitId>,Vec<QubitId>,Vec<QubitId>,Vec<QubitId>,usize,u32,usize);
fn mode<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=TOFFOLI_ACTUAL_LEAN_MODE.with(|x|x.replace(on));let at=PAYLOAD_AT.with(|x|x.replace(Some((false,128))));
    TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.set(0));let result=f();TOFFOLI_ACTUAL_LEAN_MODE.with(|x|x.set(old));PAYLOAD_AT.with(|x|x.set(at));result
}
fn fixture(room:usize,on:bool)->Layout {
    let mut c=Builder::new();let acc=c.alloc_qubits(56);let controls=c.alloc_qubits(8);
    let abi_bits:Vec<_>=(0..512).map(|_|c.alloc_bit()).collect();let abi=c.alloc_qubits(512);
    let pads=c.alloc_qubits(cells::cap()-(56+8+512+31+room));let active=c.active_qubits();
    for (&bit,&q) in abi_bits.iter().zip(&abi) {c.push_condition(bit);c.x(q);c.pop_condition();}
    let (_,peak)=mode(on,||c.r3_peak(|c|fold_fwd_v2(c,&acc,[controls[0],controls[1],controls[2]],[controls[3],controls[4],controls[5]],controls[6],controls[7],3,None,true,0)));
    let hits=TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.get());assert_eq!(hits,usize::from(on));assert_eq!(c.active_qubits(),active);assert!(peak as usize<=cells::cap());
    for (&bit,&q) in abi_bits.iter().zip(&abi) {c.push_condition(bit);c.x(q);c.pop_condition();}
    let c6=TOFFOLI_ACTUAL_LEAN_C6.with(|x|x.get()).unwrap();let ops=c.take_ops();let mut mr=0usize;let mut c6_mr=None;
    for op in &ops {if matches!(op.kind,OperationType::Hmr|OperationType::R) {if op.q_target==c6 && c6_mr.is_none() {c6_mr=Some(mr);}mr+=1;}}
    (ops,acc,controls,abi,pads,c6_mr.unwrap(),peak,hits)
}
fn expected(acc:u64,e:u64,nm:u64,k1:u64,k2:u64)->u64 {
    let c3=u64::from((acc&7)+e>=8);let c4=(acc>>3&1)&c3;let r=nm+(acc&7);
    let a4=r&1;let a5=(r^(r>>1))&1;let a=acc>>4&1;let z=acc>>5&1;
    let c5=(a&a4)|(a&c4)|(a4&c4);let y3=(k1|k2)&((acc>>3&1)^c3);
    let y4=k2&(a^c4^a4);let y5=(k1&k2)&(z^c5^a5);
    let k=r as i128+8*(y3 as i128+2*y4 as i128+4*y5 as i128-c3 as i128);
    ((acc as i128+e as i128-((1i128<<32)+976)*k)&((1i128<<56)-1)) as u64
}
struct Words {seed:u64,index:usize,c6:usize,c6_word:u64}
impl XofReader for Words {fn read(&mut self,out:&mut[u8]) {
    assert_eq!(out.len(),8);self.seed^=self.seed<<13;self.seed^=self.seed>>7;self.seed^=self.seed<<17;
    let word=if self.index==self.c6 {self.c6_word}else{self.seed};self.index+=1;out.copy_from_slice(&word.to_le_bytes());
}}
#[test]
fn toffoli_actual_lean_all_inputs_all_MR_v3() {
    let mut total=0usize;let mut max_phase=0usize;let mut max_quantum=0usize;
    for room in [4,5] {
        let mut costs=Vec::new();
        for on in [false,true] {
            let (ops,acc,controls,abi,pads,c6_mr,peak,hits)=fixture(room,on);let (nq,nb,emitted,_)=analyze_ops(ops.iter());
            let mut executed=0u64;let mut cases=0usize;
            let mask=((1u64<<56)-1)&!63;
            for high in [0,mask,0xAAAA_AAAA_AAAA_AAAA&mask,((1u64<<32)-1)&mask] {
                for base in (0..1usize<<14).step_by(64) {
                    let mut input=vec![0u64;nq as usize];let mut want=vec![0u64;nq as usize];let bits:Vec<_>=(0..512).map(|i|0x93AB_CDEF_6789_4521u64.rotate_left((i%64) as u32)).collect();
                    for shot in 0..64 {
                        let raw=(base+shot) as u64;let value=(raw&63)|high;let output=expected(value,raw>>6&7,raw>>9&7,raw>>12&1,raw>>13&1);
                        for (i,&q) in acc.iter().enumerate() {input[q.0 as usize]|=(value>>i&1)<<shot;want[q.0 as usize]|=(output>>i&1)<<shot;}
                        for (i,&q) in controls.iter().enumerate() {let bit=(raw>>(i+6)&1)<<shot;input[q.0 as usize]|=bit;want[q.0 as usize]|=bit;}
                    }
                    for &q in abi.iter().chain(pads.iter()) {input[q.0 as usize]=0xA55A_F00F_1234_5678u64.rotate_left((q.0%64) as u32);want[q.0 as usize]=input[q.0 as usize];}
                    let audit=super::toffoli_actual_lean_phase_kernel_v3::audit(&ops,&input,&bits).unwrap_or_else(|why|panic!("ALLMR room={room} new={on} base={base} high={high:#x}: {why}"));
                    assert_eq!(audit.qubits,want,"ALLMR everyphysicalqubit");max_phase=max_phase.max(audit.maximum_phase_terms);max_quantum=max_quantum.max(audit.maximum_quantum_terms);total+=64;
                    for c6_word in [0,u64::MAX,0xAAAA_AAAA_AAAA_AAAA] {
                        let mut words=Words{seed:0xDEAD_F00D_9324_6781,index:0,c6:c6_mr,c6_word};let mut sim=Simulator::new(nq as usize,nb as usize,&mut words);
                        sim.qubits.copy_from_slice(&input);sim.bits[..512].copy_from_slice(&bits);sim.phase=0x9A55_0FF0_8934_4567;
                        sim.apply_iter(ops.iter());assert_eq!(sim.qubits,want,"native everyphysicalqubit");assert_eq!(sim.phase,0x9A55_0FF0_8934_4567,"native incomingphase");
                        assert_eq!(&sim.bits[..512],&bits);executed+=sim.stats.toffoli_gates;cases+=64;
                    }
                }
            }
            costs.push((emitted,executed,cases));eprintln!("TOFFOLI_ACTUAL_LEAN_COMPONENT room={room} new={on} emitted={emitted} executed={executed} cases={cases} peak={peak} hits={hits} c6_mr={c6_mr}");
        }
        assert_eq!(costs[0].0,costs[1].0+1);assert_eq!(costs[0].1,costs[1].1+(costs[0].2/2) as u64);
    }
    eprintln!("TOFFOLI_ACTUAL_LEAN_ALLMR exact_input_cases={total} native_cases={} max_phase_terms={max_phase} max_quantum_terms={max_quantum} higher_words=4 rooms=2 classicalABI=512",total*3);
}
#[test]
fn toffoli_actual_lean_source_caller_v3() {
    crate::point_add::pingpong::with_phase_cap(Some(1234),|| {
        for on in [false,true] {
            let mut c=Builder::new();let b=c.alloc_qubits(N);let tg=c.alloc_qubits(N);let letters=c.alloc_qubits(5);let _pads=c.alloc_qubits(1234-(2*N+5+40));
            let active=c.active_qubits();let tick=128;let (_,proxy)=proxy_fold(steps()[tick][0],false);let shift=cmp_shift_at(tick);
            let (_,peak)=mode(on,||c.r3_peak(|c|cells::with_tie(None,||cells::with_cmp_shift((shift.0+Y15_CMP_EXTRA+super::n2_cmpx(),shift.1),||cells::with_bridge(proxy,false,||body_capped(c,tick,[letters[0],letters[1],letters[2]],letters[3],letters[4],&b,&tg,proxy,false))))));
            let hits=TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.get());assert_eq!(hits,usize::from(on));assert_eq!(c.active_qubits(),active);assert!(peak<=1234);
            let ops=c.take_ops();let (_,_,emitted,_)=analyze_ops(ops.iter());eprintln!("TOFFOLI_ACTUAL_LEAN_CALLER cap=1234 room=40 tick=128 new={on} hits={hits} peak={peak} emitted={emitted} source_caller_resource_only=true");
        }
    });
}
#[test]
fn toffoli_actual_lean_phase_fault_v3() {
    let (mut ops,acc,controls,_,_,_,_,_)=fixture(4,true);
    let ccx=ops.iter().rposition(|op|op.kind==OperationType::CCX).unwrap();let cz=ops.iter().enumerate().skip(ccx+1).find(|(_,op)|op.kind==OperationType::CZ).unwrap().0;ops.remove(cz);
    let (nq,_,_,_)=analyze_ops(ops.iter());let mut detected=false;
    for base in (0..1usize<<14).step_by(64) {let mut input=vec![0u64;nq as usize];
        for shot in 0..64 {let raw=(base+shot) as u64;
            for (i,&q) in acc.iter().take(6).enumerate() {input[q.0 as usize]|=(raw>>i&1)<<shot;}
            for (i,&q) in controls.iter().enumerate() {input[q.0 as usize]|=(raw>>(i+6)&1)<<shot;}
        }
        if let Err(why)=super::toffoli_actual_lean_phase_kernel_v3::audit(&ops,&input,&[]) {if why.starts_with("nonzero phase polynomial") {detected=true;break;}}
    }
    assert!(detected,"phase fault must be detected, not inconclusive");
}
