//! Exact source-exclusive carry predicate with a complemented parity addend.
//! out=Some toggles the carry into an arbitrary output bit; out=None applies
//! the original phase (-1)^(NOT carry). All data/control operands are restored.
use super::builder::Builder;
use crate::circuit::QubitId;
use std::collections::{BTreeMap,BTreeSet};

fn on(c:&mut Builder,row:&[QubitId],comp:bool,ci:QubitId)->QubitId{
    let q=if let Some((&q,rest))=row.split_first(){for &r in rest{c.cx(r,q);}c.cx(ci,q);q}else{ci};
    if comp{c.x(q);}q
}
fn off(c:&mut Builder,row:&[QubitId],comp:bool,ci:QubitId){
    let q=row.first().copied().unwrap_or(ci);if comp{c.x(q);}
    if !row.is_empty(){c.cx(ci,q);for &r in row[1..].iter().rev(){c.cx(r,q);}}
}
fn erase(c:&mut Builder,q:QubitId,a:QubitId,b:QubitId){
    let m=c.alloc_bit();c.hmr(q,m);c.cz_if(a,b,m);c.free_bit(m);c.release_clean(q);
}

pub(super) fn apply(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],comp:bool,cin:QubitId,out:Option<QubitId>,indices:&[usize])->bool{
    let n=acc.len();if n==0||rows.len()!=n{return false;}
    let m=if out.is_none(){n-1}else{n};
    let mut target=BTreeSet::new();if !acc.iter().all(|q|target.insert(q.0))||target.contains(&cin.0){return false;}
    if out.is_some_and(|q|q==cin||target.contains(&q.0)){return false;}
    let mut counts=BTreeMap::new();
    for row in rows{let mut seen=BTreeSet::new();for q in row{
        if target.contains(&q.0)||*q==cin||Some(*q)==out||!seen.insert(q.0){return false;}
        *counts.entry(q.0).or_insert(0usize)+=1;
    }}
    let mut pivots=vec![None;n];let mut chosen=BTreeSet::new();
    for &i in indices{
        if i>=m||!chosen.insert(i){return false;}
        let Some(q)=rows[i].iter().copied().filter(|q|counts[&q.0]==1).min_by_key(|q|q.0)else{return false;};
        pivots[i]=Some(q);
    }
    let mut add=rows.to_vec();let mut complements=vec![comp;n];
    for i in 0..m{if let Some(q)=pivots[i]{
        for &r in &rows[i]{if r!=q{c.cx(r,q);}}if comp{c.x(q);}
        add[i]=vec![q];complements[i]=false;
    }}
    let mut carry=vec![cin];
    for i in 0..m{
        let ci=carry[i];
        if let Some(q)=pivots[i]{
            c.cx(q,acc[i]);c.cx(q,ci);c.ccx(acc[i],ci,q);carry.push(q);
        }else{
            c.cx(ci,acc[i]);let v=on(c,&add[i],complements[i],ci);
            let q=c.alloc_qubit();c.ccx(acc[i],v,q);off(c,&add[i],complements[i],ci);
            c.cx(ci,q);c.cx(ci,acc[i]);carry.push(q);
        }
    }
    if let Some(q)=out{c.cx(carry[n],q);}else{
        let ci=carry[m];c.cx(ci,acc[m]);let v=on(c,&add[m],complements[m],ci);
        c.cz(acc[m],v);off(c,&add[m],complements[m],ci);c.cx(ci,acc[m]);
        c.x(ci);c.cz(ci,ci);c.x(ci);
    }
    for i in(0..m).rev(){
        let ci=carry[i];
        if let Some(q)=pivots[i]{
            // Inverse MAJ, rather than UMA: the predicate leaves operands intact.
            c.ccx(acc[i],ci,q);c.cx(q,ci);c.cx(q,acc[i]);
        }else{
            let q=carry[i+1];c.cx(ci,q);c.cx(ci,acc[i]);let v=on(c,&add[i],complements[i],ci);
            erase(c,q,acc[i],v);off(c,&add[i],complements[i],ci);c.cx(ci,acc[i]);
        }
    }
    for i in(0..m).rev(){if let Some(q)=pivots[i]{
        if comp{c.x(q);}for &r in rows[i].iter().rev(){if r!=q{c.cx(r,q);}}
    }}
    true
}

