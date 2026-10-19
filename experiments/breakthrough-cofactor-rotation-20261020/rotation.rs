
/// Three controlled reflections, as in leapfrog::rot4. left=true sends
/// old bit i to i+k1+2*k2; no approximation or skipped rotation is allowed.
fn rotate_four(c:&mut Builder,word:&[QubitId],k1:QubitId,k2:QubitId,left:bool){
    let n=word.len();let order=if left{[2usize,1,0]}else{[0,1,2]};
    for stage in order{
        let anchor=[1isize,0,-2][stage];
        if stage==1{c.cx(k1,k2);}
        let control=if stage==0{k1}else{k2};
        for i in 0..n{
            let j=(anchor-i as isize).rem_euclid(n as isize)as usize;
            if i<j{fredkin(c,control,word[i],word[j]);}
        }
        if stage==1{c.cx(k1,k2);}
    }
}

#[cfg(test)]mod reflection_tests{
    use super::*;
    use crate::circuit::{analyze_ops,OperationType};
    use crate::sim::Simulator;
    use sha3::{Shake256,digest::{Update,ExtendableOutput}};

    #[test]fn full_small_word_truth_tables_and_inverse(){
        for n in 3usize..=10{
            let mut b=Builder::new();let word=b.alloc_qubits(n);let k=b.alloc_qubits(2);
            rotate_four(&mut b,&word,k[0],k[1],true);let split=b.op_count();
            rotate_four(&mut b,&word,k[0],k[1],false);
            let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());
            assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)));
            let mask=(1u64<<n)-1;
            for first in(0..(4usize<<n)).step_by(64){
                let mut h=Shake256::default();h.update(b"cofactor-reflection-truth-v1");let mut rng=h.finalize_xof();
                let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);
                for lane in 0..64{let value=first+lane;if value>=4usize<<n{continue;}
                    for i in 0..n{if value>>i&1!=0{s.qubits[word[i].0 as usize]|=1u64<<lane;}}
                    for i in 0..2{if value>>(n+i)&1!=0{s.qubits[k[i].0 as usize]|=1u64<<lane;}}
                }
                let original=s.qubits.clone();s.apply_iter(ops[..split].iter());
                for lane in 0..64{let value=first+lane;if value>=4usize<<n{continue;}
                    let bits=value as u64&mask;let e=(value>>n)%n;
                    let expected=((bits<<e)|(bits>>(n-e)))&mask;
                    for i in 0..n{assert_eq!(s.qubits[word[i].0 as usize]>>lane&1,expected>>i&1);}
                }
                for &q in &k{assert_eq!(s.qubits[q.0 as usize],original[q.0 as usize]);}
                s.apply_iter(ops[split..].iter());assert_eq!(s.qubits,original);assert_eq!(s.phase,0);
            }
        }
    }

    #[test]fn component_gate_formula_for_every_width_nine_through_forty(){
        for n in 9usize..=40{
            let mut b=Builder::new();let a=b.alloc_qubits(n);let d=b.alloc_qubits(n);
            let f:[QubitId;5]=b.alloc_qubits(5).try_into().unwrap();
            update(&mut b,&a,&d,&f);let split=b.op_count();restore(&mut b,&a,&d,&f);
            let ops=b.take_ops();let rotations=if n%2==0{3*n/2-2}else{3*(n-1)/2};
            let expected=3*(n-1)+rotations+19;
            assert_eq!(ops[..split].iter().filter(|o|o.kind==OperationType::CCX).count(),expected);
            assert_eq!(ops[split..].iter().filter(|o|o.kind==OperationType::CCX).count(),expected);
        }
    }
}
