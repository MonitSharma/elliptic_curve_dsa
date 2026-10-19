//! Reversible low-bit codec for the integer adjoint-cofactor interface.
//! Component only: not integrated into point addition or a width claim.
use super::builder::Builder;
use crate::circuit::QubitId;

/// XOR one of four quantum data bits into target, preserving every source.
/// Five Toffolis, three clean work bits; no measurement or reset.
fn query4(c: &mut Builder, bits: [QubitId;4], address: [QubitId;2], target: QubitId) {
    let w=c.alloc_qubits(3);
    let branch=|c:&mut Builder,a:QubitId,b:QubitId,out:QubitId|{
        c.cx(a,out);
        c.cx(a,w[2]);c.cx(b,w[2]);
        c.ccx(address[0],w[2],out);
        c.cx(b,w[2]);c.cx(a,w[2]);
    };
    branch(c,bits[0],bits[1],w[0]);
    branch(c,bits[2],bits[3],w[1]);
    c.cx(w[0],target);
    c.cx(w[0],w[2]);c.cx(w[1],w[2]);
    c.ccx(address[1],w[2],target);
    c.cx(w[1],w[2]);c.cx(w[0],w[2]);
    // Reverse the branches (CX and CCX are self-inverse).
    for (a,b,out) in [(bits[2],bits[3],w[1]),(bits[0],bits[1],w[0])] {
        c.cx(a,w[2]);c.cx(b,w[2]);
        c.ccx(address[0],w[2],out);
        c.cx(b,w[2]);c.cx(a,w[2]);
        c.cx(a,out);
    }
    for q in w.into_iter().rev(){c.release_clean(q);}
}

/// Erase (s0,s1,k1,k2) on the admitted integer interface, retaining s3.
/// Cnew=C+q*D, Dnew=2^e*D, C divisible8, D odd,
/// q=7-2s0-4s1-8s3, e=3+k1+2k2.
/// All sources survive. Exactly14 Toffolis, at most3 clean work bits.
/// The first macro-step and a different tail require their own interfaces.
pub(super) fn erase_history(c:&mut Builder, new_c:&[QubitId], new_d:&[QubitId],
                 s0:QubitId,s1:QubitId,k1:QubitId,k2:QubitId) {
    assert!(new_c.len()>=3&&new_d.len()>=9);
    query4(c,[new_d[4],new_d[5],new_d[6],new_d[7]],[k1,k2],s0);
    c.cx(new_c[1],s0);c.x(s0);
    query4(c,[new_d[5],new_d[6],new_d[7],new_d[8]],[k1,k2],s1);
    c.cx(new_c[2],s1);c.x(s1);
    let (a,b,d)=(new_d[3],new_d[4],new_d[5]);
    c.x(a);c.x(b);
    c.ccx(a,b,k2);
    let u=c.alloc_qubit();
    c.ccx(b,d,u);c.x(u);
    c.ccx(a,u,k1);
    c.x(u);c.ccx(b,d,u);
    c.release_clean(u);
    c.x(b);c.x(a);
}

