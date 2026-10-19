
#[cfg(test)]mod carryout_tests{
    use super::*;
    use crate::circuit::{analyze_ops,OperationType};
    use crate::sim::Simulator;
    use sha3::{Shake256,digest::{Update,ExtendableOutput}};
    #[test]fn parity_bridge_preserves_arbitrary_carryout_target(){
        for w in 3usize..=6{
            for borrowed in[0,1,w-1]{
                let mut b=Builder::new();let a=b.alloc_qubits(w);let low=b.alloc_qubits(w);let high=b.alloc_qubit();let ci=b.alloc_qubit();let shared=b.alloc_qubit();
                let mut target=low.clone();target.push(high);
                let mut terms:Vec<_>=a.iter().enumerate().map(|(i,&q)|if i%2==0{vec![shared,q]}else{vec![q]}).collect();terms.push(Vec::new());
                let indices:Vec<_>=(0..borrowed).collect();assert!(add(&mut b,&target,&terms,Some(ci),&indices));
                let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());let mask=(1usize<<w)-1;
                assert!(ops.iter().any(|o|o.kind==OperationType::CCX));
                for first in(0..1usize<<(2*w+3)).step_by(64){
                    let mut h=Shake256::default();h.update(b"carryout-extension-native-v1");h.update(&first.to_le_bytes());let mut rng=h.finalize_xof();
                    let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);
                    for lane in 0..64{let value=first+lane;for i in 0..w{
                        if value>>i&1!=0{s.qubits[a[i].0 as usize]|=1u64<<lane;}
                        if value>>(w+i)&1!=0{s.qubits[low[i].0 as usize]|=1u64<<lane;}
                    }
                        for(i,q)in[high,ci,shared].iter().enumerate(){if value>>(2*w+i)&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}
                    }
                    let original=s.qubits.clone();s.apply_iter(ops.iter());
                    for lane in 0..64{let value=first+lane;let mut av=value&mask;
                        if value>>(2*w+2)&1!=0{for i in(0..w).step_by(2){av^=1<<i;}}
                        let sum=av+(value>>w&mask)+(value>>(2*w+1)&1);
                        for i in 0..w{assert_eq!(s.qubits[low[i].0 as usize]>>lane&1,(sum>>i&1)as u64);}
                        assert_eq!(s.qubits[high.0 as usize]>>lane&1,((value>>(2*w)&1)^(sum>>w&1))as u64);
                    }
                    for i in 0..nq as usize{if !target.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);
                }
            }
        }
    }
}
