
#[cfg(test)]mod short_source_tests{
    use super::*;
    use crate::circuit::{analyze_ops,OperationType};
    use crate::sim::Simulator;
    use sha3::{Shake256,digest::{Update,ExtendableOutput}};
    #[test]fn exact_zero_extended_sources_with_optional_carries(){
        for w in 3usize..=6{for k in 1..=w{for with_cin in[false,true]{for with_cout in[false,true]{
            let n=w+usize::from(with_cout);let first=usize::from(!with_cin);
            let available:Vec<_>=(first..k.min(n-2)).collect();
            for indices in[vec![],available.iter().take(1).copied().collect(),available.clone()]{
                let mut c=Builder::new();let a=c.alloc_qubits(w);let low=c.alloc_qubits(w);let out=c.alloc_qubit();let ci=c.alloc_qubit();let shared=c.alloc_qubit();
                let mut target=low.clone();let mut terms:Vec<Vec<QubitId>>=(0..w).map(|i|if i>=k{Vec::new()}else if i%2==0{vec![a[i],shared]}else{vec![a[i]]}).collect();
                if with_cout{target.push(out);terms.push(Vec::new());}
                assert!(add(&mut c,&target,&terms,with_cin.then_some(ci),&indices));
                c.declare_qubit_register(&[out,ci,shared]);
                let ops=c.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());let mask=(1usize<<w)-1;
                assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),n-1+indices.len());
                for start in(0..1usize<<(2*w+3)).step_by(64){
                    let mut h=Shake256::default();h.update(b"zero-extended-source-bridge-v1");h.update(&start.to_le_bytes());let mut rng=h.finalize_xof();
                    let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);
                    for lane in 0..64{let value=start+lane;for i in 0..w{
                        if value>>i&1!=0{s.qubits[a[i].0 as usize]|=1u64<<lane;}
                        if value>>(w+i)&1!=0{s.qubits[low[i].0 as usize]|=1u64<<lane;}
                    }for(i,q)in[out,ci,shared].iter().enumerate(){if value>>(2*w+i)&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}}
                    let original=s.qubits.clone();s.apply_iter(ops.iter());
                    for lane in 0..64{let value=start+lane;let mut av=value&((1usize<<k)-1);
                        if value>>(2*w+2)&1!=0{for i in(0..k).step_by(2){av^=1<<i;}}
                        let sum=av+(value>>w&mask)+usize::from(with_cin)*(value>>(2*w+1)&1);
                        for i in 0..w{assert_eq!(s.qubits[low[i].0 as usize]>>lane&1,(sum>>i&1)as u64);}
                        let high=(value>>(2*w)&1)^if with_cout{sum>>w&1}else{0};assert_eq!(s.qubits[out.0 as usize]>>lane&1,high as u64);
                    }
                    for i in 0..nq as usize{if !target.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);
                }
            }
        }}}}
    }
}
