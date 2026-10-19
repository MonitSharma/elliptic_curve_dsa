//! Observation only: source-exclusive carry pivot availability.
use super::builder::Builder;
use crate::circuit::QubitId;
use std::collections::{BTreeMap,BTreeSet};
pub(super) fn begin(c:&Builder,acc:&[QubitId],terms:&[Vec<QubitId>],cin:Option<QubitId>,kind:&str,hook:bool)->usize{
    let n=acc.len();let targets:BTreeSet<_>=acc.iter().map(|q|q.0).collect();let mut seen=BTreeMap::new();
    let disjoint=terms.iter().flatten().all(|q|!targets.contains(&q.0)&&Some(*q)!=cin);
    for row in terms{for q in row{*seen.entry(q.0).or_insert(0usize)+=1;}}
    let mut has_carry=cin.is_some();let mut pivots=Vec::new();
    for i in 0..n.saturating_sub(2){
        if has_carry&&disjoint&&terms[i].iter().any(|q|seen[&q.0]==1){pivots.push(i);}
        has_carry=has_carry||!terms[i].is_empty();
    }
    let list=pivots.iter().map(|i|i.to_string()).collect::<Vec<_>>().join(",");
    eprintln!("PARITY_SITE\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",c.current_phase(),kind,c.op_count(),n,c.active_qubits(),
        super::pingpong::heo_hooks::cap().saturating_sub(c.active_qubits()as usize),usize::from(cin.is_some()),usize::from(hook),usize::from(disjoint),list);
    c.op_count()
}
pub(super) fn end(c:&Builder,kind:&str,start:usize){eprintln!("PARITY_SITE_END\t{kind}\t{start}\t{}",c.op_count());}
