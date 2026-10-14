"""Append boundary/inactive tests to a newly generated isolated K32 candidate."""
from pathlib import Path
import sys

root=Path(sys.argv[1]); path=root/'src/point_add/tests_midg_k24.rs'
tests=r'''

#[test]
fn k32_partition_boundary_inactive_counter_inverse_phase() {
    let mut b=builder(); let ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let _ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),693);
    let mut r25=ring[..19].to_vec();r25.extend(&sx[1..6]);r25.push(ring[275]);
    let mut r32=r25.clone();r32.extend(&q[121..128]);
    let base=S1{r:r25.clone(),f:sx[0],zero:ring[18],sgn:sx[0],gt:vec![sx[0]],anc:vec![],andc:vec![],chain:vec![],dirty:dirty.clone()};
    let wide=S1{r:r32.clone(),..base.clone()};let win=ring[18..19+TC].to_vec();
    let f25=super::midg::stage1_v_compact_partitioned(&mut b,&ring[251..276],&win,&pool[..8],(65,256),&base,pool[12],true,&sy,false);
    let r25rec=super::midg::stage1_v_compact(&mut b,&ring[251..276],&win,&pool[..8],(65,256),&base,pool[12],false);
    let f32=super::midg::stage1_v_compact_partitioned(&mut b,&ring[244..276],&win,&pool[..8],(65,256),&wide,pool[12],true,&sy,true);
    let r32rec=super::midg::stage1_v_compact(&mut b,&ring[244..276],&win,&pool[..8],(65,256),&wide,pool[12],false);
    let record=rec(&mut b,|b|{b.x(ring[275]);b.play(&f25,false);b.play(&r25rec,true);b.play(&f32,false);b.play(&r32rec,true);b.x(ring[275]);});
    let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let mut rng=Rng::new(0x20261014_3298);let mut coefficients=0;
    for block in 0..4 {
        let mut input:Vec<_>=(0..693).map(|_|rng.next()).collect();input[sx[0].0 as usize]=0;input[pool[12].0 as usize]=0;
        for lane in 0..64 {let size=block*64+lane;put(&mut input,&sy,lane,N::from(size as u64));let active=(1..=128).contains(&size);if active{input[pool[12].0 as usize]|=1u64<<lane;for &id in &base.r{input[id.0 as usize]&=!(1u64<<lane);}input[ring[275].0 as usize]|=1u64<<lane;if size<=98{for &id in &q[121..128]{input[id.0 as usize]&=!(1u64<<lane);}}}put(&mut input,&pool[..8],lane,N::from([65usize,101,128,230,231,232,255,256][lane%8]as u64));}
        let mut expected=input.clone();
        for lane in 0..64 {let syvalue=block*64+lane;if !(1..=128).contains(&syvalue){continue;}let size=get(&input,&pool[..8],lane).as_limbs()[0]as usize;let k=if syvalue<=98{32}else{25};let divisor=get(&input,&ring[276-k..276],lane)|N::from(1u64);let dividend=(N::from(1u64)<<(256+k-size))-N::from(1u64);let f=dividend/divisor;let u=257usize.saturating_sub(size+TC);let top=N::from(1u64)<<(257-size);let delta=top-(((f>>u)+N::from(1u64))<<u);let mut w=N::ZERO;for i in 1..=TC{let pos=257isize-size as isize-i as isize;if pos>=0&&input[ring[18+i].0 as usize]>>lane&1!=0{w|=N::from(1u64)<<pos as usize;}}w=(w+delta)&(top-N::from(1u64));for i in 1..=TC{let pos=257isize-size as isize-i as isize;if pos>=0{let id=ring[18+i].0 as usize;expected[id]=(expected[id]&!(1u64<<lane))|((w.bit(pos as usize)as u64)<<lane);}}}
        let got=run(&forward,693,&|words|*words=input.clone());assert_eq!(got.q,expected,"full SY partition; inactive high aliases and counter loans");assert_eq!(got.phase,0);let(sym,n)=symbolic(&forward,input.clone());assert_eq!(sym,got.q);coefficients+=n;
        let back=run(&inverse,693,&|words|*words=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);let(sym,n)=symbolic(&inverse,got.q);assert_eq!(sym,input);coefficients+=n;
    }
    eprintln!("K32_PARTITION_PASS full_SY_words=256 active=1..128 inactive_high_aliases=true boundaries=98,99,128 all_wires=true inverse=true phase=0 independent_measurement_coefficients={coefficients} scope=V_partition_only");
}
'''
assert 'fn k32_partition_boundary' not in path.read_text()
path.write_text(path.read_text()+tests)
