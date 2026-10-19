
fn strict_square_ripple(c:&mut Builder,a:&[QubitId],b:&[QubitId],cin:Option<QubitId>,cout:Option<QubitId>)->bool{
    if c.current_phase()!="square"||a.len()!=b.len(){return false;}
    let hard=std::env::var("HEO_PIN_PP_WALK_MAX_QUBITS").expect("Pinned global width").parse::<usize>().unwrap();
    let mut target=b.to_vec();let mut terms:Vec<Vec<QubitId>>=a.iter().map(|&q|vec![q]).collect();
    if let Some(q)=cout{target.push(q);terms.push(Vec::new());}
    let n=target.len();if n<3{return false;}let need=(c.active_qubits()as usize+n-2).saturating_sub(hard);if need==0{return false;}
    let first=usize::from(cin.is_none());if first+need>n-2{return false;}
    let indices:Vec<_>=(first..first+need).collect();let start=c.op_count();let active=c.active_qubits();
    if super::parity_bridge::add(c,&target,&terms,cin,&indices){
        eprintln!("SQUARE_RIPPLE_BRIDGE\t{start}\t{}\t{active}\t{n}\t{need}\t{hard}",c.op_count());true
    }else{assert_eq!(c.op_count(),start);false}
}
