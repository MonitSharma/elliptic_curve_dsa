"""Native component tests for arbitrary-remainder inverse and borrowed K32.

No integrated allocation or width change. Copies the preserved compact source
into a clean research checkout and adds tests only within src/point_add.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys

compact,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in ['frogdrop.rs','midg.rs','tests_midg_k24.rs']:
    shutil.copyfile(compact/'src/point_add'/name,dest/'src/point_add'/name)
tests=r'''

#[test]
fn compact_dirty_remainder_partition_exhaustive_inverse_phase() {
    let mut total=0usize;let mut coefficients=0u64;
    for k in 2..=8 {
        let mut b=builder();let r=b.alloc_n(k);let d=b.alloc_n(k);let f=b.alloc();let dirty=b.alloc_n(259);
        let mut after=r.clone();let high=after.pop().unwrap();after.insert(0,high);
        let record=rec(&mut b,|b|{b.cx(r[k-1],f);b.cx(f,after[0]);super::frogdrop::cmp_csub_carries_vh1(b,&after[1..],&d[1..k-1],after[0],f);b.x(after[0]);b.cx(f,after[0]);b.cx(after[0],f);b.x(f);});
        let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);
        let cases:Vec<_>=(1usize<<(k-1)..1usize<<k).filter(|d|d&1==1).flat_map(|d|(0..1usize<<k).map(move |r|(d,r))).collect();
        let mut rng=Rng::new(0x20261014_3200+k as u64);
        for chunk in cases.chunks(64){
            let mut input=vec![0u64;b.width()as usize];for &qid in &dirty{input[qid.0 as usize]=rng.next();}
            for(lane,&(dv,rv))in chunk.iter().enumerate(){put(&mut input,&r,lane,N::from(rv as u64));put(&mut input,&d,lane,N::from(dv as u64));}
            let got=run(&forward,input.len(),&|q|*q=input.clone());let mask=if chunk.len()==64{u64::MAX}else{(1u64<<chunk.len())-1};assert_eq!(got.phase&mask,0);
            for(lane,&(dv,rv))in chunk.iter().enumerate(){let expected=if rv<dv{(2*rv+1)%dv}else{dv+(2*(rv-dv)+1)%((1usize<<k)-dv)};assert_eq!(get(&got.q,&after,lane),N::from(expected as u64));assert_eq!(get(&got.q,&d,lane),N::from(dv as u64));assert_eq!((got.q[f.0 as usize]>>lane)&1,0);}
            let back=run(&inverse,input.len(),&|q|*q=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase&mask,0);
            let(sym,n)=symbolic(&forward,input.clone());assert_eq!(sym,got.q);coefficients+=n;
            let(sym,n)=symbolic(&inverse,got.q);assert_eq!(sym,input);coefficients+=n;
            total+=chunk.len();
        }
    }
    eprintln!("DIRTY_RESTORING_PARTITION_PASS cases={total} independent_measurement_coefficients={coefficients} widths=2..8 arbitrary_R=true inverse=true");
}

#[test]
fn compact_k32_borrowed_q_counter_lanes_inactive_dirty_phase() {
    let mut b=builder();let ring=b.alloc_n(276);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let _ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),693);
    let mut remainder=ring[..19].to_vec();remainder.extend(&sx[1..6]);remainder.push(ring[275]);remainder.extend(&q[121..128]);assert_eq!(remainder.len(),32);
    let s=S1{r:remainder.clone(),f:sx[0],zero:ring[18],sgn:sx[0],gt:vec![sx[0]],anc:vec![],andc:vec![],chain:vec![],dirty:dirty.clone()};
    let fv=super::midg::stage1_v_compact(&mut b,&ring[244..276],&ring[18..19+TC],&pool[..8],(65,256),&s,pool[12],true);
    let fr=super::midg::stage1_v_compact(&mut b,&ring[244..276],&ring[18..19+TC],&pool[..8],(65,256),&s,pool[12],false);
    let record=rec(&mut b,|b|{b.x(ring[275]);b.play(&fv,false);b.play(&fr,true);b.x(ring[275]);});
    let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let mut rng=Rng::new(0x20261014_32cafe);let mut coefficients=0u64;
    for mode in 0..4 {
        let active=[u64::MAX,0,0xa55a_c33c_0ff0_f00f,0x00ff_0f0f_3333_5555][mode];let mut input:Vec<_>=(0..693).map(|_|rng.next()).collect();input[pool[12].0 as usize]=active;input[sx[0].0 as usize]=0;
        for &qid in &remainder{input[qid.0 as usize]&=!active;}input[ring[275].0 as usize]|=active;
        for lane in 0..64 {let size=[65usize,101,128,133,230,231,232,255,256][lane%9];put(&mut input,&pool[..8],lane,N::from(size as u64));put(&mut input,&sy,lane,N::from(1+(lane%98)as u64));}
        let mut expected=input.clone();
        for lane in 0..64 {if active>>lane&1==0{continue;}let size=get(&input,&pool[..8],lane).as_limbs()[0]as usize;let divisor=get(&input,&ring[244..276],lane)|N::from(1u64);let dividend=(N::from(1u64)<<(288-size))-N::from(1u64);let f=dividend/divisor;let u=257usize.saturating_sub(size+TC);let top=N::from(1u64)<<(257-size);let delta=top-(((f>>u)+N::from(1u64))<<u);let mut w=N::ZERO;
            for i in 1..=TC {let pos=257isize-size as isize-i as isize;if pos>=0&&input[ring[18+i].0 as usize]>>lane&1!=0{w|=N::from(1u64)<<pos as usize;}}
            w=(w+delta)&(top-N::from(1u64));for i in 1..=TC{let pos=257isize-size as isize-i as isize;if pos>=0{let id=ring[18+i].0 as usize;expected[id]=(expected[id]&!(1u64<<lane))|((w.bit(pos as usize)as u64)<<lane);}}
        }
        let got=run(&forward,693,&|words|*words=input.clone());assert_eq!(got.phase,0);assert_eq!(got.q,expected,"active arithmetic; inactive arbitrary remainder, Q counter loans and passengers restore");
        let(sym,n)=symbolic(&forward,input.clone());assert_eq!(sym,got.q);coefficients+=n;
        let back=run(&inverse,693,&|words|*words=got.q.clone());assert_eq!(back.phase,0);assert_eq!(back.q,input);
        let(sym,n)=symbolic(&inverse,got.q);assert_eq!(sym,input);coefficients+=n;
    }
    eprintln!("K32_DIRTY_COUNTER_COMPONENT_PASS cases=256 width=693 borrowed_Q_indices=121..127 inactive_arbitrary_R=true independent_measurement_coefficients={coefficients} inverse=true scope=V_only_no_integrated_loan_proof");
}
'''
path=dest/'src/point_add/tests_midg_k24.rs';path.write_text(path.read_text()+tests)
print(json.dumps({'scope':'Component-only arbitrary remainder/K32 borrowed-Q phase tests; no integrated loan claim',
                  'base_revision':subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),
                  'source_sha256':{f'src/point_add/{f}':hashlib.sha256(dest.joinpath('src/point_add',f).read_bytes()).hexdigest() for f in ['frogdrop.rs','midg.rs','tests_midg_k24.rs']}},indent=2))
