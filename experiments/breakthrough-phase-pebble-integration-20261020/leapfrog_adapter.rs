fn phase_plain_try(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],cin:Option<QubitId>)->bool{
    let Some(cin)=cin else{return false;};let n=acc.len();if n<3||super::phase_fit::cap()>=1234{return false;}
    let need=(c.active_qubits()as usize+n-2).saturating_sub(super::phase_fit::cap());if need==0||!super::phase_fit::source_ok(acc,rows,cin){return false;}
    let Some(drops)=super::phase_fit::choose(rows,need,false,&vec![true;n])else{return false;};let before=c.op_count();let mut h=Y28_HOOK.with(|v|v.take());
    assert!(super::phase_pebble::add_with_hook(c,acc,rows,&vec![false;n],cin,&drops,&mut|c,i,q|y28_apply(c,&mut h,i,q)));
    assert!(h.is_none(),"phase-pebble did not consume pending carry hook");eprintln!("PHASE_PEBBLE_LADDER\t{}\t{before}\t{}\t{n}\t{need}\t{drops:?}",c.current_phase(),c.op_count());true
}
// The returned outer Option indicates that the entire original chunk ran.
fn phase_chunk_try(c:&mut Builder,acc:&[QubitId],add:&[Lin],cin:QubitId,output:bool,direct:bool)->Option<Option<QubitId>>{
    if super::phase_fit::cap()>=1234||acc.len()<3||!output&&!direct{return None;}
    let owned=if output{acc.len()}else{acc.len()-2};let need=(c.active_qubits()as usize+owned).saturating_sub(super::phase_fit::cap());if need==0{return None;}
    let mut rows:Vec<_>=add.iter().map(|v|v.w.clone()).collect();let mut ones:Vec<_>=add.iter().map(|v|v.one).collect();if !super::phase_fit::source_ok(acc,&rows,cin){return None;}
    let mut target=acc.to_vec();if output{rows.push(Vec::new());ones.push(false);}
    let Some(drops)=super::phase_fit::choose(&rows,need,false,&vec![true;rows.len()])else{return None;};
    let out=output.then(||c.alloc_qubit());if let Some(q)=out{target.push(q);}let before=c.op_count();
    assert!(super::phase_pebble::add(c,&target,&rows,&ones,cin,&drops));eprintln!("PHASE_PEBBLE_CHUNK\t{}\t{before}\t{}\t{}\t{need}\t{drops:?}",c.current_phase(),c.op_count(),acc.len());Some(out)
}
fn yp8_phase_reads(n:usize,tick:usize)->Vec<usize>{
    let view=(n+1).max(6);let mut set=std::collections::BTreeSet::new();for p in[1,2,3,4,view-1]{set.insert((p-1).min(n-1));}
    let h=w1_anchor(tick).saturating_sub(w1_kt(tick));for p in h..h+w1_kt(tick)+2{if p>0&&p+1<view{set.insert((p-1).min(n-1));}}set.into_iter().collect()
}
#[derive(Clone)]struct PhasePause{reserve:usize,forward:bool,reads:Vec<QubitId>}
thread_local!{static PHASE_PAUSE:std::cell::RefCell<Option<PhasePause>>=const{std::cell::RefCell::new(None)};}
struct PhasePauseScope(Option<PhasePause>);impl Drop for PhasePauseScope{fn drop(&mut self){PHASE_PAUSE.with(|v|*v.borrow_mut()=self.0.take());}}
fn phase_pause_scope(acc:&[QubitId],tick:usize,reserve:usize,forward:bool)->PhasePauseScope{
    PhasePauseScope(PHASE_PAUSE.with(|v|v.replace(Some(PhasePause{reserve,forward,reads:yp8_phase_reads(acc.len(),tick).into_iter().map(|i|acc[i]).collect()}))))
}
fn phase_pause_try(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],cin:Option<QubitId>,mid:&mut dyn FnMut(&mut Builder,&[Option<QubitId>]))->bool{
    let Some(cin)=cin else{return false;};let Some(context)=PHASE_PAUSE.with(|v|v.borrow().clone())else{return false;};let n=acc.len();if super::phase_fit::cap()>=1234||n<3||!super::phase_fit::source_ok(acc,rows,cin){return false;}
    let need=(c.active_qubits()as usize+n-1+context.reserve).saturating_sub(super::phase_fit::cap());if need==0{return false;}
    let allowed:Vec<_>=acc.iter().map(|q|context.forward||!context.reads.contains(q)).collect();let Some(drops)=super::phase_fit::choose(rows,need,true,&allowed)else{return false;};
    let mut h=Y28_HOOK.with(|v|v.take());let before=c.op_count();
    assert!(super::phase_pebble::with_pause(c,acc,rows,&vec![false;n],cin,&drops,&mut|c,i,q|y28_apply(c,&mut h,i,q),mid));
    assert!(h.is_none(),"phase-pebble paused carry hook not consumed");eprintln!("PHASE_PEBBLE_PAUSED\t{}\t{before}\t{}\t{n}\t{need}\t{drops:?}",c.current_phase(),c.op_count());true
}
