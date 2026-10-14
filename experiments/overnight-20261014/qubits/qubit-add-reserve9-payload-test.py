"""Exact payload oracle from unchanged tests_frogdrop::pl_model/pre/off.

The native test admits real dy-derived payload states and does not assume
that zero input leaves zero intermediate offset payload.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]);path=root/'src/point_add/tests_midg_k24.rs'
test=r'''

#[test]
fn reserve9_crossing_payload_3713_exact_shadow_native(){
    use super::frogdrop_col::{Fd,ColScr,column_pl};
    let p=super::frogdrop_sched::p();let dx=N::from_str_radix("dbc03838c8e3ef33e7b222ced5415f372fbdf32febb8ead3f55c4e58c4f81f55",16).unwrap();let(mut r,mut t)=(vec![p,dx],vec![N::ZERO,N::from(1u64)]);while !r[r.len()-1].is_zero(){let n=r.len();let q=r[n-2]/r[n-1];r.push(r[n-2]-q*r[n-1]);t.push(t[n-2]+q*t[n-1]);}
    let j=60;let mut b=builder();let ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let payload=b.alloc_n(259);assert_eq!(b.width(),693);let rev:Vec<_>=ring.iter().rev().copied().collect();let mut fd=Fd{ring:ring.clone(),q:q.clone(),sy:sy.clone(),sx:sx.clone(),ph,cnt:q[121..].to_vec()};let(cols,_,_)=super::pointadd_frogdrop::col_pars(&super::frogdrop_sched::from_text(super::pointadd_frogdrop::SCHED_FROGDROP));let cp=&cols[60];assert!(cp.psw&&cp.ht);let sc=ColScr::carve_col(&pool,&sx,&payload,24,23,40,cp.sz.1>255);let pl=super::pointadd_frogdrop::pl_col(&payload,&fd,&pool);
    let record=rec(&mut b,|b|column_pl(b,&mut fd,cp,&sc,Some(&pl)));let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);
    for seed in 0..4 {
        let mut input=vec![0u64;693];let mut expected=vec![0u64;693];let mut rng=Rng::new(0x20261014_371300+seed);
        for lane in 0..64 {let dy=match lane{0=>N::ZERO,1=>N::from(1u64),2=>p-N::from(1u64),_=>rng.below(256)%p};let(mut d,mut w)=(dy,N::ZERO);for k in 1..j{let e=d/r[k];d-=e*r[k];let wpost=w.wrapping_add(e.wrapping_mul(t[k]));w=(r[k-1]/r[k]).wrapping_mul(t[k]).wrapping_add(!wpost);}
            let e=d/r[j];let dnext=d-e*r[j];let wpost=w.wrapping_add(e.wrapping_mul(t[j]));let wnext=(r[j-1]/r[j]).wrapping_mul(t[j]).wrapping_add(!wpost);let br=r[j].bit_len();let pre_boundary=258-t[j].bit_len();let off=wnext.wrapping_add(N::from(1u64)<<(258-br));
            for l in 0..259{let ib=if l<pre_boundary{d.bit(l)}else{w.bit(258-l)};let ob=if l<br{dnext.bit(l)}else{off.bit(258-l)};if ib{input[payload[l].0 as usize]|=1u64<<lane;}if ob{expected[payload[l].0 as usize]|=1u64<<lane;}}
            put(&mut input,&ring,lane,t[j]);put(&mut input,&rev[..r[j-1].bit_len()],lane,r[j-1]);put(&mut input,&q,lane,r[j]);put(&mut input,&sy,lane,N::from(r[j-1].bit_len()as u64));input[ph.0 as usize]|=1u64<<lane;
            put(&mut expected,&ring,lane,t[j+1]);put(&mut expected,&rev[..r[j+1].bit_len()],lane,r[j+1]);put(&mut expected,&q,lane,r[j]);put(&mut expected,&sx,lane,N::from(r[j+1].bit_len()as u64));expected[ph.0 as usize]|=1u64<<lane;
        }
        let got=run(&forward,693,&|words|*words=input.clone());let bad:Vec<_>=got.q.iter().zip(&expected).enumerate().filter_map(|(i,(a,z))|if a!=z{Some(i)}else{None}).collect();assert!(bad.is_empty(),"exact payload+Euclid+scratch seed{seed}; mismatching_wires={bad:?}");assert_eq!(got.phase,0,"native sampled forwardphase seed{seed}");let back=run(&inverse,693,&|words|*words=got.q.clone());assert_eq!(back.q,input,"all-wire inverse seed{seed}");assert_eq!(back.phase,0,"native sampled inversephase seed{seed}");eprintln!("RESERVE9_PAYLOAD_CASE_PASS seed={seed} lanes=64 dy=0,1,p-1,varied exact_pre_and_offset_oracle=true all_wires_inverse=true native_phase=0 measurement_coefficients=UNASSESSED");
    }
    eprintln!("RESERVE9_PAYLOAD_COMPONENT_PASS width=693 column=60 euclid_step=60 first_HT_refill=true quotient=375614 reserve=9 cases=256 scope=one_full_column_with_admitted_payload");
}
'''
assert 'fn reserve9_crossing_payload_3713' not in path.read_text();path.write_text(path.read_text()+test)
