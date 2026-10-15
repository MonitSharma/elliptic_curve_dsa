use quantum_ecc::circuit::{BitId,Op,OperationType as K,QubitId,RegisterId};
use quantum_ecc::sim::Simulator;
use sha3::digest::XofReader;
const N:u64=u64::MAX;
const OLD_B:usize=12;
const Q:usize=8;
#[derive(Clone)]struct Words{state:u64,reads:usize}
impl XofReader for Words{fn read(&mut self,out:&mut[u8]){assert_eq!(out.len(),8);self.state=self.state.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);out.copy_from_slice(&self.state.to_le_bytes());self.reads+=1;}}
fn op(k:K,a:u64,b:u64,t:u64,bt:u64,c:u64)->Op{Op{kind:k,q_control2:QubitId(a),q_control1:QubitId(b),q_target:QubitId(t),c_target:BitId(bt),c_condition:BitId(c),r_target:RegisterId(N)}}
fn push(c:u64)->Op{op(K::PushCondition,N,N,N,N,c)}
fn pop()->Op{op(K::PopCondition,N,N,N,N,N)}
fn classical(k:K,t:u64,c:u64)->Op{op(k,N,N,N,t,c)}
fn probes(out:&mut Vec<Op>,i:usize){
    let a=(i%Q)as u64;let b=((i+1)%Q)as u64;let t=((i+2)%Q)as u64;
    out.push(op(K::X,N,N,t,N,N));out.push(op(K::Z,N,N,a,N,N));
    out.push(op(K::CCX,a,b,t,N,((i+7)%OLD_B)as u64));
    out.push(op(K::Hmr,N,N,((i+4)%Q)as u64,((i+9)%OLD_B)as u64,N));
}
fn source(depth:usize,mode:usize)->Vec<Op>{
    let mut out=vec![];
    for i in 0..depth{
        let condition=(i%6)as u64;out.push(push(condition));
        // The already pushed mask is frozen even after its source bit changes.
        match mode%4{
            0=>out.push(classical(K::BitInvert,condition,N)),
            1=>out.push(classical(K::BitStore0,condition,N)),
            2=>out.push(classical(K::BitStore1,condition,((i+1)%6)as u64)),
            _=>out.push(op(K::Hmr,N,N,((i+3)%Q)as u64,condition,N)),
        }
        probes(&mut out,i);
    }
    for i in (0..depth).rev(){probes(&mut out,i+depth);out.push(pop());probes(&mut out,i+2*depth);}
    out
}
fn transform(original:&[Op],cut:usize,bad_restore:bool)->(Vec<Op>,usize){
    let count=original.iter().filter(|o|o.kind==K::PushCondition).count();
    let mut out=(0..count).map(|i|classical(K::BitStore0,(OLD_B+i)as u64,N)).collect::<Vec<_>>();
    let mut stack=vec![];let mut next=OLD_B;
    for (index,o) in original.iter().enumerate(){
        if index==cut{
            for _ in &stack{out.push(pop());}
            // Identity payload with two unconditional Toffolis measures whether
            // the temporary global scope was actually reached, even when false.
            out.push(op(K::CCX,0,1,2,N,N));out.push(op(K::CCX,0,1,2,N,N));
            for (snapshot,original_bit) in &stack{out.push(push(if bad_restore{*original_bit}else{*snapshot}));}
        }
        if o.kind==K::PushCondition{
            out.push(classical(K::BitStore1,next as u64,o.c_condition.0));
            stack.push((next as u64,o.c_condition.0));next+=1;
        }else if o.kind==K::PopCondition{assert!(stack.pop().is_some());}
        out.push(*o);
    }
    assert!(stack.is_empty());assert_eq!(next,OLD_B+count);
    for i in OLD_B..next{out.push(classical(K::BitStore0,i as u64,N));}
    (out,count)
}
fn main(){
    let mut cases=0u64;let mut negative_failures=0u64;let mut lane_checks=0u64;
    for depth in 1..=8{for mode in 0..4{
        let original=source(depth,mode);
        // Cut at every instruction boundary: guards, mutable bits and HMR all
        // occur on both sides. A valid static renderer must know exact depth.
        for cut in 0..original.len(){
            let (changed,extra)=transform(&original,cut,false);
            let (wrong,_)=transform(&original,cut,true);
            for seed in 0..32u64{
                let mut reader=Words{state:seed^0x1b5e8f3a7c9d2460,reads:0};
                let mut other=reader.clone();let mut negative=reader.clone();
                let mut left=Simulator::new(Q,OLD_B,&mut reader);
                let mut right=Simulator::new(Q,OLD_B+extra,&mut other);
                let mut bad=Simulator::new(Q,OLD_B+extra,&mut negative);
                // Packed independent lanes, arbitrary dirty qubits/classical.
                let mut state=seed.wrapping_add(0xb12ca9843d7e065f);
                for i in 0..Q{state=state.wrapping_mul(2862933555777941757).wrapping_add(3037000493);left.qubits[i]=state;right.qubits[i]=state;bad.qubits[i]=state;}
                for i in 0..OLD_B{state=state.rotate_left(13).wrapping_add(0x9e3779b97f4a7c15);left.bits[i]=state;right.bits[i]=state;bad.bits[i]=state;}
                for i in OLD_B..OLD_B+extra{right.bits[i]=N;bad.bits[i]=N;}
                left.apply_iter(original.iter());right.apply_iter(changed.iter());bad.apply_iter(wrong.iter());
                assert_eq!(left.qubits,right.qubits,"q depth={depth} mode={mode} cut={cut}");
                assert_eq!(left.bits,right.bits[..OLD_B],"b depth={depth} mode={mode} cut={cut}");
                assert_eq!(left.phase,right.phase,"phase depth={depth} mode={mode} cut={cut}");
                assert!(right.bits[OLD_B..].iter().all(|x|*x==0));
                assert_eq!(right.stats.toffoli_gates,left.stats.toffoli_gates+128);
                assert_eq!(right.stats.clifford_gates,left.stats.clifford_gates);
                let failed=left.qubits!=bad.qubits||left.bits!=bad.bits[..OLD_B]||left.phase!=bad.phase;
                negative_failures+=u64::from(failed);
                drop(left);drop(right);drop(bad);assert_eq!(reader.reads,other.reads);
                cases+=1;lane_checks+=64;
            }
        }
    }}
    assert!(negative_failures>0,"control restoring mutated original bits must fail");
    println!("{}",serde_json::json!({"status":"PROTECTED_GUARD_SNAPSHOT_RESTORATION_PASS","packed_cases":cases,"lane_cases":lane_checks,"negative_mutable_bit_failures":negative_failures,"depths":8,"all_cut_boundaries":true,"all_old_q_b_phase_and_rng_positions_equal":true,"private_bits_clean":true,"no_extra_qubits_or_mr":true,"identity_payload_toffolis_per_lane":2,"not_a_cache_certificate_or_candidate":true}));
}
