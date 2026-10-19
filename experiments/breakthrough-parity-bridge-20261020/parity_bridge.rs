//! Exact mixed borrowed-source / measured carry ladder for parity addends.
//! Source pivots must be exclusive across all addend expressions. No allocation
//! limits, approximate comparisons, or GCD iteration changes are introduced.
use super::builder::Builder;
use crate::circuit::QubitId;
use std::collections::{BTreeMap,BTreeSet};

fn on(c:&mut Builder,term:&[QubitId],carry:Option<QubitId>)->QubitId{
    if let Some((&pivot,rest))=term.split_first(){
        for &q in rest{c.cx(q,pivot);}if let Some(q)=carry{c.cx(q,pivot);}pivot
    }else{carry.expect("A nonzero carry supplies an empty parity")}
}
fn off(c:&mut Builder,term:&[QubitId],carry:Option<QubitId>){
    if let Some((&pivot,rest))=term.split_first(){
        if let Some(q)=carry{c.cx(q,pivot);}for &q in rest.iter().rev(){c.cx(q,pivot);}
    }
}
fn erase(c:&mut Builder,q:QubitId,a:QubitId,b:QubitId){
    let m=c.alloc_bit();c.hmr(q,m);c.cz_if(a,b,m);c.free_bit(m);c.release_clean(q);
}

/// Add acc += parity(terms) + cin, modulo2^n. Returns false without emitting
/// operations if a requested source pivot cannot be borrowed safely. Pivots
/// occur in exactly one row, are disjoint from acc and cin, and are restored.
pub(super) fn add(c:&mut Builder,acc:&[QubitId],terms:&[Vec<QubitId>],cin:Option<QubitId>,indices:&[usize])->bool{
    let n=acc.len();
    if n<3||terms.len()!=n{return false;}
    let mut aset=BTreeSet::new();
    if !acc.iter().all(|q|aset.insert(q.0))||cin.is_some_and(|q|aset.contains(&q.0)){return false;}
    let mut occurrences=BTreeMap::new();
    for row in terms{
        let mut seen=BTreeSet::new();
        for &q in row{
            if aset.contains(&q.0)||Some(q)==cin||!seen.insert(q.0){return false;}
            *occurrences.entry(q.0).or_insert(0usize)+=1;
        }
    }
    let mut pivots=vec![None;n];let mut chosen=BTreeSet::new();
    for &i in indices{
        if i+2>=n||!chosen.insert(i)||i==0&&cin.is_none(){return false;}
        let pivot=terms[i].iter().copied().filter(|q|Some(*q)!=cin&&occurrences[&q.0]==1).min_by_key(|q|q.0);
        let Some(pivot)=pivot else{return false;};pivots[i]=Some(pivot);
    }
    // A skipped initial zero carry must not reach a borrowed MAJ stage.
    let mut has_carry=cin.is_some();
    for i in 0..n-2{
        if pivots[i].is_some()&&!has_carry{return false;}
        has_carry=has_carry||!terms[i].is_empty();
    }
    let mut addend=terms.to_vec();
    for i in 0..n{
        if let Some(p)=pivots[i]{
            for &q in &terms[i]{if q!=p{c.cx(q,p);}}
            addend[i]=vec![p];
        }
    }
    let mut carries=vec![None;n];carries[0]=cin;
    for i in 0..n-1{
        let ci=carries[i];
        if let Some(p)=pivots[i]{
            let ci=ci.expect("Borrowed carry admission");
            c.cx(p,acc[i]);c.cx(p,ci);c.ccx(acc[i],ci,p);carries[i+1]=Some(p);
            continue;
        }
        if ci.is_none()&&addend[i].is_empty(){continue;}
        if let Some(q)=ci{c.cx(q,acc[i]);}
        let v=on(c,&addend[i],ci);
        if i+2==n{
            c.ccx(acc[i],v,acc[n-1]);off(c,&addend[i],ci);
            if let Some(q)=ci{c.cx(q,acc[n-1]);c.cx(q,acc[i]);}
        }else{
            let q=c.alloc_qubit();c.ccx(acc[i],v,q);off(c,&addend[i],ci);
            if let Some(ci)=ci{c.cx(ci,q);c.cx(ci,acc[i]);}carries[i+1]=Some(q);
        }
    }
    for i in(0..n).rev(){
        let ci=carries[i];
        if let Some(p)=pivots[i]{
            let ci=ci.unwrap();c.ccx(acc[i],ci,p);c.cx(p,ci);c.cx(ci,acc[i]);continue;
        }
        if i+1<n{
            if let Some(next)=carries[i+1]{
                if let Some(ci)=ci{c.cx(ci,next);c.cx(ci,acc[i]);}
                let v=on(c,&addend[i],ci);erase(c,next,acc[i],v);off(c,&addend[i],ci);
                if let Some(ci)=ci{c.cx(ci,acc[i]);}
            }
        }
        for &q in &addend[i]{c.cx(q,acc[i]);}if let Some(ci)=ci{c.cx(ci,acc[i]);}
    }
    for i in(0..n).rev(){
        if let Some(p)=pivots[i]{for &q in terms[i].iter().rev(){if q!=p{c.cx(q,p);}}}
    }
    true
}

