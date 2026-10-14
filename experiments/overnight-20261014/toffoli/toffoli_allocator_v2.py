"""Versioned generic allocator-boundary normalization for bank research."""
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
AREA=ROOT/'research-output/overnight-20261014/toffoli'
SOURCE=AREA/'bank-product-source/src/point_add'
TARGET=AREA/'bank-product-v2-source/src/point_add'

def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for name in ['y15_onefold.rs','toffoli_bank_loan.rs','mod.rs']:
        shutil.copyfile(SOURCE/name,TARGET/name)
    p=TARGET/'toffoli_bank_loan.rs';s=p.read_text();start=s.index('#[cfg(test)]');end=s.index('const TRANSFORM')
    s=s[:start]+'''thread_local! {
    static MODE: std::cell::Cell<bool> = const {std::cell::Cell::new(false)};
    static HEAD_PLAN: std::cell::Cell<bool> = const {std::cell::Cell::new(false)};
}
pub(super) fn enabled()->bool {MODE.with(|x|x.get())}
pub(super) fn head_plan()->bool {HEAD_PLAN.with(|x|x.get())}
pub(super) fn with_mode<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=MODE.with(|x|x.replace(on));let result=f();MODE.with(|x|x.set(old));result
}
pub(super) fn with_head_plan<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=HEAD_PLAN.with(|x|x.replace(on));let result=f();HEAD_PLAN.with(|x|x.set(old));result
}
#[cfg(test)] thread_local! {static RECIPE:std::cell::Cell<bool>=const{std::cell::Cell::new(false)};}
#[cfg(test)] pub(super) fn recipe()->bool {RECIPE.with(|x|x.get())}
#[cfg(not(test))] pub(super) fn recipe()->bool {true}
#[cfg(test)] pub(super) fn with_recipe<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=RECIPE.with(|x|x.replace(on));let result=f();RECIPE.with(|x|x.set(old));result
}
#[cfg(test)] thread_local! {static BANK_SWITCH:std::cell::Cell<bool>=const{std::cell::Cell::new(true)};}
#[cfg(test)] pub(super) fn bank_switch()->bool {BANK_SWITCH.with(|x|x.get())}
#[cfg(not(test))] pub(super) fn bank_switch()->bool {true}
#[cfg(test)] pub(super) fn with_bank_switch<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=BANK_SWITCH.with(|x|x.replace(on));let result=f();BANK_SWITCH.with(|x|x.set(old));result
}
'''+s[end:];p.write_bytes(s.encode())
    builder=subprocess.check_output(['git','-C',str(ROOT/'agents/product'),'show','c5bb1ec8:src/point_add/builder.rs']).decode()
    at=builder.index('    /// Highest live-qubit count seen')
    method='''    /// Generic allocator replay: this fresh emitter has the same allocation
    /// inputs, but owns a separate operation vector and report. Its gates never
    /// enter the submitted circuit. The original body determines baseline pool
    /// ordering; the existing checked setter restores only allocator metadata.
    pub(crate) fn toffoli_allocator_fork(&self)->Self {
        let mut fork=Self::new();
        fork.next_qubit=self.next_qubit;fork.next_bit=self.next_bit;
        fork.next_register=self.next_register;fork.free_qubits=self.free_qubits.clone();
        fork.free_bits=self.free_bits.clone();fork.active_qubits=self.active_qubits;
        fork.phase=self.phase;fork.avoid_ids=self.avoid_ids.clone();fork.report=None;
        fork
    }
    pub(crate) fn toffoli_allocator_restore(&mut self,before:&(Vec<u32>,Vec<u32>,u32),after:&Self) {
        assert_eq!(self.next_qubit,after.next_qubit,"bank allocator fresh-wire boundary");
        assert_eq!(self.active_qubits,after.active_qubits,"bank allocator live-wire boundary");
        let wanted=after.y42_alloc_state();
        self.y42_alloc_set(before,&wanted.0,0,&wanted.1,wanted.2);
        assert_eq!(self.y42_alloc_state(),wanted,"bank allocator exact boundary ordering");
    }
'''
    builder=builder[:at]+method+builder[at:];TARGET.joinpath('builder.rs').write_bytes(builder.encode())
    pingpong=subprocess.check_output(['git','-C',str(ROOT/'agents/product'),'show','c5bb1ec8:src/point_add/pingpong.rs']).decode()
    pingpong+='''
// Snapshot every operational allocation context reachable by a payload body.
pub(crate) type ToffoliEmitterContext=(Option<(usize,QubitId)>,isize,usize,(isize,isize),Option<QubitId>,Option<usize>);
pub(crate) fn toffoli_emitter_context()->ToffoliEmitterContext {
    (Y15_CARRY_IN.with(|x|x.get()),Y17_EXTRA.with(|x|x.get()),REPLAY_SIGN_LOANS.with(|x|x.get()),
     HEO_CMP_SHIFT.with(|x|x.get()),HEO_TIE.with(|x|x.get()),PHASE_CAP.with(|x|x.get()))
}
pub(crate) fn toffoli_restore_emitter_context(s:ToffoliEmitterContext) {
    Y15_CARRY_IN.with(|x|x.set(s.0));Y17_EXTRA.with(|x|x.set(s.1));REPLAY_SIGN_LOANS.with(|x|x.set(s.2));
    HEO_CMP_SHIFT.with(|x|x.set(s.3));HEO_TIE.with(|x|x.set(s.4));PHASE_CAP.with(|x|x.set(s.5));
}
''';TARGET.joinpath('pingpong.rs').write_bytes(pingpong.encode())
    leapfrog=subprocess.check_output(['git','-C',str(ROOT/'agents/product'),'show','c5bb1ec8:src/point_add/leapfrog.rs']).decode()
    leapfrog+='''
// Operational compare contexts plus shared diagnostic counters/logs reached
// by the original payload emitter. Deferred tick0 phase storage is excluded:
// allocator replay runs only at t>0; the original Y26_T0=5 is preserved.
pub(crate) type ToffoliBodyContext=((usize,bool,bool),bool,usize,f64,[f64;3],f64,Vec<String>,(usize,usize));
pub(crate) fn toffoli_body_context()->ToffoliBodyContext {
    (C35_AT.with(|x|x.get()),C35_CMP_FX.with(|x|x.get()),C35_PADS.with(|x|x.get()),
     Y16_FOLD.with(|x|x.get()),Y16_ACC.with(|x|x.get()),Y16_NEST.with(|x|x.get()),
     Y17_LOG.with(|x|x.borrow().clone()),Y28_COUNT.with(|x|x.get()))
}
pub(crate) fn toffoli_restore_body_context(s:ToffoliBodyContext) {
    C35_AT.with(|x|x.set(s.0));C35_CMP_FX.with(|x|x.set(s.1));C35_PADS.with(|x|x.set(s.2));
    Y16_FOLD.with(|x|x.set(s.3));Y16_ACC.with(|x|x.set(s.4));Y16_NEST.with(|x|x.set(s.5));
    Y17_LOG.with(|x|*x.borrow_mut()=s.6);Y28_COUNT.with(|x|x.set(s.7));
}
''';TARGET.joinpath('leapfrog.rs').write_bytes(leapfrog.encode())
    p=TARGET/'y15_onefold.rs';s=p.read_text()
    old='    let ((), peak) = c.r3_peak(|c| body(c, t, s, k1, k2, b, tg, proxy, rev));'
    assert s.count(old)==1
    new='''    // Replay the original emitter from identical allocation inputs. Never
    // alter the historical y42 assertions or their recorded allocator tables.
    let baseline=if !rev && t>0 && toffoli_bank_loan::recipe() {
        assert!(!toffoli_bank_loan::enabled(),"bank body owns its mode");
        let before=c.y42_alloc_state();let mut fork=c.toffoli_allocator_fork();
        assert!(t>0,"allocator replay excludes deferred tick0 phase storage");
        let context=super::super::pingpong::toffoli_emitter_context();
        let body_context=super::toffoli_body_context();
        let payload=PAYLOAD_AT.with(|x|x.get());
        let loan=LOAN_ACTIVE.with(|x|x.get());
        body(&mut fork,t,s,k1,k2,b,tg,proxy,rev);
        super::super::pingpong::toffoli_restore_emitter_context(context);
        super::toffoli_restore_body_context(body_context);PAYLOAD_AT.with(|x|x.set(payload));
        LOAN_ACTIVE.with(|x|x.set(loan));
        Some((before,fork))
    } else {None};
    let on=baseline.is_some() && toffoli_bank_loan::bank_switch();
    let ((),peak)=c.r3_peak(|c|toffoli_bank_loan::with_mode(on,||toffoli_bank_loan::with_head_plan(on,||body(c,t,s,k1,k2,b,tg,proxy,rev))));
    if let Some((before,fork))=baseline {c.toffoli_allocator_restore(&before,&fork);}'''
    s=s.replace(old,new)
    s+='\n#[cfg(test)]\n#[path = "toffoli_allocator_tests_v2.rs"]\nmod toffoli_allocator_tests_v2;\n'
    p.write_bytes(s.encode())
    TARGET.joinpath('toffoli_allocator_tests_v2.rs').write_bytes(HERE.joinpath('toffoli_allocator_tests_v2.rs').read_bytes().replace(b'\r\n',b'\n'))
    print('prepared allocator v2 source',TARGET)

if __name__=='__main__':main()
