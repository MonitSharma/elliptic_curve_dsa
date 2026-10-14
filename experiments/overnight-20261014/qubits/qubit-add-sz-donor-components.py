"""Add isolated SZ6/7 donor normalization and virtual-size care tests.

Does not integrate the donors into crossing parking or change reserve size.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]);midg=root/'src/point_add/midg.rs'
helpers=r'''

// Only admitted large-SY active shots have SZ101..159. Their high two
// size bits are determined by the low six; inactive arbitrary bits restore.
pub(crate) fn normalize_sz_donors(b:&mut B,sz:&[QubitId],sy:&[QubitId],act:QubitId,dirty:&[QubitId])->Vec<G>{
    assert!(sz.len()>=8);
    let large=size_partition(sy,false);
    let high6=[(63usize,37usize),(62,38),(56,40),(48,48)];
    super::frogdrop_col::rec(b,|b|{
        for selector in &large {
            for &(mask,value) in &high6 {
                let mut literals=selector.clone();literals.push((act,false));
                literals.extend((0..6).filter(|&i|mask>>i&1!=0).map(|i|(sz[i],value>>i&1==0)));
                mc_xor(b,&literals,sz[6],&[],dirty);
            }
            let mut literals=selector.clone();literals.extend([(act,false),(sz[5],true)]);
            mc_xor(b,&literals,sz[7],&[],dirty);
        }
    })
}

fn virtual_crot_care(b:&mut B,v:&[QubitId],r:usize,support:&std::collections::BTreeSet<usize>,
                    selectors:&[Vec<(QubitId,bool)>],dirty:&[QubitId]) {
    use std::collections::{BTreeMap,BTreeSet};let n=v.len();let r=r%n;if r==0{return;}
    let mut successor:BTreeMap<usize,usize>=support.iter().map(|&i|(i,(i+r)%n)).collect();
    let destinations:BTreeSet<usize>=successor.values().copied().collect();
    for &start in support.difference(&destinations){let mut end=start;while support.contains(&end){end=successor[&end];}successor.insert(end,start);}
    let mut seen=BTreeSet::new();for &start in successor.keys(){if seen.contains(&start){continue;}let mut cycle=vec![];let mut i=start;while !seen.contains(&i){seen.insert(i);cycle.push(i);i=successor[&i];}assert_eq!(i,start);
        for k in (1..cycle.len()).rev(){for selector in selectors{super::mid2::mc_swap(b,selector,v[cycle[k]],v[cycle[k-1]],&[],dirty);}}
    }
}

pub(crate) fn care_borrowed_sz(b:&mut B,v:&[QubitId],sz:&[QubitId],sy:&[QubitId],
                  dest:&std::collections::BTreeSet<usize>,inverse:bool,dirty:&[QubitId])->Vec<G>{
    assert!(sz.len()>=8);let mut support=dest.clone();let small=size_partition(sy,true);let large=size_partition(sy,false);
    let record=super::frogdrop_col::rec(b,|b|{
        for (k,&bit) in sz.iter().enumerate(){let r=(1usize<<k)%v.len();let mut controls=vec![];
            if k==6||k==7{
                for cube in &small{let mut c=cube.clone();c.push((bit,false));controls.push(c);}
                for cube in &large{
                    if k==6{for &(mask,value)in &[(63usize,37usize),(62,38),(56,40),(48,48)]{let mut c=cube.clone();c.extend((0..6).filter(|&i|mask>>i&1!=0).map(|i|(sz[i],value>>i&1==0)));controls.push(c);}}
                    else{let mut c=cube.clone();c.push((sz[5],true));controls.push(c);}
                }
            }else{controls.push(vec![(bit,false)]);}
            virtual_crot_care(b,v,r,&support,&controls,dirty);
            let shifted:Vec<_>=support.iter().map(|&i|(i+r)%v.len()).collect();support.extend(shifted);
        }
    });
    if inverse{record.iter().rev().copied().collect()}else{record}
}
'''
# Care gates are strictly unitary X/CX/CCX, so reversing their recording is
# exact. No measurement gates or abstract row operations occur in this helper.
assert 'fn normalize_sz_donors' not in midg.read_text();midg.write_text(midg.read_text()+helpers)
path=root/'src/point_add/tests_midg_k24.rs'
tests=r'''

#[test]
fn sz_donor_normalization_virtual_care_boundary_inactive_inverse_phase(){
    let mut b=builder();let ring=b.alloc_n(276);let sz=b.alloc_n(9);let sy=b.alloc_n(8);let act=b.alloc();let dirty=b.alloc_n(259);
    let dest:std::collections::BTreeSet<usize>=(0..45).chain(244..276).collect();
    let normal=super::midg::normalize_sz_donors(&mut b,&sz,&sy,act,&dirty);
    let up=super::midg::care_borrowed_sz(&mut b,&ring,&sz,&sy,&dest,false,&dirty);
    let forward=emitted(&mut b,&up,false);let inverse=emitted(&mut b,&up,true);let nforward=emitted(&mut b,&normal,false);let ninverse=emitted(&mut b,&normal,true);
    let mut rng=Rng::new(0x20261014_6799);let mut coefficients=0;
    for block in 0..8 {
        let mut input:Vec<_>=(0..b.width()).map(|_|rng.next()).collect();input[act.0 as usize]=0;
        for lane in 0..64 {let syv=[98usize,99,128,129,226,227,0,1][lane%8];let size=[101usize,127,128,159,0,100,160,255][(lane/8+block)%8];let active=(1..=128).contains(&syv)&&(101..=159).contains(&size);put(&mut input,&sz,lane,N::from(size as u64));put(&mut input,&sy,lane,N::from(syv as u64));if active{input[act.0 as usize]|=1u64<<lane;}}
        let normalized=run(&nforward,input.len(),&|q|*q=input.clone());assert_eq!(normalized.phase,0);
        for lane in 0..64{let syv=get(&input,&sy,lane).as_limbs()[0]as usize;let active=input[act.0 as usize]>>lane&1!=0;if active&&syv>=99{assert_eq!(normalized.q[sz[6].0 as usize]>>lane&1,0);assert_eq!(normalized.q[sz[7].0 as usize]>>lane&1,0);}else{assert_eq!(normalized.q[sz[6].0 as usize]>>lane&1,input[sz[6].0 as usize]>>lane&1);assert_eq!(normalized.q[sz[7].0 as usize]>>lane&1,input[sz[7].0 as usize]>>lane&1);}}
        let nback=run(&ninverse,input.len(),&|q|*q=normalized.q.clone());assert_eq!(nback.q,input);assert_eq!(nback.phase,0);
        let(mut borrowed,borrowed_act)=(normalized.q.clone(),input[act.0 as usize]);let high6=rng.next();let high7=rng.next();let large_active=(0..64).fold(0u64,|mask,lane|{let syv=get(&input,&sy,lane).as_limbs()[0];mask|if borrowed_act>>lane&1!=0&&syv>=99{1u64<<lane}else{0}});borrowed[sz[6].0 as usize]=(borrowed[sz[6].0 as usize]&!large_active)|(high6&large_active);borrowed[sz[7].0 as usize]=(borrowed[sz[7].0 as usize]&!large_active)|(high7&large_active);
        let got=run(&forward,input.len(),&|q|*q=borrowed.clone());assert_eq!(got.phase,0);
        for lane in 0..64 {if borrowed_act>>lane&1==0{continue;}let size=get(&input,&sz,lane).as_limbs()[0]as usize;for &index in &dest{assert_eq!(got.q[ring[(index+size)%276].0 as usize]>>lane&1,borrowed[ring[index].0 as usize]>>lane&1,"admitted care mapping with parked high-size data");}}
        for &id in sz.iter().chain(&sy).chain(&dirty){assert_eq!(got.q[id.0 as usize],borrowed[id.0 as usize]);}
        let back=run(&inverse,input.len(),&|q|*q=got.q.clone());assert_eq!(back.q,borrowed);assert_eq!(back.phase,0);let(sym,n)=symbolic(&forward,borrowed.clone());assert_eq!(sym,got.q);coefficients+=n;let(sym,n)=symbolic(&inverse,got.q);assert_eq!(sym,borrowed);coefficients+=n;
    }
    eprintln!("SZ_DONOR_COMPONENT_PASS cases=512 SY_boundaries=98,99,128 SZ_boundaries=101,127,128,159 inactive_aliases=true arbitrary_parked_highbits=true all_wire_inverse=true phase=0 independent_measurement_coefficients={coefficients} scope=normalization_and_care_only");
}
'''
assert 'fn sz_donor_normalization' not in path.read_text();path.write_text(path.read_text()+tests)
