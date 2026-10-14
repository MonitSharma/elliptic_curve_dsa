//! Complete-cost paired native tests for the six-wire bank loan.
use super::*;
use crate::circuit::{analyze_ops,OperationType};
use crate::sim::Simulator;
use sha3::digest::XofReader;

struct Words {seed:u64,first_only:bool,index:usize}
impl XofReader for Words {
    fn read(&mut self,out:&mut [u8]) {
        assert_eq!(out.len(),8);
        let value=if self.first_only {if self.index==0 {u64::MAX}else{0}} else {
            self.seed^=self.seed<<13;self.seed^=self.seed>>7;self.seed^=self.seed<<17;self.seed
        };
        out.copy_from_slice(&value.to_le_bytes());self.index+=1;
    }
}

fn fixture(room:usize,on:bool,fault:bool)->(u64,u64,u32,usize) {
    let mw=56usize;
    let mut c=Builder::new();
    let acc=c.alloc_qubits(mw);
    let e:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
    let nm:[QubitId;3]=c.alloc_qubits(3).try_into().unwrap();
    let shift:[QubitId;2]=c.alloc_qubits(2).try_into().unwrap();
    let pads=c.alloc_qubits(cells::cap()-(mw+8+31+room));
    let active=c.active_qubits();
    let (_,peak)=c.r3_peak(|c|toffoli_bank_loan::with_mode(on,||fold_fwd_v2(c,&acc,e,nm,shift[0],shift[1],0,None,false,0)));
    assert_eq!(c.active_qubits(),active);
    assert!(peak as usize<=cells::cap());
    let mut ops=c.take_ops();
    if fault {
        let index=ops.iter().position(|o|o.kind==OperationType::CZ).unwrap();
        ops.remove(index);
    }
    let emitted=ops.iter().filter(|o|matches!(o.kind,OperationType::CCX|OperationType::CCZ)).count() as u64;
    let (nq,nb,_,_)=analyze_ops(ops.iter());
    let mut words=Words {seed:0xDEAD_C0DE_7654_3210,first_only:fault,index:0};
    let mut sim=Simulator::new(nq as usize,nb as usize,&mut words);
    let mut shots=0;
    let mut phase_bad=0;
    let high_mask=((1u64<<mw)-1)&!63;
    for high in [0,high_mask,0xAAAA_AAAA_AAAA_AAAA&high_mask] {
        for base in (0..1usize<<14).step_by(64) {
            sim.clear_for_shot();sim.xof.index=0;
            for shot in 0..64 {
                let raw=(base+shot) as u64;let value=(raw&63)|high;
                for (i,&q) in acc.iter().enumerate() {*sim.qubit_mut(q)|=(value>>i&1)<<shot;}
                for (i,&q) in e.iter().chain(nm.iter()).chain(shift.iter()).enumerate() {*sim.qubit_mut(q)|=(raw>>(i+6)&1)<<shot;}
            }
            for &q in &pads {*sim.qubit_mut(q)=0xA55A_F00F_1234_5678;}
            sim.apply_iter(ops.iter());
            phase_bad+=sim.phase.count_ones();
            for shot in 0..64 {
                let raw=(base+shot) as u64;
                let want=super::toffoli_native_fold::expected((raw&63)|high,raw>>6&7,raw>>9&7,raw>>12&1,raw>>13&1,mw);
                let got=acc.iter().enumerate().fold(0u64,|v,(i,&q)|v|((sim.qubit(q)>>shot&1)<<i));
                assert_eq!(got,want,"room={room} bank={on} raw={raw} high={high:#x}");
                for (i,&q) in e.iter().chain(nm.iter()).chain(shift.iter()).enumerate() {assert_eq!(sim.qubit(q)>>shot&1,raw>>(i+6)&1);}
            }
            for &q in &pads {assert_eq!(sim.qubit(q),0xA55A_F00F_1234_5678);}
            for &q in acc.iter().chain(e.iter()).chain(nm.iter()).chain(shift.iter()).chain(pads.iter()) {*sim.qubit_mut(q)=0;}
            assert!(sim.qubits.iter().all(|&v|v==0),"scratch dirty room={room} bank={on}");
            shots+=64;
        }
    }
    if fault {assert!(phase_bad>0,"bank-phase fault must be detected");}
    else {assert_eq!(phase_bad,0,"phase dirty room={room} bank={on}");}
    (emitted,sim.stats.toffoli_gates,peak,shots)
}

#[test]
fn toffoli_bank_roomy_phase_coefficients() {
    assert!(toffoli_bank_loan::with_mode(true,||super::toffoli_native_fold::run_native(56,0,true,false)));
}

#[test]
fn toffoli_bank_complete_cost_rooms() {
    for room in [10,12,14,16,18,22,26,31,36,45,50] {
        let base=fixture(room,false,false);
        let bank=fixture(room,true,false);
        eprintln!("TOFFOLI_BANK_COMPONENT room={room} shots={} old_emitted={} new_emitted={} old_executed={} new_executed={} old_peak={} new_peak={}",
                  base.3,base.0,bank.0,base.1,bank.1,base.2,bank.2);
    }
}

#[test]
fn toffoli_bank_early_phase_fault() {
    fixture(50,true,true);
}