#[cfg(test)]mod tests{
    use super::*;
    use crate::circuit::{analyze_ops,OperationType,Op,NO_BIT};
    use crate::sim::Simulator;
    use sha3::digest::XofReader;
    struct Words{data:Vec<u8>,pos:usize}
    impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
    fn rng(words:&[u64])->Words{Words{data:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0}}
    fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
    fn put<R:XofReader>(s:&mut Simulator<'_,R>,q:QubitId,lane:usize,bit:usize){if bit&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}
    fn build(n:usize,indices:&[usize],with_cin:bool,inverse:bool)->(Vec<Op>,Vec<QubitId>,Vec<QubitId>,QubitId,QubitId,usize){
        let mut b=Builder::new();let a=b.alloc_qubits(n);let acc=b.alloc_qubits(n);let shared=b.alloc_qubit();let ci=b.alloc_qubit();
        let terms:Vec<Vec<QubitId>>=a.iter().enumerate().map(|(i,&q)|if i%2==0{vec![shared,q]}else{vec![q]}).collect();
        let cin=with_cin.then_some(ci);assert!(add(&mut b,&acc,&terms,cin,indices));let split=b.op_count();
        if inverse{
            assert!(with_cin);for &q in &a{b.x(q);}b.x(ci);
            assert!(add(&mut b,&acc,&terms,Some(ci),indices));
            b.x(ci);for &q in &a{b.x(q);}
        }
        (b.take_ops(),a,acc,shared,ci,split)
    }
    #[test]fn exhaustive_parity_addends_source_preservation_and_gate_space_trade(){
        for n in 3usize..=7{for with_cin in[false,true]{
            let first=if with_cin{0}else{1};
            let patterns=vec![vec![],(first..n-2).collect(),(first..n-2).step_by(2).collect()];
            for indices in patterns{
                let(ops,a,acc,shared,ci,_)=build(n,&indices,with_cin,false);let(nq,nb,_,_)=analyze_ops(ops.iter());
                let nr=draws(&ops);let mask=(1usize<<n)-1;
                assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),n-1+indices.len());
                assert_eq!(nq as usize,2*n+2+n-2-indices.len());
                for start in(0..(1usize<<(2*n+2))).step_by(64){
                    let words:Vec<_>=(0..nr).map(|j|0xD1B54A32D192ED03u64.rotate_left((j%64)as u32)).collect();let mut random=rng(&words);
                    let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
                    for lane in 0..64{let value=start+lane;for i in 0..n{put(&mut s,a[i],lane,value>>i);put(&mut s,acc[i],lane,value>>(n+i));}
                        put(&mut s,shared,lane,value>>(2*n));put(&mut s,ci,lane,value>>(2*n+1));}
                    let original=s.qubits.clone();s.apply_iter(ops.iter());
                    for lane in 0..64{let value=start+lane;let mut aa=value&mask;let bb=(value>>n)&mask;
                        if value>>(2*n)&1!=0{for i in(0..n).step_by(2){aa^=1<<i;}}
                        let incoming=usize::from(with_cin)*(value>>(2*n+1)&1);let expected=(aa+bb+incoming)&mask;
                        for i in 0..n{assert_eq!(s.qubits[acc[i].0 as usize]>>lane&1,(expected>>i&1)as u64);}}
                    for i in 0..nq as usize{if !acc.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);
                }
            }
        }}
    }
    #[test]fn every_physical_measurement_phase_coefficient_and_inverse(){
        let n=8;let(ops,a,acc,shared,ci,split)=build(n,&[0,2,4],true,true);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=draws(&ops);
        assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::PushCondition|OperationType::PopCondition)));
        assert!(ops.iter().all(|o|o.c_condition==NO_BIT||matches!(o.kind,OperationType::Z|OperationType::CZ|OperationType::CCZ)));
        for probe in 0..nr+2{
            let mut words=vec![0;nr];if probe<nr{words[probe]=u64::MAX;}else if probe==nr{words.fill(u64::MAX);}
            let mut random=rng(&words);let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
            for lane in 0..64{let value=(lane*12347)^0x5A31;for i in 0..n{put(&mut s,a[i],lane,value>>i);put(&mut s,acc[i],lane,value>>(n+i));}
                put(&mut s,shared,lane,lane);put(&mut s,ci,lane,lane>>1);}
            let original=s.qubits.clone();s.apply_iter(ops[..split].iter());assert_eq!(s.phase,0);
            s.apply_iter(ops[split..].iter());assert_eq!(s.qubits,original);assert_eq!(s.phase,0);
            drop(s);assert_eq!(random.pos,nr*8);
        }
    }
    #[test]fn unsafe_aliases_and_missing_pivots_are_rejected_before_emission(){
        let mut b=Builder::new();let a=b.alloc_qubits(5);let acc=b.alloc_qubits(5);let ci=b.alloc_qubit();
        let base:Vec<_>=a.iter().map(|&q|vec![q]).collect();let start=b.op_count();
        let mut bad=base.clone();bad[2].push(a[1]);assert!(!add(&mut b,&acc,&bad,Some(ci),&[1]));
        bad=base.clone();bad[1]=vec![acc[2]];assert!(!add(&mut b,&acc,&bad,Some(ci),&[1]));
        assert!(!add(&mut b,&acc,&base,None,&[0]));assert!(!add(&mut b,&acc,&base,Some(ci),&[1,1]));
        assert!(!add(&mut b,&acc,&base,Some(a[1]),&[1]));assert!(!add(&mut b,&acc,&base,Some(ci),&[3]));
        assert!(!add(&mut b,&acc,&base,Some(a[4]),&[1]));
        assert_eq!(b.op_count(),start);
    }
}
