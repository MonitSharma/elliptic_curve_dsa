"""Isolated arithmetic-repair prototype. Never alters a frozen candidate."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path(sys.argv[1]); original=root/'candidate-control-fold-v6'; dest=root/'candidate-repair-v8'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-hardlinks',str(original),str(dest)],check=True)
shutil.copytree(original/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/midg.rs'; s=p.read_text(encoding='utf8')
assert s.count('pub const TC: usize = 26;')==1
s=s.replace('pub const TC: usize = 26;','pub const TC: usize = 27;')
old='b.play(f24,false);b.play(&fr,true);'; assert s.count(old)==1
s=s.replace(old,'// Large-SY reciprocal uses a conditional-clean SZ donor below.\n            let _ = f24;')
old='b.play(f25,false);b.play(&fr,true);b.play(f32,false);b.play(r32,true);';assert s.count(old)==1
s=s.replace(old,'let _ = f25; b.play(f32,false);b.play(r32,true);')
needle='''        if precision25 { b.x(ring[n - 1]); }
        b.play(&prot, true);''';assert s.count(needle)==1
s=s.replace(needle,'''        if precision25 {
            let large = stage1_v_compact_large25(b, &ring[n-25..n], &win,
                &sc.sz, &fd.sy, &s1.r, act, sx[0], &dirty, ht25);
            b.play(&large, false);
        }
        if precision25 { b.x(ring[n - 1]); }
        b.play(&prot, true);''')
s+='''

// On selected large-SY shots, ACT=1 and SZ+SY<=258. Thus SZ<=162,
// so TC27 never clips. Retain selection in SX0, temporarily clear ACT
// and SZ0, and borrow these as reciprocal flag and 25th remainder lane.
// On unselected shots window writes are disabled and the reciprocal's
// exact forward/inverse pair restores arbitrary borrowed state.
pub(crate) fn stage1_v_compact_large25(b:&mut B,zh:&[QubitId],win:&[QubitId],
    sz:&[QubitId],sy:&[QubitId],r24:&[QubitId],act:QubitId,root:QubitId,
    dirty:&[QubitId],bank:bool)->Vec<G>{
    assert_eq!(zh.len(),25);assert_eq!(r24.len(),24);
    assert_eq!(sz.len(),8);assert!(sy.len()>=7);
    assert!(!r24.contains(&sz[0])&&!r24.contains(&act)&&!r24.contains(&root));
    assert!(!zh.contains(&sz[0])&&!zh.contains(&act)&&!zh.contains(&root));
    let cubes = if bank {vec![(127usize,0usize),(120,104),(112,112)]}
                else {vec![(127usize,0usize),(96,96)]};
    rec(b,|b|{for (mask,value) in cubes.iter().copied(){for bit in 0..=1{
        let mut literals=vec![(act,false),(sz[0],bit==0)];
        literals.extend((0..7).filter(|i|mask>>i&1!=0).map(|i|(sy[i],value>>i&1==0)));
        mc_xor(b,&literals,root,&[],dirty);
        if bit==1 {b.cx(root,sz[0]);}
        b.x(act);
        let mut r=r24.to_vec();r.push(sz[0]);
        let scratch=S1{r,f:act,zero:r24[17],sgn:act,gt:vec![act],
            anc:vec![],andc:vec![],chain:vec![],dirty:dirty.to_vec()};
        let forward=stage1_v_compact(b,zh,win,sz,(101,230),&scratch,root,true);
        let restore=stage1_v_compact(b,zh,win,sz,(101,230),&scratch,root,false);
        b.play(&forward,false);b.play(&restore,true);
        b.x(act);
        if bit==1 {b.cx(root,sz[0]);}
        mc_xor(b,&literals,root,&[],dirty);
    }}})
}
'''
p.write_text(s,encoding='utf8',newline='\n')
p=dest/'src/point_add/pointadd_frogdrop.rs';s=p.read_text(encoding='utf8')
assert s.count('pub const EMAX: usize = 21;')==1
s=s.replace('pub const EMAX: usize = 21;','pub const EMAX: usize = 23;');p.write_text(s,encoding='utf8',newline='\n')
p=dest/'src/point_add/frogdrop_col.rs';s=p.read_text(encoding='utf8')
assert s.count('let nc = cp.cntw.min(fd.cnt.len());')==1
s=s.replace('let nc = cp.cntw.min(fd.cnt.len());','let mut nc = cp.cntw.min(fd.cnt.len());')
assert s.count('let sy_free = lean_park;')==1
s=s.replace('let sy_free = lean_park;','''let sy_free = lean_park || (cp.emax>21 && cp.sz!=(0,0));
        // Without counter parking, Q's counter remains outside qmap.
        if sy_free && !lean_park {nc=0;}''')
old='''extension.push(q[120]);
                    if extra>2 {assert_eq!(extra,3);extension.push(q[119]);}''';assert s.count(old)==1
s=s.replace(old,'''assert!(extra<=5);
                    for index in 0..extra-1 {extension.push(q[120-index]);}''')
p.write_text(s,encoding='utf8',newline='\n')
subprocess.run(['git','-C',str(dest),'add','--','src/point_add/'],check=True)
patch=subprocess.check_output(['git','-C',str(dest),'diff','--cached','--binary','--full-index','HEAD','--','src/point_add/'])
(root/'candidate-repair-v8.patch').write_bytes(patch)
manifest=dict(scope='UNQUALIFIED arithmetic repair prototype; TC27, large head25, EMAX23; no nonce change',candidate=str(dest),base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((dest/'src/point_add').rglob('*')) if p.is_file()})
(root/'candidate-repair-v8-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(json.dumps(manifest,indent=2))
