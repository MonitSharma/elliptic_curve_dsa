// Exact source-level contract: low bits1..4, sign, and the unchanged W1 window.
fn yp8_read_indices(nt:usize,nb:usize,tick:usize)->(Vec<usize>,Vec<usize>){
    fn one(real:usize,view:usize,tick:usize)->Vec<usize>{
        assert!(real>0);let mut mask=std::collections::BTreeSet::new();
        for p in[1,2,3,4,view-1]{if p>0{mask.insert((p-1).min(real-1));}}
        let h=w1_anchor(tick).saturating_sub(w1_kt(tick));
        for p in h..h+w1_kt(tick)+2{if p>0&&p+1<view{mask.insert((p-1).min(real-1));}}
        mask.into_iter().collect()
    }
    let tv=(nt+1).max(6);let bv=(nb+1).max(6).min(tv);
    (one(nt,tv,tick),one(nb,bv,tick))
}
#[derive(Clone)]struct Yp8Reads{target:Vec<QubitId>,source:Vec<QubitId>,reserve:usize}
thread_local!{static YP8_READS:std::cell::RefCell<Option<Yp8Reads>>=const{std::cell::RefCell::new(None)};}
struct Yp8ReadScope(Option<Yp8Reads>);
impl Drop for Yp8ReadScope{fn drop(&mut self){YP8_READS.with(|r|*r.borrow_mut()=self.0.take());}}
fn yp8_read_scope(acc:&[QubitId],b:&[QubitId],tick:usize,reserve:usize)->Yp8ReadScope{
    let(t,s)=yp8_read_indices(acc.len(),b.len(),tick);
    let reads=Yp8Reads{target:t.into_iter().map(|i|acc[i]).collect(),source:s.into_iter().map(|i|b[i]).collect(),reserve};
    Yp8ReadScope(YP8_READS.with(|r|r.replace(Some(reads))))
}
fn yp8_flip_reads(q:QubitId)->bool{hard_carry_cap()>=1234||YP8_READS.with(|r|r.borrow().as_ref().is_some_and(|r|r.target.contains(&q)))}
fn yp8_paused_borrow(c:&mut Builder,acc:&[QubitId],add:&[Vec<QubitId>],cin:Option<QubitId>,mid:&mut dyn FnMut(&mut Builder,&[Option<QubitId>]))->bool{
    if hard_carry_cap()>=1234||acc.len()<3||y28_pending(){return false;}
    let Some(reads)=YP8_READS.with(|r|r.borrow().clone())else{return false;};let n=acc.len();
    let need=(c.active_qubits()as usize+n-1+reads.reserve).saturating_sub(hard_carry_cap());if need==0{return false;}
    let protected:Vec<_>=(0..n).filter(|&i|reads.target.contains(&acc[i])).collect();
    let mut count=std::collections::BTreeMap::new();for row in add{for q in row{*count.entry(q.0).or_insert(0usize)+=1;}}
    let mut have=cin.is_some();let mut indices=Vec::new();
    for i in 0..n-2{
        if have&&!protected.contains(&i)&&add[i].iter().any(|q|Some(*q)!=cin&&count[&q.0]==1&&!reads.source.contains(q)){indices.push(i);}
        have=have||!add[i].is_empty();
    }
    if indices.len()<need{return false;}indices.truncate(need);let start=c.op_count();let active=c.active_qubits();
    if super::parity_paused::with_pause(c,acc,add,cin,&indices,&protected,&reads.source,mid){
        eprintln!("YP8_BORROW\t{}\t{start}\t{}\t{active}\t{n}\t{}\t{need}",c.current_phase(),c.op_count(),reads.reserve);true
    }else{assert_eq!(start,c.op_count());false}
}
