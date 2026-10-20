//! Release the first carry after the second is built; regenerate it in the
//! reverse sweep after higher carries have been released. n>=5, live cin.
//! One less owned carry, one extra CCX and one extra HMR. Sources restore.
use super::builder::Builder;
use crate::circuit::QubitId;
use std::collections::BTreeSet;

fn on(c:&mut Builder,row:&[QubitId],one:bool,ci:QubitId)->QubitId{
    let q=if row.is_empty(){ci}else{let q=row[0];for &r in &row[1..]{c.cx(r,q);}c.cx(ci,q);q};if one{c.x(q);}q
}
fn off(c:&mut Builder,row:&[QubitId],one:bool,ci:QubitId){
    let q=row.first().copied().unwrap_or(ci);if one{c.x(q);}if !row.is_empty(){c.cx(ci,q);for &r in row[1..].iter().rev(){c.cx(r,q);}}
}
fn carry(c:&mut Builder,a:QubitId,row:&[QubitId],one:bool,ci:QubitId)->QubitId{
    c.cx(ci,a);let v=on(c,row,one,ci);let out=c.alloc_qubit();c.ccx(a,v,out);off(c,row,one,ci);c.cx(ci,out);c.cx(ci,a);out
}
fn erase(c:&mut Builder,out:QubitId,a:QubitId,row:&[QubitId],one:bool,ci:QubitId){
    c.cx(ci,out);c.cx(ci,a);let v=on(c,row,one,ci);let m=c.alloc_bit();c.hmr(out,m);c.cz_if(a,v,m);c.free_bit(m);c.release_clean(out);off(c,row,one,ci);c.cx(ci,a);
}
pub(super) fn add(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId)->bool{
    let n=acc.len();if n<5||rows.len()!=n||ones.len()!=n{return false;}
    let mut target=BTreeSet::from([cin.0]);if !acc.iter().all(|q|target.insert(q.0)){return false;}
    if !rows.iter().all(|r|{let mut seen=BTreeSet::new();r.iter().all(|q|!target.contains(&q.0)&&seen.insert(q.0))}){return false;}
    let mut cc=vec![None;n];cc[0]=Some(cin);
    for i in 0..n-2{
        let q=carry(c,acc[i],&rows[i],ones[i],cc[i].unwrap());cc[i+1]=Some(q);
        if i==1{erase(c,cc[1].take().unwrap(),acc[0],&rows[0],ones[0],cin);}
    }
    // The final carry toggles directly into the top target bit.
    let i=n-2;let ci=cc[i].unwrap();c.cx(ci,acc[i]);let v=on(c,&rows[i],ones[i],ci);
    c.ccx(acc[i],v,acc[n-1]);off(c,&rows[i],ones[i],ci);c.cx(ci,acc[n-1]);c.cx(ci,acc[i]);
    for i in(0..n).rev(){
        if i==2{assert!(cc[1].is_none());cc[1]=Some(carry(c,acc[0],&rows[0],ones[0],cin));}
        for &q in &rows[i]{c.cx(q,acc[i]);}if ones[i]{c.x(acc[i]);}
        if i!=n-1{c.cx(cc[i].unwrap(),acc[i]);}
        if i>0&&i<n-1{erase(c,cc[i].unwrap(),acc[i-1],&rows[i-1],ones[i-1],cc[i-1].unwrap());}
    }true
}

#[cfg(test)]mod tests{
    use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::digest::XofReader;
    struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
    fn rng(words:&[u64])->Words{Words{data:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0}}
    fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
    fn put<R:XofReader>(s:&mut Simulator<'_,R>,q:QubitId,lane:usize,x:usize){if x&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}
    fn run(n:usize,pattern:usize,inverse:bool,probe:Option<usize>){
        let mut c=Builder::new();let source=c.alloc_qubits(n);let target=c.alloc_qubits(n);let ci=c.alloc_qubit();let shared=c.alloc_qubit();
        let interface:Vec<_>=source.iter().chain(target.iter()).copied().chain([ci,shared]).collect();c.declare_qubit_register(&interface);
        let rows:Vec<Vec<QubitId>>=(0..n).map(|i|match pattern{0=>vec![shared],1=>if i%3==0{vec![]}else{vec![source[i],shared]},_=>vec![source[i]]}).collect();
        let ones:Vec<_>=(0..n).map(|i|pattern==2&&i%3==1).collect();let active=c.active_qubits();
        let((),peak)=c.r3_peak(|c|{assert!(add(c,&target,&rows,&ones,ci));if inverse{c.x_all(&target);assert!(add(c,&target,&rows,&ones,ci));c.x_all(&target);}});
        assert_eq!(peak,active+(n-3)as u32);let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());assert_eq!(nq as usize,interface.len()+n-3);
        assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),n*if inverse{2}else{1});let nr=draws(&ops);assert_eq!(nr,(n-1)*if inverse{2}else{1});
        let starts:Vec<_>=if probe.is_some(){vec![0x6F3C0]}else{(0..1usize<<(2*n+2)).step_by(64).collect()};
        for start in starts{let words:Vec<_>=(0..nr).map(|j|match probe{Some(p)=>if p==j||p==nr{u64::MAX}else{0},None=>0xD1B54A32D192ED03u64.wrapping_mul((start+j+1)as u64).rotate_left(j as u32)}).collect();let mut random=rng(&words);
            let mut s=Simulator::new(nq as usize,nb as usize,&mut random);for lane in 0..64{for(i,&q)in interface.iter().enumerate(){put(&mut s,q,lane,(start+lane)>>i);}}let original=s.qubits.clone();s.apply_iter(ops.iter());
            for lane in 0..64{let value=start+lane;let mut av=0usize;for(i,row)in rows.iter().enumerate(){let bit=row.iter().fold(usize::from(ones[i]),|x,q|x^(value>>interface.iter().position(|r|r==q).unwrap()&1));av|=bit<<i;}
                let bv=value>>n&((1<<n)-1);let wanted=if inverse{bv}else{(av+bv+(value>>(2*n)&1))&((1<<n)-1)};
                for i in 0..n{assert_eq!(s.qubits[target[i].0 as usize]>>lane&1,(wanted>>i&1)as u64,"n={n} pattern={pattern} inverse={inverse}");}}
            for i in 0..nq as usize{if !target.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);drop(s);assert_eq!(random.pos,nr*8);
        }
    }
    #[test]fn all_small_parity_addends_with_shared_or_empty_sources_and_constants(){for n in 5usize..=7{for pattern in 0..3{run(n,pattern,false,None);}}}
    #[test]fn all_physical_measurement_coefficients_and_inverse_on_sixty_four_bases(){for inverse in[false,true]{let nr=7*if inverse{2}else{1};for probe in 0..nr+2{for pattern in 0..3{run(8,pattern,inverse,Some(probe));}}}}
    #[test]fn unsafe_alias_or_too_short_rejected_before_emission(){let mut c=Builder::new();let a=c.alloc_qubits(5);let b=c.alloc_qubits(5);let ci=c.alloc_qubit();let op=c.op_count();let mut rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();rows[2]=vec![b[1]];assert!(!add(&mut c,&b,&rows,&[false;5],ci));assert!(!add(&mut c,&b[..4],&rows[..4],&[false;4],ci));assert_eq!(op,c.op_count());}
}
