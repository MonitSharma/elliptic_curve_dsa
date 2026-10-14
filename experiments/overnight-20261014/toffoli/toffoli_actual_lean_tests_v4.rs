//! Producer-aware top1/direct/nondeep fin4/drop2 fixture.
use super::*;
use crate::circuit::{analyze_ops,Op,OperationType};
use crate::sim::Simulator;
use sha3::digest::XofReader;
type Layout=(Vec<Op>,Vec<QubitId>,Vec<QubitId>,Vec<QubitId>,Vec<QubitId>,[QubitId;3],usize,u32);
fn mode<R>(on:bool,f:impl FnOnce()->R)->R {
    let old=TOFFOLI_ACTUAL_LEAN_MODE.with(|x|x.replace(on));let at=PAYLOAD_AT.with(|x|x.replace(Some((false,130))));
    TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.set(0));let result=f();TOFFOLI_ACTUAL_LEAN_MODE.with(|x|x.set(old));PAYLOAD_AT.with(|x|x.set(at));result
}
fn fixture(on:bool)->Layout {
    let mut c=Builder::new();let acc=c.alloc_qubits(56);let controls=c.alloc_qubits(12);
    let abi_bits:Vec<_>=(0..512).map(|_|c.alloc_bit()).collect();let abi=c.alloc_qubits(512);
    let cq2=m_carry(&mut c,controls[2],&l(controls[5]),controls[6]);
    let cq1=m_carry(&mut c,controls[0],&l(controls[4]),cq2);
    let x258=m_carry(&mut c,controls[1],&l(controls[3]),cq1);
    c.cx(controls[4],controls[0]);c.cx(cq2,controls[0]);c.cx(controls[3],controls[1]);c.cx(cq1,controls[1]);
    let mut esh=ESh{x256:controls[0],x257:controls[1],x258,h1:controls[6],m0:controls[6],m1:controls[6],cq1,cq2,cq3:controls[6],t255:controls[2],b1:controls[3],b2:controls[4],b3:controls[5],s:[controls[7],controls[8],controls[9]],direct:true,top1:true,deep_c:vec![],deep_a:vec![],deep_b:vec![]};
    // The three ESh targets are additional to the raw independent-input budget.
    let pads=c.alloc_qubits(cells::cap()-(56+12+512+31+2));let active=c.active_qubits();
    for (&bit,&q) in abi_bits.iter().zip(&abi) {c.push_condition(bit);c.x(q);c.pop_condition();}
    let (_,peak)=mode(on,||c.r3_peak(|c|fold_fwd_v2(c,&acc,[controls[0],controls[1],x258],[controls[7],controls[8],controls[9]],controls[10],controls[11],4,Some(&mut esh),true,2)));
    assert_eq!(TOFFOLI_ACTUAL_LEAN_DROPS.with(|x|x.get()),2,"two actually dropped chunks");
    assert_eq!(TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.get()),usize::from(on));assert_eq!(c.active_qubits(),active);assert!(peak as usize<=cells::cap());
    for (&bit,&q) in abi_bits.iter().zip(&abi) {c.push_condition(bit);c.x(q);c.pop_condition();}
    let c6=TOFFOLI_ACTUAL_LEAN_C6.with(|x|x.get()).unwrap();let boundary=TOFFOLI_ACTUAL_LEAN_BOUNDARY.with(|x|x.get());
    let final_esh=[esh.cq2,esh.cq1,esh.x258];let ops=c.take_ops();let mut mr=0usize;let mut c6_mr=None;
    for (i,op) in ops.iter().enumerate() {if matches!(op.kind,OperationType::Hmr|OperationType::R) {if i>=boundary && op.q_target==c6 && c6_mr.is_none() {c6_mr=Some(mr);}mr+=1;}}
    (ops,acc,controls,abi,pads,final_esh,c6_mr.unwrap(),peak)
}
fn maj(a:u64,b:u64,c:u64)->u64 {(a&b)^(a&c)^(b&c)}
fn producer(raw:u64)->[u64;5] {
    let x0=raw&1;let x1=raw>>1&1;let t=raw>>2&1;let b1=raw>>3&1;let b2=raw>>4&1;let b3=raw>>5&1;let c3=raw>>6&1;
    let c2=maj(t,b3,c3);let c1=maj(x0,b2,c2);let e2=maj(x1,b1,c1);
    [x0^b2^c2,x1^b1^c1,e2,c1,c2]
}
fn expected(acc:u64,e:u64,nm:u64,k1:u64,k2:u64)->u64 {
    let c3=u64::from((acc&7)+e>=8);let c4=(acc>>3&1)&c3;let r=nm+(acc&7);
    let a4=r&1;let a5=(r^(r>>1))&1;let a=acc>>4&1;let z=acc>>5&1;
    let c5=maj(a,a4,c4);let y3=(k1|k2)&((acc>>3&1)^c3);let y4=k2&(a^c4^a4);let y5=(k1&k2)&(z^c5^a5);
    let k=r as i128+8*(y3 as i128+2*y4 as i128+4*y5 as i128-c3 as i128);
    ((acc as i128+e as i128-((1i128<<32)+976)*k)&((1i128<<56)-1)) as u64
}
struct Words {seed:u64,index:usize,c6:usize,c6_word:u64}
impl XofReader for Words {fn read(&mut self,out:&mut[u8]) {
    assert_eq!(out.len(),8);self.seed^=self.seed<<13;self.seed^=self.seed>>7;self.seed^=self.seed<<17;
    let word=if self.index==self.c6 {self.c6_word}else{self.seed};self.index+=1;out.copy_from_slice(&word.to_le_bytes());
}}
fn inputs(nq:usize,base:usize,high:u64,acc:&[QubitId],controls:&[QubitId],abi:&[QubitId],pads:&[QubitId],esh:[QubitId;3])->(Vec<u64>,Vec<u64>) {
    let mut input=vec![0u64;nq];let mut want=vec![0u64;nq];
    for shot in 0..64 {
        let raw=(base+shot) as u64;let value=(raw&63)|high;let p=producer(raw>>6&127);let e=p[0]|p[1]<<1|p[2]<<2;
        let output=expected(value,e,raw>>13&7,raw>>16&1,raw>>17&1);
        for (i,&q) in acc.iter().enumerate() {input[q.0 as usize]|=(value>>i&1)<<shot;want[q.0 as usize]|=(output>>i&1)<<shot;}
        for (i,&q) in controls.iter().enumerate() {let bit=(raw>>(i+6)&1)<<shot;input[q.0 as usize]|=bit;want[q.0 as usize]|=(if i<2 {p[i]} else {raw>>(i+6)&1})<<shot;}
        for (&q,value) in esh.iter().zip([p[4],p[3],p[2]]) {want[q.0 as usize]|=value<<shot;}
    }
    for &q in abi.iter().chain(pads.iter()) {input[q.0 as usize]=0xA55A_F00F_1234_5678u64.rotate_left((q.0%64) as u32);want[q.0 as usize]=input[q.0 as usize];}
    (input,want)
}
#[test]
fn toffoli_actual_lean_all_producers_allmr_v4() {
    let mut costs=Vec::new();let mut total=0usize;let mut max_phase=0usize;
    for on in [false,true] {
        let (ops,acc,controls,abi,pads,esh,c6_mr,peak)=fixture(on);let (nq,nb,_,_)=analyze_ops(ops.iter());
        let emitted=ops.iter().filter(|op|op.kind==OperationType::CCX).count();let mut executed=0u64;let mut cases=0usize;
        let mask=((1u64<<56)-1)&!63;let bits:Vec<_>=(0..512).map(|i|0x93AB_CDEF_6789_4521u64.rotate_left((i%64) as u32)).collect();
        for high in [0,mask,0xAAAA_AAAA_AAAA_AAAA&mask,((1u64<<32)-1)&mask] {
            for base in (0..1usize<<18).step_by(64) {
                let (input,want)=inputs(nq as usize,base,high,&acc,&controls,&abi,&pads,esh);
                let audit=super::toffoli_actual_lean_phase_kernel_v4::audit(&ops,&input,&bits).unwrap_or_else(|why|panic!("ALLMR fin4 new={on} base={base} high={high:#x}: {why}"));
                assert_eq!(audit.qubits,want,"ALLMR everyphysicalqubit includingfreshESH");max_phase=max_phase.max(audit.maximum_phase_terms);total+=64;
                for c6_word in [0,u64::MAX,0xAAAA_AAAA_AAAA_AAAA] {
                    let mut words=Words{seed:0xDEAD_F00D_9324_6781,index:0,c6:c6_mr,c6_word};let mut sim=Simulator::new(nq as usize,nb as usize,&mut words);
                    sim.qubits.copy_from_slice(&input);sim.bits[..512].copy_from_slice(&bits);sim.phase=0x9A55_0FF0_8934_4567;
                    sim.apply_iter(ops.iter());assert_eq!(sim.qubits,want);assert_eq!(sim.phase,0x9A55_0FF0_8934_4567);assert_eq!(&sim.bits[..512],&bits);
                    executed+=sim.stats.toffoli_gates;cases+=64;
                }
            }
        }
        costs.push((emitted,executed,cases));eprintln!("TOFFOLI_ACTUAL_LEAN_V4 new={on} emitted={emitted} executed={executed} cases={cases} peak={peak} c6_mr={c6_mr} actualdrops=2 freshESH={esh:?}");
    }
    assert_eq!(costs[0].0,costs[1].0+1);assert_eq!(costs[0].1,costs[1].1+(costs[0].2/2) as u64);
    eprintln!("TOFFOLI_ACTUAL_LEAN_V4_ALLMR exact_input_cases={total} native_cases={} max_phase_terms={max_phase} producer_rows=128 raw_bits=18 higher_words=4 room=2 classicalABI=512",total*3);
}
#[test]
fn toffoli_actual_lean_source_caller_v4() {
    crate::point_add::pingpong::with_phase_cap(Some(1234),||for on in [false,true] {
        let mut c=Builder::new();let b=c.alloc_qubits(N);let tg=c.alloc_qubits(N);let letters=c.alloc_qubits(5);let _pads=c.alloc_qubits(1234-(2*N+5+37));
        let active=c.active_qubits();let tick=130;let (_,proxy)=proxy_fold(steps()[tick][0],false);let shift=cmp_shift_at(tick);
        let (_,peak)=mode(on,||c.r3_peak(|c|cells::with_tie(None,||cells::with_cmp_shift((shift.0+Y15_CMP_EXTRA+super::n2_cmpx(),shift.1),||cells::with_bridge(proxy,false,||body_capped(c,tick,[letters[0],letters[1],letters[2]],letters[3],letters[4],&b,&tg,proxy,false))))));
        assert_eq!(TOFFOLI_ACTUAL_LEAN_DROPS.with(|x|x.get()),2);let hits=TOFFOLI_ACTUAL_LEAN_HITS.with(|x|x.get());assert_eq!(hits,usize::from(on));assert_eq!(c.active_qubits(),active);assert!(peak<=1234);
        let emitted=c.take_ops().iter().filter(|op|op.kind==OperationType::CCX).count();eprintln!("TOFFOLI_ACTUAL_LEAN_V4_CALLER cap=1234 room=37 tick=130 new={on} hits={hits} peak={peak} emitted={emitted} source_caller_resource_only=true");
    });
}
#[test]
fn toffoli_actual_lean_phase_fault_v4() {
    let (mut ops,acc,controls,abi,pads,esh,_,_)=fixture(true);let ccx=ops.iter().rposition(|op|op.kind==OperationType::CCX).unwrap();let cz=ops.iter().enumerate().skip(ccx+1).find(|(_,op)|op.kind==OperationType::CZ).unwrap().0;ops.remove(cz);
    let (nq,_,_,_)=analyze_ops(ops.iter());let mut detected=false;
    for base in (0..1usize<<18).step_by(64) {let (input,_)=inputs(nq as usize,base,0,&acc,&controls,&abi,&pads,esh);
        if let Err(why)=super::toffoli_actual_lean_phase_kernel_v4::audit(&ops,&input,&[]) {if why.starts_with("nonzero phase polynomial") {detected=true;break;}}
    }
    assert!(detected,"producer-admitted phase fault must be detected");
}
