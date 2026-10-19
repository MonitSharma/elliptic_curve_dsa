
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
    fn build(n:usize,indices:&[usize],with_phase:bool)->(Vec<Op>,Vec<QubitId>,Vec<QubitId>,QubitId,QubitId,Vec<usize>){
        let mut b=Builder::new();let a=b.alloc_qubits(n);let acc=b.alloc_qubits(n);let shared=b.alloc_qubit();let ci=b.alloc_qubit();let out=b.alloc_qubit();
        let terms:Vec<Vec<QubitId>>=a.iter().enumerate().map(|(i,&q)|if i%2==0{vec![shared,q]}else{vec![q]}).collect();
        let target:Vec<_>=(0..n).filter(|i|!indices.contains(i)).collect();
        let source:Vec<_>=target.iter().flat_map(|&i|terms[i].iter().copied()).collect();
        assert!(with_pause(&mut b,&acc,&terms,Some(ci),indices,&target,&source,&mut|b,carry|{
            // On the declared read set, original target/source and the
            // exposed carries must encode exactly those bits of the sum.
            let parity=|b:&mut Builder|{
                for &i in &target{
                    b.cx(acc[i],out);for &q in &terms[i]{b.cx(q,out);}
                    b.cx(carry[i].expect("Every protected position has a valid carry"),out);
                }
            };
            parity(b);if with_phase{b.z(out);}parity(b);
        }));
        (b.take_ops(),a,acc,shared,ci,target)
    }
    fn initial<R:XofReader>(s:&mut Simulator<'_,R>,a:&[QubitId],acc:&[QubitId],shared:QubitId,ci:QubitId,start:usize){
        let n=a.len();for lane in 0..64{let value=start+lane;for i in 0..n{put(s,a[i],lane,value>>i);put(s,acc[i],lane,value>>(n+i));}
            put(s,shared,lane,value>>(2*n));put(s,ci,lane,value>>(2*n+1));}
    }
    fn check<R:XofReader>(s:&Simulator<'_,R>,original:&[u64],a:&[QubitId],acc:&[QubitId],target:&[usize],start:usize,with_phase:bool){
        let n=a.len();let mask=(1usize<<n)-1;let mut expected_phase=0u64;
        for lane in 0..64{let value=start+lane;let mut aa=value&mask;let bb=(value>>n)&mask;
            if value>>(2*n)&1!=0{for i in(0..n).step_by(2){aa^=1<<i;}}
            let result=(aa+bb+(value>>(2*n+1)&1))&mask;
            for i in 0..n{assert_eq!(s.qubits[acc[i].0 as usize]>>lane&1,(result>>i&1)as u64);}
            if with_phase&&target.iter().fold(0,|p,&i|p^(result>>i&1))!=0{expected_phase|=1u64<<lane;}
        }
        for i in 0..s.qubits.len(){if !acc.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}
        assert_eq!(s.phase,expected_phase);
    }
    #[test]fn exhaustive_paused_views_and_intended_phase_on_small_inputs(){
        for n in 3usize..=7{
            let patterns=vec![vec![],(1..n-2).collect(),(1..n-2).step_by(2).collect()];
            for indices in patterns{
                let(ops,a,acc,shared,ci,target)=build(n,&indices,true);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=draws(&ops);
                assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),n-1+indices.len());
                assert_eq!(nq as usize,2*n+3+n-1-indices.len());
                for start in(0..(1usize<<(2*n+2))).step_by(64){
                    let words:Vec<_>=(0..nr).map(|j|0x9E3779B97F4A7C15u64.rotate_left((j%64)as u32)).collect();let mut random=rng(&words);
                    let mut s=Simulator::new(nq as usize,nb as usize,&mut random);initial(&mut s,&a,&acc,shared,ci,start);let original=s.qubits.clone();
                    s.apply_iter(ops.iter());check(&s,&original,&a,&acc,&target,start,true);
                }
            }
        }
    }
    #[test]fn every_rng_phase_coefficient_with_paused_parity_consumer(){
        let(ops,a,acc,shared,ci,target)=build(8,&[1,2,4],true);let(nq,nb,_,_)=analyze_ops(ops.iter());let nr=draws(&ops);
        assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::PushCondition|OperationType::PopCondition)));
        assert!(ops.iter().all(|o|o.c_condition==NO_BIT||matches!(o.kind,OperationType::Z|OperationType::CZ|OperationType::CCZ)));
        for probe in 0..nr+2{
            let mut words=vec![0;nr];if probe<nr{words[probe]=u64::MAX;}else if probe==nr{words.fill(u64::MAX);}
            let mut random=rng(&words);let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
            initial(&mut s,&a,&acc,shared,ci,0x13F80);let original=s.qubits.clone();s.apply_iter(ops.iter());
            check(&s,&original,&a,&acc,&target,0x13F80,true);drop(s);assert_eq!(random.pos,nr*8);
        }
    }
    #[test]fn callback_read_conflicts_reject_before_any_emission(){
        let mut b=Builder::new();let a=b.alloc_qubits(6);let acc=b.alloc_qubits(6);let ci=b.alloc_qubit();let terms:Vec<_>=a.iter().map(|&q|vec![q]).collect();
        let start=b.op_count();let mut called=false;
        assert!(!with_pause(&mut b,&acc,&terms,Some(ci),&[2],&[2],&[],&mut|_,_|{called=true;}));
        assert!(!with_pause(&mut b,&acc,&terms,Some(ci),&[2],&[],&[a[2]],&mut|_,_|{called=true;}));
        assert!(!called);assert_eq!(b.op_count(),start);
    }
}
