"""External immutable-expression audit for two-wire XOR control products.

This is a research census, not a source rewrite or qualified resource result.
Every hit is an exact equality in the public interned Boolean abstraction.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("zero", Path(__file__).with_name("prepare-wire-zero-audit.py"))
ZERO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ZERO)

QUERY = r'''
pub(crate) fn audit_pairs(ops: &[Op]) -> usize {
    use std::collections::{HashMap,BTreeSet};
    let mut state=Support::new(ops);
    let mut values:HashMap<Affine,BTreeSet<usize>>=HashMap::new();
    let mut atoms:HashMap<u64,BTreeSet<usize>>=HashMap::new();
    for (q,v) in state.qubits.iter().enumerate() {
        values.entry(v.clone()).or_default().insert(q);
        for &a in &v.atoms { atoms.entry(a).or_default().insert(q); }
    }
    let mut hits=Vec::new(); let mut depth=0i32; let mut weight=0f64;
    let mut attempts=0usize; let mut candidates=0usize;
    for (at,op) in ops.iter().enumerate() {
        if op.kind==OperationType::PushCondition {depth+=1;}
        if op.kind==OperationType::PopCondition {depth-=1;}
        if op.kind==OperationType::CCX {
            let product=state.and(&state.qubits[op.q_control1.0 as usize].clone(),
                                   &state.qubits[op.q_control2.0 as usize].clone());
            let t=op.q_target.0 as usize;
            // Skip a one-wire identity already covered by the baseline pass.
            let single=values.get(&product).is_some_and(|qs|qs.iter().any(|&q|q!=t));
            if !single && !product.is_zero() && !product.is_one() {
                attempts+=1;
                // Some chosen atom must appear in exactly one of the two terms.
                let least=product.atoms.iter().min_by_key(|a|atoms.get(a).map_or(0,|qs|qs.len()));
                if let Some(a)=least {
                    if let Some(qs)=atoms.get(a) {
                        for &q in qs {
                            if q==t {continue;}
                            candidates+=1;
                            let other=state.xor(&product,&state.qubits[q].clone());
                            if let Some(rs)=values.get(&other) {
                                if let Some(&r)=rs.iter().find(|&&r|r!=t && r!=q) {
                                    // Direct equality is rechecked before recording a hit.
                                    assert_eq!(state.xor(&state.qubits[q].clone(),&state.qubits[r].clone()),product);
                                    weight+=2f64.powi(-depth-i32::from(op.c_condition!=NO_BIT));
                                    hits.push((at,q,r,t,depth,op.c_condition)); break;
                                }
                            }
                        }
                    }
                }
            }
        }
        let changed:Vec<usize>=match op.kind {
            OperationType::CCX|OperationType::CX|OperationType::X|OperationType::R|OperationType::Hmr=>vec![op.q_target.0 as usize],
            OperationType::Swap=>vec![op.q_control1.0 as usize,op.q_target.0 as usize],_=>vec![]};
        for &q in &changed {
            let old=&state.qubits[q];
            let slots=values.get_mut(old).unwrap();assert!(slots.remove(&q));
            if slots.is_empty(){values.remove(old);}
            for a in &old.atoms { let slots=atoms.get_mut(a).unwrap();assert!(slots.remove(&q));if slots.is_empty(){atoms.remove(a);} }
        }
        state.step(op);
        for &q in &changed {
            let v=&state.qubits[q]; values.entry(v.clone()).or_default().insert(q);
            for &a in &v.atoms {atoms.entry(a).or_default().insert(q);}
        }
    }
    println!("PAIR_XOR_AUDIT attempts={attempts} candidates={candidates} hits={} depth_proxy={weight}",hits.len());
    let count=hits.len();
    for (at,q,r,t,d,c) in hits { println!("PAIR_XOR_HIT op={at} sources={q},{r} target={t} depth={d} explicit_condition={}",c!=NO_BIT); }
    count
}

#[test]
fn exact_pair_and_mutable_slot_fault() {
    use crate::circuit::RegisterId;
    fn gate(k:OperationType,a:u64,b:u64,t:u64)->Op {
        let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);o
    }
    let mut ops=Vec::new();
    let mut reg=Op::empty();reg.kind=OperationType::Register;reg.r_target=RegisterId(0);ops.push(reg);
    for q in 0..3 {let mut o=Op::empty();o.kind=OperationType::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);ops.push(o);}
    ops.push(gate(OperationType::CCX,0,1,3));
    let mut cx=Op::empty();cx.kind=OperationType::CX;cx.q_control1=QubitId(2);cx.q_target=QubitId(3);ops.push(cx);
    ops.push(gate(OperationType::CCX,0,1,5));
    assert_eq!(audit_pairs(&ops),1);
    let mut fault=ops.clone();let mut x=Op::empty();x.kind=OperationType::X;x.q_target=QubitId(2);fault.insert(fault.len()-1,x);
    assert_eq!(audit_pairs(&fault),0,"a current wire must not keep its pre-mutation witness");
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    base, dest = args.baseline.resolve(), args.destination.resolve()
    (dest / "src").mkdir(parents=True, exist_ok=True)
    original = (base / "src/point_add/interned_witness.rs").read_bytes()
    source = original.decode().replace("\r\n", "\n")
    # Debug formatting is solely for the equality assertion, not its semantics.
    source = source.replace("#[derive(Clone, PartialEq, Eq, Hash)]", "#[derive(Clone, Debug, PartialEq, Eq, Hash)]")
    (dest / "src/interned_witness.rs").write_text(source + QUERY, encoding="utf-8")
    main = ZERO.MAIN.replace("mod affine_simplify;\nmod quadratic_simplify;\nmod truth_simplify;", "mod interned_witness;")
    main = main.replace('assert_eq!(args.len(),3,"stream peak-op-index");', 'assert_eq!(args.len(),2,"stream");')
    main = main.replace("truth_simplify::audit_zero(&ops,args[2].parse().unwrap());", "interned_witness::audit_pairs(&ops);")
    (dest / "src/main.rs").write_text(main, encoding="utf-8")
    (dest / "Cargo.toml").write_text('[package]\nname="linear_pair_audit"\nversion="0.1.0"\nedition="2021"\n\n[dependencies]\nquantum_ecc={path='+json.dumps(str(base))+'}\nzstd="0.13"\n', encoding="utf-8")
    (dest / "rust-toolchain").write_bytes((base / "rust-toolchain").read_bytes())
    (dest / "provenance.json").write_text(json.dumps({"baseline":str(base),"interned_source_sha256":hashlib.sha256(original).hexdigest(),"scope":"Exact two-live-wire XOR census only; no candidate, scorer, or sampled control deletion."},indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
