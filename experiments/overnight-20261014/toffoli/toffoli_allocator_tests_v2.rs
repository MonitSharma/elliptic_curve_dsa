//! Whole-body allocator interface equality; no resource record claim.
use super::*;
use crate::circuit::{Op,analyze_ops};
use crate::sim::Simulator;
use alloy_primitives::U256;
use crate::point_add::SECP256K1_P;
use sha3::digest::XofReader;
type Pool=(Vec<u32>,Vec<u32>,u32);
fn fixture(room:usize,t:usize,on:bool,bank:bool)->(Pool,u32,Vec<Op>,Vec<QubitId>,Vec<QubitId>,Vec<QubitId>,Vec<QubitId>) {
    let mut c=Builder::new();
    let b=c.alloc_qubits(N);let tg=c.alloc_qubits(N);let letter=c.alloc_qubits(5);
    let pads=c.alloc_qubits(cells::cap()-(2*N+5+room));
    let pool=c.alloc_qubits(room);for q in pool {c.release_clean(q);}
    let active=c.active_qubits();
    let (_,proxy)=proxy_fold(steps()[t][0],false);let shift=cmp_shift_at(t);
    let (_,peak)=c.r3_peak(|c|toffoli_bank_loan::with_bank_switch(bank,||toffoli_bank_loan::with_recipe(on,||
        cells::with_tie(None,||cells::with_cmp_shift((shift.0+Y15_CMP_EXTRA+super::n2_cmpx(),shift.1),||
            cells::with_bridge(proxy,false,||body_capped(c,t,[letter[0],letter[1],letter[2]],letter[3],letter[4],&b,&tg,proxy,false)))))));
    assert_eq!(c.active_qubits(),active);
    for _ in 0..3 {rot1(&mut c,&tg,true);}rot4(&mut c,letter[3],letter[4],&tg,false);
    (c.y42_alloc_state(),peak,c.take_ops(),b,tg,letter,pads)
}
#[test]
fn toffoli_allocator_exact_body_boundaries_v2() {
    for room in [90,100,120,160,240] {
        for t in [30,60,85,90,100,110,120,127,128,137,145] {
            let old=fixture(room,t,false,false);let bank=fixture(room,t,true,true);
            assert_eq!(old.0,bank.0,"allocator room={room} tick={t}");
            eprintln!("TOFFOLI_ALLOCATOR_EQUAL room={room} tick={t} hash={} old_peak={} new_peak={}",Builder::y42_alloc_hash(&old.0),old.1,bank.1);
        }
    }
}

#[test]
fn toffoli_allocator_disabled_bank_stream_exact_v2() {
    for room in [90,100,120,160,240] {
        for t in [30,60,85,90,100,110,120,127,128,137,145] {
            let old=fixture(room,t,false,false);let fork=fixture(room,t,true,false);
            assert_eq!(old.0,fork.0);assert_eq!(old.2,fork.2,"fork changes gates room={room} tick={t}");
        }
    }
}

struct RandomWords(u64);
impl XofReader for RandomWords {fn read(&mut self,out:&mut[u8]) {assert_eq!(out.len(),8);self.0^=self.0<<13;self.0^=self.0>>7;self.0^=self.0<<17;out.copy_from_slice(&self.0.to_le_bytes());}}
fn expected(t:U256,s:U256,letter:u8)->U256 {
    let mut x=t;
    for i in 0..3 {
        let a=s.mul_mod(U256::from(1u64<<i),SECP256K1_P);
        x=if letter>>i&1==0 {x.add_mod(a,SECP256K1_P)} else {crate::weierstrass_elliptic_curve::sub_mod(x,a,SECP256K1_P)};
    }
    for _ in 0..3+((letter>>3)&3) {
        x=if x.as_limbs()[0]&1!=0 {(x>>1)+(SECP256K1_P>>1)+U256::from(1)} else {x>>1};
    }
    x
}
fn put<R:XofReader>(sim:&mut Simulator<R>,register:&[QubitId],value:U256,shot:usize) {
    for (i,&q) in register.iter().enumerate() {*sim.qubit_mut(q)|=(value.as_limbs()[i/64]>>(i%64)&1)<<shot;}
}
fn get<R:XofReader>(sim:&Simulator<R>,register:&[QubitId],shot:usize)->U256 {
    let mut words=[0u64;4];for (i,&q) in register.iter().enumerate() {words[i/64]|=(sim.qubit(q)>>shot&1)<<(i%64);}U256::from_limbs(words)
}

