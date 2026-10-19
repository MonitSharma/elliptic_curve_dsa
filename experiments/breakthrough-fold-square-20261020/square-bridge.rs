
/// Use the original square's chunk boundaries, borrowing exclusive source
/// pivots only when its carries would exceed the global width target.
fn strict_square_chunk(c:&mut Builder,map:&[Vec<QubitId>],b:&[QubitId],at:usize,w:usize,prev:QubitId,out:Option<QubitId>)->bool{
    if c.current_phase()!="square"{return false;}
    let hard=std::env::var("HEO_PIN_PP_WALK_MAX_QUBITS").expect("Pinned global width").parse::<usize>().unwrap();
    let mut target=b[at..at+w].to_vec();let mut terms=map[at..at+w].to_vec();
    if let Some(q)=out{target.push(q);terms.push(Vec::new());}
    let n=target.len();if n<3{return false;}
    let need=(c.active_qubits()as usize+n-2).saturating_sub(hard);if need==0{return false;}
    let mut counts=std::collections::BTreeMap::new();for row in &terms{for q in row{*counts.entry(q.0).or_insert(0usize)+=1;}}
    let mut choices:Vec<usize>=(0..n-2).filter(|&i|terms[i].iter().any(|q|*q!=prev&&counts[&q.0]==1)).collect();
    if choices.len()<need{return false;}choices.truncate(need);
    let start=c.op_count();let active=c.active_qubits();
    if super::parity_bridge::add(c,&target,&terms,Some(prev),&choices){
        eprintln!("SQUARE_BRIDGE\t{start}\t{}\t{active}\t{n}\t{need}\t{hard}",c.op_count());true
    }else{assert_eq!(c.op_count(),start);false}
}
