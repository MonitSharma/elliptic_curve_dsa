//! Carry pebbling with early sum writes and direct phase repair.
//! Selected nonadjacent carries are erased after the next is built. Their
//! target sums are written first. The next carries are erased by the tested
//! two-stage phase kernel, with no regeneration and no additional HMR draws.
use super::builder::Builder;
use crate::circuit::QubitId;
use std::collections::BTreeSet;
fn on(c:&mut Builder,row:&[QubitId],one:bool,ci:QubitId)->QubitId{let q=if row.is_empty(){ci}else{let q=row[0];for &r in &row[1..]{c.cx(r,q);}c.cx(ci,q);q};if one{c.x(q);}q}
fn off(c:&mut Builder,row:&[QubitId],one:bool,ci:QubitId){let q=row.first().copied().unwrap_or(ci);if one{c.x(q);}if !row.is_empty(){c.cx(ci,q);for &r in row[1..].iter().rev(){c.cx(r,q);}}}
fn carry(c:&mut Builder,a:QubitId,row:&[QubitId],one:bool,ci:QubitId)->QubitId{c.cx(ci,a);let v=on(c,row,one,ci);let out=c.alloc_qubit();c.ccx(a,v,out);off(c,row,one,ci);c.cx(ci,out);c.cx(ci,a);out}
fn erase(c:&mut Builder,out:QubitId,a:QubitId,row:&[QubitId],one:bool,ci:QubitId){c.cx(ci,out);c.cx(ci,a);let v=on(c,row,one,ci);let m=c.alloc_bit();c.hmr(out,m);c.cz_if(a,v,m);c.free_bit(m);c.release_clean(out);off(c,row,one,ci);c.cx(ci,a);}
pub(super) fn valid(acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId,drops:&[usize])->bool{
    let n=acc.len();if n<3||rows.len()!=n||ones.len()!=n{return false;}let m=n-2;if drops.len()>m{return false;}let room=m-drops.len();
    for(j,&i)in drops.iter().enumerate(){if i==0||i+1>m||i+1-j>room||j>0&&drops[j-1]+1>=i{return false;}}
    let mut target=BTreeSet::from([cin.0]);if !acc.iter().all(|q|target.insert(q.0)){return false;}
    rows.iter().all(|r|{let mut seen=BTreeSet::new();r.iter().all(|q|!target.contains(&q.0)&&seen.insert(q.0))})
}
pub(super) fn add(c:&mut Builder,acc:&[QubitId],rows:&[Vec<QubitId>],ones:&[bool],cin:QubitId,drops:&[usize])->bool{
    if !valid(acc,rows,ones,cin,drops){return false;}let n=acc.len();let mut cc=vec![None;n];cc[0]=Some(cin);
    for i in 0..n-2{
        let ci=cc[i].unwrap();cc[i+1]=Some(carry(c,acc[i],&rows[i],ones[i],ci));
        if drops.contains(&i){
            for &q in &rows[i]{c.cx(q,acc[i]);}if ones[i]{c.x(acc[i]);}c.cx(ci,acc[i]);
            erase(c,cc[i].take().unwrap(),acc[i-1],&rows[i-1],ones[i-1],cc[i-1].unwrap());
        }
    }
    let i=n-2;let ci=cc[i].unwrap();c.cx(ci,acc[i]);let v=on(c,&rows[i],ones[i],ci);c.ccx(acc[i],v,acc[n-1]);off(c,&rows[i],ones[i],ci);c.cx(ci,acc[n-1]);c.cx(ci,acc[i]);
    for i in(0..n).rev(){
        if drops.contains(&i){continue;}
        for &q in &rows[i]{c.cx(q,acc[i]);}if ones[i]{c.x(acc[i]);}if i!=n-1{c.cx(cc[i].unwrap(),acc[i]);}
        if i>0&&i<n-1{
            let out=cc[i].unwrap();
            if drops.contains(&(i-1)){
                let bit=c.alloc_bit();c.hmr(out,bit);c.release_clean(out);c.push_condition(bit);
                // C_i=MAJ(a_{i-1}, NOT sum_{i-1}, C_{i-1});
                // C_{i-1}=MAJ(a_{i-2}, original_b_{i-2}, C_{i-2}).
                c.x(acc[i-1]);
                assert!(super::phase_fusion::pair(c,acc[i-2],acc[i-1],cc[i-2].unwrap(),&rows[i-2],ones[i-2],&rows[i-1],ones[i-1],false));
                c.x(acc[i-1]);c.pop_condition();c.free_bit(bit);
            }else{erase(c,out,acc[i-1],&rows[i-1],ones[i-1],cc[i-1].unwrap());}
        }
    }true
}