#[test]
fn toffoli_allocator_native_payload_pair_extended_domain_v2() {
    let mut random=RandomWords(0xC0FE_F00D_9384_7671);let mut pairs=vec![(U256::ZERO,U256::ZERO),(U256::from(1),U256::ZERO),(U256::ZERO,U256::from(1)),(SECP256K1_P-U256::from(1),SECP256K1_P-U256::from(1))];
    for _ in 0..12 {
        let mut raw=[0u8;8];let mut t=[0;4];let mut s=[0;4];
        for w in t.iter_mut().chain(s.iter_mut()) {random.read(&mut raw);*w=u64::from_le_bytes(raw);}
        pairs.push((U256::from_limbs(t)%SECP256K1_P,U256::from_limbs(s)%SECP256K1_P));
    }
    for room in [90,100,120,160,240] {for tick in [30,60,85,90,100,110,120,127,128,137,145] {
    let mut baseline_outputs=None;let mut baseline_phase=0;
    for on in [false,true] {
        let (_,_,ops,b,tg,letter,pads)=fixture(room,tick,on,on);
        let (nq,nb,_,_)=analyze_ops(ops.iter());let mut words=RandomWords(0xBADD_C0DE_7324_9831);let mut sim=Simulator::new(nq as usize,nb as usize,&mut words);
        let mut phase_bad=0;let mut reference_bad=0;let mut outputs=Vec::new();
        for chunk in pairs.chunks(2) {
            sim.clear_for_shot();
            for shot in 0..64 {
                let (t,s)=chunk[shot/32];put(&mut sim,&tg,t,shot);put(&mut sim,&b,s,shot);
                for (i,&q) in letter.iter().enumerate() {*sim.qubit_mut(q)|=((shot as u64>>i)&1)<<shot;}
            }
            for &q in &pads {*sim.qubit_mut(q)=0xA55A_F00F_1234_5678;}
            sim.apply_iter(ops.iter());phase_bad+=sim.phase.count_ones();
            for shot in 0..64 {
                let (t,s)=chunk[shot/32];let got=get(&sim,&tg,shot)%SECP256K1_P;let want=expected(t,s,(shot%32) as u8);
                outputs.push(got);
                if got!=want {
                    reference_bad+=1;
                    if reference_bad<=2 {eprintln!("TOFFOLI_EXTENDED_DOMAIN_REFERENCE room={room} tick={tick} bank={on} T={t} S={s} letter={} expected={want} actual={got} producer_admission=unproved",shot%32);}
                }
                assert_eq!(get(&sim,&b,shot),s,"source passenger");
                for (i,&q) in letter.iter().enumerate() {assert_eq!(sim.qubit(q)>>shot&1,(shot as u64>>i)&1);}
            }
            for &q in &pads {assert_eq!(sim.qubit(q),0xA55A_F00F_1234_5678);}
            for &q in b.iter().chain(tg.iter()).chain(letter.iter()).chain(pads.iter()) {*sim.qubit_mut(q)=0;}
            assert!(sim.qubits.iter().all(|&x|x==0),"payload scratch room={room} tick={tick} bank={on}");
        }
        if on {assert_eq!(baseline_outputs.as_ref().unwrap(),&outputs,"paired payload values room={room} tick={tick}");if baseline_phase==0 {assert_eq!(phase_bad,0,"new sampled phase failures room={room} tick={tick}");}}
        else {baseline_outputs=Some(outputs);baseline_phase=phase_bad;}
        eprintln!("TOFFOLI_ALLOCATOR_NATIVE room={room} tick={tick} bank={on} cases=512 reference_bad={reference_bad} phase_bad={phase_bad} independent_measurement_words=yes producer_admission=unproved");
    }}}
}
