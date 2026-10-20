pub(super) fn plain_optional(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:Option<QubitId>,hook:&mut dyn FnMut(&mut Builder,usize,QubitId))->bool{
    if cap()>=1234||acc.len()!=rows.len()||acc.len()!=ones.len(){return false;}
    let trim=if cin.is_none(){rows.iter().zip(ones).take_while(|(r,one)|r.is_empty()&&!**one).count()}else{0};
    let acc=&acc[trim..];let rows=&rows[trim..];let ones=&ones[trim..];let n=acc.len();if n<3{return false;}
    let need=(c.active_qubits()as usize+n-2).saturating_sub(cap());if need==0{return false;}
    let drops=if let Some(q)=cin{
        if !super::phase_pebble::valid_mode(acc,rows,ones,q,&[],false){return false;}
        let Some(ds)=choose(rows,need,false,&vec![true;n])else{return false;};ds
    }else{
        if !super::zero_carry::valid(acc,rows,ones,&[]){return false;}
        let Some(ds)=choose(&rows[1..],need,false,&vec![true;n-1])else{return false;};ds
    };
    let before=c.op_count();let active=c.active_qubits();
    if let Some(q)=cin{assert!(super::phase_pebble::add_with_hook(c,acc,rows,ones,q,&drops,&mut|c,i,q|hook(c,i+trim,q)));}
    else{assert!(super::zero_carry::add(c,acc,rows,ones,&drops,&mut|c,i,q|hook(c,i+trim,q)));}
    eprintln!("PHASE_OPTIONAL\t{}\t{before}\t{}\t{active}\t{n}\t{need}\t{}\t{drops:?}",c.current_phase(),c.op_count(),usize::from(cin.is_some()));true
}