#[cfg(test)]mod tests{
    use super::*;use crate::circuit::{analyze_ops,Op,OperationType};use crate::sim::Simulator;use sha3::digest::XofReader;
    struct Words{data:Vec<u8>,pos:usize}impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
    fn rng(words:&[u64])->Words{Words{data:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0}}
    fn draws(ops:&[Op])->usize{ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count()}
    fn put<R:XofReader>(s:&mut Simulator<'_,R>,q:QubitId,lane:usize,x:usize){if x&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}
    fn run(n:usize,pattern:usize,drop_count:usize,inverse:bool,probe:Option<usize>){
        let mut c=Builder::new();let source=c.alloc_qubits(n);let target=c.alloc_qubits(n);let ci=c.alloc_qubit();let shared=c.alloc_qubit();
        let interface:Vec<_>=source.iter().chain(target.iter()).copied().chain([ci,shared]).collect();c.declare_qubit_register(&interface);
        let rows:Vec<Vec<QubitId>>=(0..n).map(|i|match pattern{0=>vec![shared],1=>if i%3==0{vec![]}else{vec![source[i],shared]},2=>vec![source[i]],_=>if i==1||i==n-1{vec![]}else{vec![source[i]]}}).collect();
        let ones:Vec<_>=(0..n).map(|i|pattern==2&&i%3==1||pattern==3&&i==1).collect();let drops:Vec<_>=(0..drop_count).map(|i|2*i+1).collect();let active=c.active_qubits();
        let((),peak)=c.r3_peak(|c|{assert!(add(c,&target,&rows,&ones,ci,&drops));if inverse{c.x_all(&target);assert!(add(c,&target,&rows,&ones,ci,&drops));c.x_all(&target);}});
        assert_eq!(peak,active+(n-2-drop_count)as u32);let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());assert_eq!(nq as usize,interface.len()+n-2-drop_count);
        let copies=if inverse{2}else{1};assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),(n-1)*copies);let nr=draws(&ops);assert_eq!(nr,(n-2)*copies);
        let ranks:Vec<_>=drops.iter().map(|&j|if rows[j-1].is_empty()||rows[j].is_empty()||rows[j-1]==rows[j]{1usize}else{2}).collect();assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCZ).count(),ranks.iter().sum::<usize>()*copies);
        let starts:Vec<_>=if probe.is_some(){vec![0x6F3C0]}else{(0..1usize<<(2*n+2)).step_by(64).collect()};
        for start in starts{
            let words:Vec<_>=(0..nr).map(|j|match probe{Some(p)=>if p==j||p==nr{u64::MAX}else{0},None=>0xD1B54A32D192ED03u64.wrapping_mul((start+j+1)as u64).rotate_left(j as u32)}).collect();let mut random=rng(&words);
            let mut expected_t=(64*(n-1)*copies)as u64;for copy in 0..copies{for(j,&d)in drops.iter().enumerate(){let i=d+1;let ordinal=drop_count+(n-2-i)-drops.iter().filter(|&&x|x>i).count();expected_t+=ranks[j]as u64*words[copy*(n-2)+ordinal].count_ones()as u64;}}
            let mut s=Simulator::new(nq as usize,nb as usize,&mut random);for lane in 0..64{for(i,&q)in interface.iter().enumerate(){put(&mut s,q,lane,(start+lane)>>i);}}let original=s.qubits.clone();s.apply_iter(ops.iter());
            for lane in 0..64{let value=start+lane;let mut av=0usize;for(i,row)in rows.iter().enumerate(){let bit=row.iter().fold(usize::from(ones[i]),|x,q|x^(value>>interface.iter().position(|r|r==q).unwrap()&1));av|=bit<<i;}
                let bv=value>>n&((1<<n)-1);let wanted=if inverse{bv}else{(av+bv+(value>>(2*n)&1))&((1<<n)-1)};for i in 0..n{assert_eq!(s.qubits[target[i].0 as usize]>>lane&1,(wanted>>i&1)as u64,"n={n} pattern={pattern} drops={drop_count} inverse={inverse}");}}
            for i in 0..nq as usize{if !target.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);assert_eq!(s.stats.toffoli_gates as u64,expected_t);drop(s);assert_eq!(random.pos,nr*8);
        }
    }
    #[test]fn all_small_affine_parities_constants_and_multiple_drops(){for n in 5usize..=7{for pattern in 0..4{for count in 1..=(n-3)/2{run(n,pattern,count,false,None);}}}}
    #[test]fn every_physical_measurement_coefficient_and_inverse_on_sixty_four_bases(){for inverse in[false,true]{let nr=7*if inverse{2}else{1};for p in 0..nr+2{for pattern in 0..4{for count in 1..=3{run(9,pattern,count,inverse,Some(p));}}}}}
    #[test]fn invalid_alias_adjacent_or_over_budget_drop_rejected_before_emission(){let mut c=Builder::new();let a=c.alloc_qubits(7);let b=c.alloc_qubits(7);let ci=c.alloc_qubit();let op=c.op_count();let mut rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();assert!(!add(&mut c,&b,&rows,&[false;7],ci,&[1,2]));assert!(!add(&mut c,&b,&rows,&[false;7],ci,&[3,5]));rows[2]=vec![b[1]];assert!(!add(&mut c,&b,&rows,&[false;7],ci,&[1]));assert_eq!(op,c.op_count());}
}
