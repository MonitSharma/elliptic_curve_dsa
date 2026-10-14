"""Source-bound linear live-wire witnesses in immutable Boolean expressions.

Unbounded sparse GF(2) elimination is purely symbolic: it uses no sampled bits.
The constant row permits a final X. The mutable target is never a witness.
"""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

SPAN = r'''
fn symmetric<T:Ord+Copy>(a:&[T],b:&[T])->Vec<T> {
    let(mut i,mut j,mut out)=(0,0,Vec::new());
    while i<a.len() || j<b.len() {
        if j==b.len() || (i<a.len() && a[i]<b[j]) {out.push(a[i]);i+=1;}
        else if i==a.len() || b[j]<a[i] {out.push(b[j]);j+=1;}
        else {i+=1;j+=1;}
    } out
}
fn formal(v:&Affine)->Vec<u64> {
    let mut r=v.atoms.iter().map(|&a|a.checked_add(1).unwrap()).collect::<Vec<_>>();
    if v.constant {r.insert(0,0);} r
}
fn solve_span(state:&Support,product:&Affine,target:usize)->Option<(bool,Vec<usize>)> {
    use std::collections::BTreeMap;
    let mut basis:BTreeMap<u64,(Vec<u64>,Vec<usize>)>=BTreeMap::new();
    basis.insert(0,(vec![0],vec![usize::MAX]));
    for (q,v) in state.qubits.iter().enumerate() {
        if q==target {continue;}
        let(mut row,mut coeff)=(formal(v),vec![q]);
        while let Some(&p)=row.last() {
            if let Some((known,kcoeff))=basis.get(&p) {row=symmetric(&row,known);coeff=symmetric(&coeff,kcoeff);}
            else {basis.insert(p,(row,coeff));break;}
        }
    }
    let(mut row,mut coeff)=(formal(product),Vec::<usize>::new());
    while let Some(&p)=row.last() {
        let (known,kcoeff)=basis.get(&p)?;
        row=symmetric(&row,known);coeff=symmetric(&coeff,kcoeff);
    }
    let constant=coeff.last()==Some(&usize::MAX);if constant {coeff.pop();}
    assert!(!coeff.contains(&target));
    let mut check=Affine::constant(constant);
    for &q in &coeff {check.constant^=state.qubits[q].constant;check.atoms=symmetric(&check.atoms,&state.qubits[q].atoms);}
    assert_eq!(&check,product);
    Some((constant,coeff))
}
pub(crate) fn audit_span(ops:&[Op]) {
    use std::collections::{HashMap,BTreeSet};
    let mut state=Support::new(ops);
    let mut atoms:HashMap<u64,BTreeSet<usize>>=HashMap::new();
    for(q,v)in state.qubits.iter().enumerate(){for &a in &v.atoms{atoms.entry(a).or_default().insert(q);}}
    let(mut depth,mut attempts,mut hits,mut weight)=(0i32,0usize,0usize,0f64);
    for(at,op)in ops.iter().enumerate(){
        if op.kind==OperationType::PushCondition{depth+=1;}
        if op.kind==OperationType::PopCondition{depth-=1;}
        if op.kind==OperationType::CCX {
            let product=state.and(&state.qubits[op.q_control1.0 as usize].clone(),&state.qubits[op.q_control2.0 as usize].clone());
            let t=op.q_target.0 as usize;
            if !product.is_zero() && !product.is_one() && product.atoms.iter().all(|a|atoms.get(a).is_some_and(|qs|qs.iter().any(|&q|q!=t))) {
                attempts+=1;
                if let Some((constant,qs))=solve_span(&state,&product,t) {
                    hits+=1;weight+=2f64.powi(-depth-i32::from(op.c_condition!=NO_BIT));
                    println!("LINEAR_SPAN_HIT op={at} target={t} constant={constant} sources={qs:?} depth={depth} explicit_condition={}",op.c_condition!=NO_BIT);
                }
            }
        }
        let changed:Vec<usize>=match op.kind{
            OperationType::CCX|OperationType::CX|OperationType::X|OperationType::R|OperationType::Hmr=>vec![op.q_target.0 as usize],
            OperationType::Swap=>vec![op.q_control1.0 as usize,op.q_target.0 as usize],_=>vec![]};
        for &q in &changed{for a in &state.qubits[q].atoms{let slots=atoms.get_mut(a).unwrap();assert!(slots.remove(&q));if slots.is_empty(){atoms.remove(a);}}}
        state.step(op);
        for &q in &changed{for &a in &state.qubits[q].atoms{atoms.entry(a).or_default().insert(q);}}
    }
    println!("LINEAR_SPAN_AUDIT attempts={attempts} hits={hits} depth_proxy={weight} scorer=NONE");
}
#[test]
fn sparse_formal_span_excludes_target_and_tracks_constant() {
    let ops:Vec<Op>=Vec::new();let mut state=Support::new(&ops);
    state.qubits=vec![Affine{constant:false,atoms:vec![0]},Affine{constant:false,atoms:vec![1]},Affine{constant:true,atoms:vec![0,1,2]},Affine{constant:false,atoms:vec![2]}];
    let product=Affine{constant:false,atoms:vec![2]};
    let answer=solve_span(&state,&product,3).unwrap();assert_eq!(answer,(true,vec![0,1,2]));
    state.qubits[2].atoms=vec![0,1,4];
    assert_eq!(solve_span(&state,&product,3),None,"target itself must not prove its own replacement");
}
'''


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("baseline",type=Path)
    a.add_argument("destination",type=Path)
    args=a.parse_args()
    subprocess.run([sys.executable,str(Path(__file__).with_name("prepare-linear-pair-audit.py")),str(args.baseline),str(args.destination)],check=True)
    dest=args.destination.resolve()
    p=dest/"src/interned_witness.rs"
    p.write_text(p.read_text()+SPAN,encoding="utf-8")
    p=dest/"src/main.rs"
    p.write_text(p.read_text().replace("interned_witness::audit_pairs(&ops);","interned_witness::audit_span(&ops);"),encoding="utf-8")
    p=dest/"Cargo.toml"
    p.write_text(p.read_text().replace('name="linear_pair_audit"','name="linear_span_audit"'),encoding="utf-8")


if __name__=="__main__":main()
