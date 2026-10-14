"""Isolated N275/K16 prototype: eight Q loans and three-lane ordinary maps.

Source geometry only; counts are not scores. Only point_add files change.
"""
from pathlib import Path
import shutil, subprocess, sys
source,dest=map(lambda s:Path(s).resolve(),sys.argv[1:3])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in ['frogdrop.rs','midg.rs','pointadd_frogdrop.rs','tests_midg_k24.rs']:
    shutil.copyfile(source/'src/point_add'/name,dest/'src/point_add'/name)
p=dest/'src/point_add/pointadd_frogdrop.rs';t=p.read_text().replace('pub const N: usize = 276;','pub const N: usize = 275;').replace('pub const K: usize = 17;','pub const K: usize = 16;');p.write_text(t)
p=dest/'src/point_add/midg.rs';t=p.read_text()
for old,new in [('n==276','n==275'),('n == 276','n == 275'),('k==17','k==16'),('k == 17','k == 16'),('cp.h==19','cp.h==18'),('cp.h == 19','cp.h == 18'),('if cap24{24}else{23}','if cap24{24}else{22}'),('q[121..128]','q[120..128]'),('ring[n - 25..n]','ring[n - 24..n]'),('reciprocal_r.len(), 25','reciprocal_r.len(), 24'),('k + 1, 18','k + 1, 17'),('k+1==18','k+1==17'),('&[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64),(126,96)]','&[(127,1),(126,2),(124,4),(120,8),(112,16),(96,32),(96,64),(127,96)]'),('&[(127,0),(126,98),(124,100),(120,104),(112,112)]','&[(127,0),(127,97),(126,98),(124,100),(120,104),(112,112)]')]:
    assert old in t,old;t=t.replace(old,new)
old='let mut literals=selector.clone();literals.extend([(act,false),(sz[5],true)]);\n            mc_xor(b,&literals,sz[7],&[],dirty);'
new=old+'\n            let mut literals=selector.clone();literals.push((act,false));literals.extend((0..6).map(|i|(sz[i],i!=5)));\n            mc_xor(b,&literals,sz[7],&[],dirty);'
assert old in t;t=t.replace(old,new)
old='else{let mut c=cube.clone();c.push((sz[5],true));controls.push(c);}'
new='else{let mut c=cube.clone();c.push((sz[5],true));controls.push(c);let mut c=cube.clone();c.extend((0..6).map(|i|(sz[i],i!=5)));controls.push(c);}'
assert old in t;t=t.replace(old,new).replace('SZ101..159','SZ101..160');p.write_text(t)
p=dest/'src/point_add/frogdrop_col.rs';t=p.read_text()
old='extension.push(q[120]);';new=old+'\n                    if extra>2 {assert_eq!(extra,3);extension.push(q[119]);}'
assert t.count(old)==1;t=t.replace(old,new)
old='let owed = extra - extension.len();'
new='''// After stage 8 probe_z inverse, every SZ lane is clean, including
            // SW when the first column borrowed it as SZ bit 8. Non-switch
            // maps preserve SW=0; B0 excludes it because SW is replay control.
            if extra==3 && cp.sz!=(0,0) {assert!(!cp.sw);extension.push(sc.sw);}
            let owed = extra - extension.len();'''
assert t.count(old)==1;t=t.replace(old,new);p.write_text(t)
# Native full-column fixtures use the new actual width; historical primitive
# fixtures retain their original constructor geometry and are not selected.
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text();start=t.index('#[test]\nfn reserve9_columns_crossing_3713_positive_native');t=t[:start]+t[start:].replace('alloc_n(276)','alloc_n(275)').replace('693','692')
a=t.index('#[test]\nfn sz_donor_normalization');z=t.index('#[test]',a+10)
donor=t[a:z].replace('sz_donor_normalization_virtual_care_boundary_inactive_inverse_phase','n275_sz_donor_boundaries_inverse_phase').replace('276','275').replace('244..275','243..275').replace('98usize,99,128','96usize,97,128').replace('159','160').replace('syv>=99','syv>=97')
a=t.index('#[test]\nfn k32_partition_boundary');z=t.index('#[test]',a+10)
partition=t[a:z].replace('k32_partition_boundary_inactive_counter_inverse_phase','n275_k32_k24_partition_all_sy_words').replace('alloc_n(276)','alloc_n(275)').replace('693','692').replace('ring[..19]','ring[..18]').replace('ring[275]','ring[274]').replace('q[121..128]','q[120..128]').replace('ring[18]','ring[17]').replace('ring[18..19+TC]','ring[17..18+TC]').replace('ring[251..276]','ring[251..275]').replace('ring[244..276]','ring[243..275]').replace('size<=98','size<=96').replace('syvalue<=98','syvalue<=96').replace('else{25}','else{24}').replace('ring[276-k..276]','ring[275-k..275]').replace('ring[18+i]','ring[17+i]')
partition=partition.replace('put(&mut input,&pool[..8],lane,N::from([65usize,101,128,230,231,232,255,256][lane%8]as u64));','put(&mut input,&pool[..8],lane,N::from(if active && size>=97 {[101usize,127,128,160][lane%4]}else{[65usize,101,128,230,231,232,255,256][lane%8]}as u64));')
p.write_text(t+donor+partition)
# Copy existing map checks under unique names, adapting only new geometry.
p=dest/'src/point_add/tests_frogdrop.rs';t=p.read_text();a=t.index('#[test]\nfn d2_ordinary_map_extension_exact');z=t.index('#[test]\nfn d4_n278',a);new=t[a:z].replace('d2_ordinary_map_extension_exact','n275_ordinary_three_lane_map_exact').replace('d3_b0_two_lane_extension_controlled_replay','n275_b0_three_lane_extension_controlled_replay').replace('276','275').replace('693','692');p.write_text(t+new)
