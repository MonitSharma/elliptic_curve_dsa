
/// Fixed source-based workspace policy; no input, packet, arithmetic range,
/// approximation or iteration setting is consulted or changed.
fn parity_bridge_try(c:&mut Builder,acc:&[QubitId],add:&[Vec<QubitId>],cin:Option<QubitId>)->bool{
    const TARGET:usize=1200;
    let n=acc.len();if n<3||add.len()!=n||Y28_HOOK.with(|x|x.get().is_some()){return false;}
    let need=(c.active_qubits()as usize+n-2).saturating_sub(TARGET);
    if need==0{return false;}
    let mut count=std::collections::BTreeMap::new();
    for row in add{for q in row{*count.entry(q.0).or_insert(0usize)+=1;}}
    let mut has=cin.is_some();let mut indices=Vec::new();
    for i in 0..n-2{
        if has&&add[i].iter().any(|q|Some(*q)!=cin&&count[&q.0]==1){indices.push(i);}
        has=has||!add[i].is_empty();
    }
    if indices.len()<need{return false;}
    indices.truncate(need);
    let start=c.op_count();let active=c.active_qubits();
    if super::parity_bridge::add(c,acc,add,cin,&indices){
        eprintln!("PARITY_USE\t{}\t{start}\t{}\t{n}\t{active}\t{need}",c.current_phase(),c.op_count());true
    }else{assert_eq!(c.op_count(),start,"Rejected adapter emitted operations");false}
}