#[cfg(test)] mod tests {
    use super::*;
    use crate::circuit::{analyze_ops,OperationType};
    use crate::sim::Simulator;
    use sha3::{Shake256,digest::{Update,ExtendableOutput}};
    fn reader()->sha3::Shake256Reader {let mut x=Shake256::default();x.update(b"cofactor-history-codec-native-controls-v1");x.finalize_xof()}
    fn put<R:sha3::digest::XofReader>(s:&mut Simulator<'_,R>,q:QubitId,lane:usize,value:bool){if value{s.qubits[q.0 as usize]|=1u64<<lane;}}

    #[test] fn quantum_data_query_all_addresses_old_targets_and_data(){
        let mut b=Builder::new();let d=b.alloc_qubits(4);let a=b.alloc_qubits(2);let t=b.alloc_qubit();
        query4(&mut b,d.clone().try_into().unwrap(),a.clone().try_into().unwrap(),t);
        let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());
        assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),5);
        for group in 0..2{
            let mut rng=reader();let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);
            for lane in 0..64{let case=group*64+lane;let data=case&15;let addr=(case>>4)&3;let old=case>>6;
                for i in 0..4{put(&mut s,d[i],lane,data>>i&1!=0);}for i in 0..2{put(&mut s,a[i],lane,addr>>i&1!=0);}put(&mut s,t,lane,old!=0);}
            let original=s.qubits.clone();s.apply_iter(ops.iter());
            for lane in 0..64{let case=group*64+lane;let data=case&15;let addr=(case>>4)&3;let old=case>>6;assert_eq!((s.qubits[t.0 as usize]>>lane)&1,(old^((data>>addr)&1))as u64);}
            for i in 0..nq as usize{if i!=t.0 as usize{assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);
        }
    }

    #[test] fn integer_interface_all_low_residues_clean_and_exact_inverse(){
        let mut b=Builder::new();let c=b.alloc_qubits(3);let d=b.alloc_qubits(9);let flags=b.alloc_qubits(4);let spectator=b.alloc_qubits(3);
        erase_history(&mut b,&c,&d,flags[0],flags[1],flags[2],flags[3]);
        let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());
        assert_eq!(ops.iter().filter(|o|o.kind==OperationType::CCX).count(),14);
        assert!(!ops.iter().any(|o|matches!(o.kind,OperationType::R|OperationType::Hmr|OperationType::Z|OperationType::CZ|OperationType::CCZ)));
        let mut cases=Vec::new();
        for old_d in (-31i64..32).step_by(2){for e in 3..7{for base in [-16i64,0,16]{for word in 0..8{
            let s0=word&1;let s1=(word>>1)&1;let s3=(word>>2)&1;let q=7-2*s0-4*s1-8*s3;
            cases.push((base+q*old_d,old_d<<e,[s0,s1,(e-3)&1,(e-3)>>1],word));
        }}}}
        assert_eq!(cases.len(),3072);
        for chunk in cases.chunks(64){let mut rng=reader();let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);
            for(lane,(cv,dv,fv,word))in chunk.iter().enumerate(){for i in 0..3{put(&mut s,c[i],lane,cv>>i&1!=0);put(&mut s,spectator[i],lane,word>>i&1!=0);}for i in 0..9{put(&mut s,d[i],lane,dv>>i&1!=0);}for i in 0..4{put(&mut s,flags[i],lane,fv[i]!=0);}}
            let original=s.qubits.clone();s.apply_iter(ops.iter());
            for i in 0..nq as usize{if flags.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],0);}else{assert_eq!(s.qubits[i],original[i]);}}
            assert_eq!(s.phase,0);
            s.apply_iter(ops.iter().rev());assert_eq!(s.qubits,original);assert_eq!(s.phase,0);
        }
    }

    #[test] fn incorrect_history_is_preserved_as_a_dirty_flag(){
        let mut b=Builder::new();let c=b.alloc_qubits(3);let d=b.alloc_qubits(9);let f=b.alloc_qubits(4);
        erase_history(&mut b,&c,&d,f[0],f[1],f[2],f[3]);let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());
        let mut rng=reader();let mut s=Simulator::new(nq as usize,nb as usize,&mut rng);
        // C=0,D=1,s0=s1=s3=0,e=3 gives Cnew=7,Dnew=8. Flip only the stored s0.
        for q in c{put(&mut s,q,0,true);}put(&mut s,d[3],0,true);put(&mut s,f[0],0,true);
        s.apply_iter(ops.iter());assert_eq!(s.qubits[f[0].0 as usize]&1,1);assert_eq!(s.phase,0);
    }
}

/// Global inverse of the history eraser: recover address flags before queries.
pub(super) fn restore_history(c:&mut Builder,new_c:&[QubitId],new_d:&[QubitId],
    s0:QubitId,s1:QubitId,k1:QubitId,k2:QubitId){
    let(a,b,d)=(new_d[3],new_d[4],new_d[5]);c.x(a);c.x(b);c.ccx(a,b,k2);
    let u=c.alloc_qubit();c.ccx(b,d,u);c.x(u);c.ccx(a,u,k1);c.x(u);c.ccx(b,d,u);c.release_clean(u);c.x(b);c.x(a);
    query4(c,[new_d[4],new_d[5],new_d[6],new_d[7]],[k1,k2],s0);c.cx(new_c[1],s0);c.x(s0);
    query4(c,[new_d[5],new_d[6],new_d[7],new_d[8]],[k1,k2],s1);c.cx(new_c[2],s1);c.x(s1);
}
