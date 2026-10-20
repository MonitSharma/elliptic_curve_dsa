/// Same measured known-top-output channel as modular::terminal_step_known.
/// The top bit is forced even on inputs that violate its arithmetic promise.
pub(super) fn known_top(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId,drops:&[usize],desired:bool)->bool{
    run(c,acc,rows,ones,cin,drops,false,&mut|_,_,_|{},None,Some(desired))
}
fn known_phase(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],ci:QubitId,desired:bool){
    let n=acc.len();let bit=c.alloc_bit();c.hmr(acc[n-1],bit);if desired{c.x(acc[n-1]);}
    c.push_condition(bit);
    // desired XOR a_top XOR MAJ(a_pen,b_pen,ci).
    if desired^ones[n-1]{c.cz(ci,ci);c.x(ci);c.cz(ci,ci);c.x(ci);}
    for &q in &rows[n-1]{c.cz(q,q);}
    for &q in &rows[n-2]{c.cz(q,acc[n-2]);c.cz(q,ci);}
    if ones[n-2]{c.cz(acc[n-2],acc[n-2]);c.cz(ci,ci);}
    c.cz(acc[n-2],ci);c.pop_condition();c.free_bit(bit);
}
