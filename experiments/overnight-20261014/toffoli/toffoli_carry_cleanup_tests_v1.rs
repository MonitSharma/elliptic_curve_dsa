//! Native exact low-domain phase coefficients and complete-cost paired folds.
use super::*;
use crate::circuit::{analyze_ops,OperationType};
use crate::sim::Simulator;
use sha3::digest::XofReader;
struct Words(u64);
impl XofReader for Words {fn read(&mut self,out:&mut[u8]) {assert_eq!(out.len(),8);self.0^=self.0<<13;self.0^=self.0>>7;self.0^=self.0<<17;out.copy_from_slice(&self.0.to_le_bytes());}}
fn with_mode<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.replace(on));
    let at=PAYLOAD_AT.with(|x|x.replace(Some((false,128))));
    TOFFOLI_CARRY_CLEANUP_HITS.with(|x|x.set(0));let result=f();
    TOFFOLI_CARRY_CLEANUP_MODE.with(|x|x.set(old));PAYLOAD_AT.with(|x|x.set(at));result
}
#[test]
fn toffoli_carry_cleanup_all_inputs_all_phase_coefficients_v1() {
    for on in [false,true] {
        assert!(with_mode(on,||super::toffoli_native_fold::run_native(56,0,true,false)));
        let hits=TOFFOLI_CARRY_CLEANUP_HITS.with(|x|x.get());assert_eq!(hits,usize::from(on));
        eprintln!("TOFFOLI_CARRY_NATIVE_PHASE new={on} hits={hits} all16384_low_inputs=true upper_words=38 all_measurement_coefficients=true");
    }
}
#[test]
fn toffoli_carry_cleanup_phase_fault_detected_v1() {
    assert!(!with_mode(true,||super::toffoli_native_fold::run_native(56,0,true,true)));
}
fn fixture(room:usize,on:bool)->(u64,u64,u32,usize,usize) {
    let mw=56usize;let mut c=Builder::new();let acc=c.alloc_qubits(mw);
    let e:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();let nm:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
    let shift:[QubitId;2]=c.alloc_qubits(2).try_into().unwrap();
    let pads=c.alloc_qubits(cells::cap()-(mw+8+30+room));let active=c.active_qubits();
    let (_,peak)=with_mode(on,||c.r3_peak(|c|fold_fwd_v2(c,&acc,e,nm,shift[0],shift[1],0,None,false,0)));
    let hits=TOFFOLI_CARRY_CLEANUP_HITS.with(|x|x.get());assert_eq!(c.active_qubits(),active);
    let ops=c.take_ops();let emitted=ops.iter().filter(|op|matches!(op.kind,OperationType::CCX|OperationType::CCZ)).count() as u64;
    let (nq,nb,_,_)=analyze_ops(ops.iter());let mut words=Words(0x93AB_CDEF_6789_4521);let mut sim=Simulator::new(nq as usize,nb as usize,&mut words);
    let highmask=((1u64<<mw)-1)&!63;let mut shots=0;
    for high in [0,highmask,0xAAAA_AAAA_AAAA_AAAA&highmask] {
        for base in (0..1usize<<14).step_by(64) {
            sim.clear_for_shot();
            for shot in 0..64 {
                let raw=(base+shot) as u64;let value=(raw&63)|high;
                for (i,&q) in acc.iter().enumerate() {*sim.qubit_mut(q)|=(value>>i&1)<<shot;}
                for (i,&q) in e.iter().chain(nm.iter()).chain(shift.iter()).enumerate() {*sim.qubit_mut(q)|=(raw>>(i+6)&1)<<shot;}
            }
            for &q in &pads {*sim.qubit_mut(q)=0xA55A_F00F_1234_5678;}
            sim.apply_iter(ops.iter());assert_eq!(sim.phase,0,"phase room={room} new={on}");
            for shot in 0..64 {
                let raw=(base+shot) as u64;let want=super::toffoli_native_fold::expected((raw&63)|high,raw>>6&7,raw>>9&7,raw>>12&1,raw>>13&1,mw);
                let got=acc.iter().enumerate().fold(0u64,|value,(i,&q)|value|((sim.qubit(q)>>shot&1)<<i));assert_eq!(got,want,"value room={room} new={on} raw={raw}");
                for (i,&q) in e.iter().chain(nm.iter()).chain(shift.iter()).enumerate() {assert_eq!(sim.qubit(q)>>shot&1,raw>>(i+6)&1);}
            }
            for &q in &pads {assert_eq!(sim.qubit(q),0xA55A_F00F_1234_5678);}
            for &q in acc.iter().chain(e.iter()).chain(nm.iter()).chain(shift.iter()).chain(pads.iter()) {*sim.qubit_mut(q)=0;}
            assert!(sim.qubits.iter().all(|&value|value==0),"dirty scratch room={room} new={on}");shots+=64;
        }
    }
    (emitted,sim.stats.toffoli_gates,peak,shots,hits)
}
#[test]
fn toffoli_carry_cleanup_complete_cost_v1() {
    for room in [12,14,18,26,36,45,50] {
        let old=fixture(room,false);let new=fixture(room,true);assert_eq!(new.4,1);
        assert_eq!(old.0,new.0+1);assert_eq!(old.1,new.1+old.3 as u64);
        eprintln!("TOFFOLI_CARRY_COMPONENT room={room} shots={} old_emitted={} new_emitted={} old_executed={} new_executed={} old_peak={} new_peak={} hits={}",old.3,old.0,new.0,old.1,new.1,old.2,new.2,new.4);
    }
}