#[cfg(test)]mod tests{
    use super::*;
    use crate::circuit::{analyze_ops,Op,OperationType,NO_BIT};
    use crate::sim::Simulator;
    use sha3::digest::XofReader;
    struct Words{data:Vec<u8>,pos:usize}
    impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
    fn rng(words:&[u64])->Words{Words{data:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0}}
    fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
    fn put<R:XofReader>(s:&mut Simulator<'_,R>,q:QubitId,lane:usize,bit:usize){if bit&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}
    fn build(n:usize,comp:bool,output:bool,empty:bool,indices:&[usize])->(Vec<Op>,Vec<QubitId>,Vec<QubitId>,QubitId,QubitId,QubitId){
        let mut c=Builder::new();let a=c.alloc_qubits(n);let b=c.alloc_qubits(n);let cin=c.alloc_qubit();let shared=c.alloc_qubit();let out=c.alloc_qubit();
        let rows:Vec<Vec<QubitId>>=a.iter().enumerate().map(|(i,&q)|if empty&&i%3==2{vec![]}else if i%2==0{vec![shared,q]}else{vec![q]}).collect();
        assert!(apply(&mut c,&b,&rows,comp,cin,output.then_some(out),indices));
        (c.take_ops(),a,b,cin,shared,out)
    }
    fn initial<R:XofReader>(s:&mut Simulator<'_,R>,a:&[QubitId],b:&[QubitId],cin:QubitId,shared:QubitId,out:QubitId,start:usize){
        let n=a.len();for lane in 0..64{let value=start+lane;for i in 0..n{put(s,a[i],lane,value>>i);put(s,b[i],lane,value>>(n+i));}
            put(s,cin,lane,value>>(2*n));put(s,shared,lane,value>>(2*n+1));put(s,out,lane,value>>(2*n+2));}
    }
    fn check<R:XofReader>(s:&Simulator<'_,R>,original:&[u64],a:&[QubitId],out:QubitId,start:usize,comp:bool,output:bool,empty:bool){
        let n=a.len();let mask=(1usize<<n)-1;let mut expected_phase=0u64;let mut expected_out=0u64;
        for lane in 0..64{let value=start+lane;let mut av=0usize;
            for i in 0..n{let bit=if empty&&i%3==2{0}else{(value>>i&1)^if i%2==0{value>>(2*n+1)&1}else{0}};av|=(bit^usize::from(comp))<<i;}
            let carry=(av+(value>>n&mask)+(value>>(2*n)&1))>>n;
            if output{expected_out|=(((value>>(2*n+2)&1)^carry)as u64)<<lane;}
            else if carry==0{expected_phase|=1u64<<lane;}
        }
        for i in 0..s.qubits.len(){if output&&i==out.0 as usize{assert_eq!(s.qubits[i],expected_out);}else{assert_eq!(s.qubits[i],original[i]);}}
        assert_eq!(s.phase,expected_phase);
    }
    #[test]fn exhaustive_complemented_parity_predicate_values_phase_and_workspace(){
        for n in 2usize..=6{for comp in[false,true]{for output in[false,true]{for empty in[false,true]{
            let m=if output{n}else{n-1};let available:Vec<_>=(0..m).filter(|i|!empty||i%3!=2).collect();
            for indices in[vec![],available.iter().take(1).copied().collect(),available.clone()]{
                let(ops,a,b,ci,shared,out)=build(n,comp,output,empty,&indices);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=draws(&ops);
                assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),m+indices.len());
                assert_eq!(nq as usize,2*n+3+m-indices.len());
                for start in(0..(1usize<<(2*n+3))).step_by(64){
                    let words:Vec<_>=(0..nr).map(|j|0x9E3779B97F4A7C15u64.wrapping_mul((start+j+1)as u64).rotate_left((j%64)as u32)).collect();let mut random=rng(&words);
                    let mut s=Simulator::new(nq as usize,nb as usize,&mut random);initial(&mut s,&a,&b,ci,shared,out,start);let original=s.qubits.clone();
                    s.apply_iter(ops.iter());check(&s,&original,&a,out,start,comp,output,empty);
                }
            }
        }}}}
    }
    #[test]fn every_rng_phase_coefficient_on_sixty_four_basis_states(){
        for output in[false,true]{
            let(ops,a,b,ci,shared,out)=build(8,true,output,true,&[0,3,4]);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=draws(&ops);
            assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::PushCondition|OperationType::PopCondition)));
            assert!(ops.iter().all(|o|o.c_condition==NO_BIT||matches!(o.kind,OperationType::Z|OperationType::CZ|OperationType::CCZ)));
            for probe in 0..nr+2{let mut words=vec![0;nr];if probe<nr{words[probe]=u64::MAX;}else if probe==nr{words.fill(u64::MAX);}
                let mut random=rng(&words);let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
                initial(&mut s,&a,&b,ci,shared,out,0x39FC0);let original=s.qubits.clone();s.apply_iter(ops.iter());
                check(&s,&original,&a,out,0x39FC0,true,output,true);drop(s);assert_eq!(random.pos,nr*8);
            }
        }
    }
    #[test]fn reject_shared_pivots_and_output_alias_before_emitting(){
        let mut c=Builder::new();let a=c.alloc_qubits(4);let b=c.alloc_qubits(4);let ci=c.alloc_qubit();let out=c.alloc_qubit();let start=c.op_count();
        let rows=vec![vec![a[0]],vec![a[0]],vec![a[2]],vec![]];
        assert!(!apply(&mut c,&b,&rows,false,ci,Some(out),&[0]));
        assert!(!apply(&mut c,&b,&rows,false,ci,Some(a[2]),&[2]));
        assert!(!apply(&mut c,&b,&rows,true,ci,None,&[3]));assert_eq!(c.op_count(),start);
    }
}
