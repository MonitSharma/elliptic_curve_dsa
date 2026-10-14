//! Prove conditioned linear conjugations restore values; phase then affine in MR.
use crate::circuit::{Op,OperationType};
use std::collections::{BTreeMap,BTreeSet};
pub(super) fn check(ops:&[Op])->(usize,usize) {
    let mut depth=0usize;let mut blocks=0usize;let mut linear_ops=0usize;
    let mut rows:BTreeMap<u64,BTreeSet<u64>>=BTreeMap::new();
    fn value(rows:&BTreeMap<u64,BTreeSet<u64>>,q:u64)->BTreeSet<u64> {rows.get(&q).cloned().unwrap_or_else(||BTreeSet::from([q]))}
    for op in ops {
        match op.kind {
            OperationType::PushCondition=>{assert_eq!(depth,0,"no multiplied MR conditions");depth=1;rows.clear();continue;},
            OperationType::PopCondition=>{assert_eq!(depth,1);for (&q,row) in &rows {assert_eq!(row,&BTreeSet::from([q]),"conditioned linear block changes q{q}");}depth=0;blocks+=1;continue;},
            _=>{}
        }
        if depth==1 {
            assert_eq!(op.c_condition.0,u64::MAX,"no direct/stack condition product");
            match op.kind {
                OperationType::CX=>{
                    let source=value(&rows,op.q_control1.0);let mut target=value(&rows,op.q_target.0);
                    for bit in source {if !target.insert(bit) {target.remove(&bit);}}
                    rows.insert(op.q_target.0,target);linear_ops+=1;
                },
                OperationType::X=>{let mut target=value(&rows,op.q_target.0);if !target.insert(u64::MAX) {target.remove(&u64::MAX);}rows.insert(op.q_target.0,target);linear_ops+=1;},
                OperationType::Swap=>{let a=value(&rows,op.q_control1.0);let b=value(&rows,op.q_target.0);rows.insert(op.q_control1.0,b);rows.insert(op.q_target.0,a);linear_ops+=1;},
                OperationType::Z|OperationType::CZ|OperationType::CCZ|OperationType::Neg=>{},
                _=>panic!("conditioned nonlinear/nonphase op {:?}",op.kind),
            }
        } else if op.c_condition.0!=u64::MAX {
            assert!(matches!(op.kind,OperationType::Z|OperationType::CZ|OperationType::CCZ|OperationType::Neg),"direct-conditioned value operation {:?}",op.kind);
        }
    }
    assert_eq!(depth,0);(blocks,linear_ops)
}
