
#[cfg(test)]mod plan7_tests{
    use super::*;
    use crate::circuit::{analyze_ops,OperationType};
    use crate::sim::Simulator;
    use sha3::{Shake256,digest::{Update,ExtendableOutput,XofReader}};
    struct Words{data:Vec<u8>,pos:usize}
    impl XofReader for Words{fn read(&mut self,b:&mut[u8]){let end=self.pos+b.len();assert!(end<=self.data.len());b.copy_from_slice(&self.data[self.pos..end]);self.pos=end;}}
    fn rng(words:&[u64])->Words{Words{data:words.iter().flat_map(|w|w.to_le_bytes()).collect(),pos:0}}
    fn put<R:XofReader>(s:&mut Simulator<'_,R>,q:QubitId,lane:usize,bit:u64){if bit&1!=0{s.qubits[q.0 as usize]|=1u64<<lane;}}

    #[test]fn plan7_and_plan8_full_fifty_bit_affine_addition_and_phase(){
        let mut input_hash=Shake256::default();input_hash.update(b"exact-plan7-native-control-v1");let mut input=input_hash.finalize_xof();
        let cases:Vec<_>=(0..65536).map(|_|{let mut b=[0u8;24];input.read(&mut b);(u64::from_le_bytes(b[..8].try_into().unwrap()),u64::from_le_bytes(b[8..16].try_into().unwrap()),b[16]&1,b[17]&1)}).collect();
        for (plan,drops,wanted_peak)in[(Y28_PLAN8.0.to_vec(),Y28_PLAN8.1.to_vec(),8usize),(Y28_PLAN7.0.to_vec(),Y28_PLAN7.1.to_vec(),7usize)]{
            let mut b=Builder::new();let source=b.alloc_qubits(56);let target=b.alloc_qubits(56);let cin=b.alloc_qubit();let sign=b.alloc_qubit();
            let add:Vec<Lin>=source.iter().enumerate().map(|(i,&q)|{
                let mut v=l(q);if i%3==0{v=v.x(&l(sign));}if i%5==0{v=v.x(&Lin::k(true));}v
            }).collect();
            let active=b.active_qubits();let((),peak)=b.r3_peak(|b|ladder_drop(b,&target,&add,6,cin,&plan,&drops));
            assert_eq!(peak as usize,active as usize+wanted_peak);
            let ops=b.take_ops();let(nq,nb,_,_)=analyze_ops(ops.iter());
            let nr=ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).count();
            eprintln!("PLAN7_COMPONENT budget={wanted_peak} physical_peak={peak} ops={} rng={nr} emitted_ccx={}",ops.len(),ops.iter().filter(|o|o.kind==OperationType::CCX).count());
            for(first,chunk)in cases.chunks(64).enumerate(){
                let words:Vec<_>=(0..nr).map(|j|0xD1B54A32D192ED03u64.wrapping_mul((first+j+1)as u64).rotate_left((j%64)as u32)).collect();let mut random=rng(&words);
                let mut s=Simulator::new(nq as usize,nb as usize,&mut random);
                for(lane,&(a,t,c,sg))in chunk.iter().enumerate(){for i in 0..56{put(&mut s,source[i],lane,a>>i);put(&mut s,target[i],lane,t>>i);}put(&mut s,cin,lane,c as u64);put(&mut s,sign,lane,sg as u64);}
                let original=s.qubits.clone();s.apply_iter(ops.iter());
                for(lane,&(a,t,c,sg))in chunk.iter().enumerate(){let mut aa=0u64;for i in 6..56{let bit=(a>>i&1)^u64::from(i%3==0&&sg!=0)^u64::from(i%5==0);aa|=bit<<(i-6);}
                    let expected=(((t>>6)+aa+c as u64)&((1u64<<50)-1))<<6|(t&63);
                    for i in 0..56{assert_eq!(s.qubits[target[i].0 as usize]>>lane&1,expected>>i&1);}
                }
                for i in 0..nq as usize{if !target.iter().any(|q|q.0 as usize==i){assert_eq!(s.qubits[i],original[i]);}}assert_eq!(s.phase,0);
            }
        }
    }

    #[test]#[should_panic(expected="a dropped carry needs")]
    fn adjacent_drops_are_rejected_by_existing_contract(){
        let mut b=Builder::new();let a=b.alloc_qubits(56);let target=b.alloc_qubits(56);let cin=b.alloc_qubit();
        let terms:Vec<_>=a.iter().map(|&q|l(q)).collect();ladder_drop(&mut b,&target,&terms,6,cin,&Y28_PLAN7.0,&[0,1]);
    }
}
