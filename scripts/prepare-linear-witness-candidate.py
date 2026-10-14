"""Emit a point_add-only live linear-witness candidate and external native tests.

Does not edit the given baseline checkout. Candidate files are separate copies.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

SPEC=importlib.util.spec_from_file_location("span",Path(__file__).with_name("prepare-linear-span-audit.py"))
SPAN=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SPAN)

NATIVE=r'''
#[test]
fn native_linear_witness_preserves_dirty_basis_bits_and_measurement_phase() {
    use crate::circuit::{BitId,RegisterId};
    use quantum_ecc::sim::Simulator;
    use sha3::digest::{Update,ExtendableOutput};
    fn gate(k:OperationType,a:Option<u64>,b:Option<u64>,t:u64)->Op {
        let mut o=Op::empty();o.kind=k;o.q_target=QubitId(t);
        if let Some(a)=a{o.q_control1=QubitId(a);}if let Some(b)=b{o.q_control2=QubitId(b);}o
    }
    let mut ops=Vec::new();
    let mut reg=Op::empty();reg.kind=OperationType::Register;reg.r_target=RegisterId(0);ops.push(reg);
    for q in [0,1,2,5] {let mut o=Op::empty();o.kind=OperationType::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);ops.push(o);}
    for bit in [0,1] {let mut o=Op::empty();o.kind=OperationType::AppendToRegister;o.r_target=RegisterId(0);o.c_target=BitId(bit);ops.push(o);}
    ops.push(gate(OperationType::CCX,Some(0),Some(1),3));
    ops.push(gate(OperationType::CX,Some(2),None,3));
    ops.push(gate(OperationType::Z,None,None,3));
    let mut push=Op::empty();push.kind=OperationType::PushCondition;push.c_condition=BitId(0);ops.push(push);
    let mut invert=Op::empty();invert.kind=OperationType::BitInvert;invert.c_target=BitId(0);ops.push(invert);
    let mut final_ccx=gate(OperationType::CCX,Some(0),Some(1),5);final_ccx.c_condition=BitId(1);ops.push(final_ccx);
    let mut pop=Op::empty();pop.kind=OperationType::PopCondition;ops.push(pop);
    ops.push(gate(OperationType::CZ,Some(5),None,2));
    let mut hmr=gate(OperationType::Hmr,None,None,3);hmr.c_target=BitId(2);ops.push(hmr);
    for o in &ops{o.validate();}
    let rewritten=linear_witnesses(ops.clone());
    assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),2);
    assert_eq!(rewritten.iter().filter(|o|o.kind==OperationType::CCX).count(),1);
    for seed in 0..32u64 {
        let mut hash=sha3::Shake256::default();hash.update(b"native-linear-witness-phase-v1");hash.update(&seed.to_le_bytes());
        let mut xa=hash.clone().finalize_xof();let mut xb=hash.finalize_xof();
        let mut a=Simulator::new(6,3,&mut xa);let mut b=Simulator::new(6,3,&mut xb);
        for (i,q) in [0usize,1,2,5].iter().enumerate(){a.qubits[*q]=(0..64).fold(0u64,|v,lane|v|(((lane>>i)&1)as u64)<<lane);}
        for bit in 0..2{a.bits[bit]=(0..64).fold(0u64,|v,lane|v|(((lane>>(4+bit))&1)as u64)<<lane);}
        b.qubits=a.qubits.clone();b.bits=a.bits.clone();
        a.apply_iter(ops.iter());b.apply_iter(rewritten.iter());
        assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits,b.bits);assert_eq!(a.phase,b.phase);
    }
}
'''


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("baseline",type=Path)
    a.add_argument("destination",type=Path)
    args=a.parse_args()
    base,dest=args.baseline.resolve(),args.destination.resolve()
    subprocess.run([sys.executable,str(Path(__file__).with_name("prepare-linear-span-audit.py")),str(base),str(dest/"crate")],check=True)
    code=SPAN.SPAN.replace("pub(crate) fn audit_span(ops:&[Op]) {","pub(crate) fn linear_witnesses(ops:Vec<Op>)->Vec<Op> {\n    let mut out=Vec::with_capacity(ops.len());")
    code=code.replace("Support::new(ops)","Support::new(&ops)")
    code=code.replace("for(at,op)in ops.iter().enumerate(){","for(at,op)in ops.iter().enumerate(){\n        let mut replacement=None;")
    code=code.replace("hits+=1;weight+=", "replacement=Some((constant,qs.clone()));\n                    hits+=1;weight+=")
    marker="for &q in &changed{for &a in &state.qubits[q].atoms{atoms.entry(a).or_default().insert(q);}}"
    code=code.replace(marker,marker+r'''
        if let Some((constant,qs))=replacement {
            if constant {let mut r=Op::empty();r.kind=OperationType::X;r.q_target=op.q_target;r.c_condition=op.c_condition;r.validate();out.push(r);}
            for q in qs {let mut r=Op::empty();r.kind=OperationType::CX;r.q_control1=QubitId(q as u64);r.q_target=op.q_target;r.c_condition=op.c_condition;r.validate();out.push(r);}
        }else{out.push(*op);}
''')
    code=code.replace('println!("LINEAR_SPAN_AUDIT attempts={attempts} hits={hits} depth_proxy={weight} scorer=NONE");','println!("LINEAR_SPAN_AUDIT attempts={attempts} hits={hits} depth_proxy={weight} scorer=NONE");\n    out')
    candidate=dest/"candidate-source/point_add"
    candidate.mkdir(parents=True,exist_ok=True)
    interned=(base/"src/point_add/interned_witness.rs").read_text().replace("\r\n","\n").replace("#[derive(Clone, PartialEq, Eq, Hash)]","#[derive(Clone, Debug, PartialEq, Eq, Hash)]")
    (candidate/"interned_witness.rs").write_text(interned+code+NATIVE,encoding="utf-8")
    mod=(base/"src/point_add/mod.rs").read_text().replace("\r\n","\n")
    needle='    let nonce: u64 = required_env("TAIL_NONCE");'
    assert mod.count(needle)==1
    (candidate/"mod.rs").write_text(mod.replace(needle,'    ops = interned_witness::linear_witnesses(ops);\n'+needle),encoding="utf-8")
    research=dest/"crate/src/interned_witness.rs"
    research.write_text(interned+code+NATIVE,encoding="utf-8")
    p=dest/"crate/src/main.rs"
    p.write_text(p.read_text().replace("interned_witness::audit_span(&ops);","let _candidate = interned_witness::linear_witnesses(ops);"),encoding="utf-8")
    p=dest/"crate/Cargo.toml"
    p.write_text(p.read_text().replace('name="linear_span_audit"','name="linear_witness_native"')+'sha3="0.10"\n',encoding="utf-8")


if __name__=="__main__":main()
