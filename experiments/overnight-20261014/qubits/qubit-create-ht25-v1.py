"""Isolated N275 HT25 storage prototype; precision remains deliberately unchanged."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,re
source,dest,ev=map(lambda x:Path(x).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
def rep(t,a,z):
    assert a in t,a
    return t.replace(a,z)
p=dest/'src/point_add/pointadd_frogdrop.rs';t=p.read_text();t=rep(t,'pub const QB: usize = 24;','pub const QB: usize = 25;');p.write_text(t)
p=dest/'src/point_add/midg.rs';t=p.read_text()
t=rep(t,'(96,64),(127,96)]','(96,64)]')
t=rep(t,'&[(127,0),(127,97),(126,98),(124,100),(120,104),(112,112)]','&[(127,0),(96,96)]')
t=rep(t,'(0..6).map(|i|(sz[i],i!=5))','(1..6).map(|i|(sz[i],i!=5))')
t=rep(t,'let kmax = bmax.min(mt).min(if n==275 && k==16 {if cap24{24}else{22}}else{usize::MAX});','''let ht25 = n==275 && k==16 && nq==128 && sx.len()==8 && dirty.len()==259
        && cp.h==18 && cp.sz.0>=101 && cp.sz.1<=255 && cp.ht;
    let hrmax=bmax.min(mt).min(if cap24{24}else{22});
    let kmax = bmax.min(mt).min(if ht25{25}else if n==275&&k==16{if cap24{24}else{22}}else{usize::MAX});''')
t=rep(t,'!q[120..128].contains(qid)','!q[116..128].contains(qid)')
t=rep(t,'else if precision25 && (k+1..=k+5).contains(&kb)','else if ht25 && (22..=24).contains(&kb){Some(q[140-kb])}else if precision25 && (k+1..=k+5).contains(&kb)')
t=rep(t,'kmax<=if cap24{24}else{22}','kmax<=if ht25{25}else if cap24{24}else{22}')
idx=t.index('    // tmp ^= [kb >= 258 - s9]')
t=t[:idx]+'''    let high_toggle=|b:&mut B,kb:usize,base:&[(QubitId,bool)],target:QubitId|{
        high_q25_toggle(b,&fd.sy,kb,base,target,&dirty);
    };
'''+t[idx:]
t=rep(t,'b.and_c(a, c, ak);','if ht25 && kb>=22 {high_toggle(b,kb,&[(a,false),(c,false)],ak);}else{b.and_c(a,c,ak);}')
t=rep(t,'b.and_u(a, c, ak);','if ht25 && kb>=22 {high_toggle(b,kb,&[(a,false),(c,false)],ak);}else{b.and_u(a,c,ak);}')
t=rep(t,'ring_cadd2_loan(b, &ring, &q, kb, mt - kb, ctl, sub, &sc.zeros, c0, x128, &dirty, lsb, loan_end, x128);','''if precision25 {q25_cadd(b,&ring,&q,&fd.sy,kb,mt-kb,ctl,sub,&sc.zeros,c0,x128,&dirty,lsb,loan_end,sx[0]);}
        else{ring_cadd2_loan(b,&ring,&q,kb,mt-kb,ctl,sub,&sc.zeros,c0,x128,&dirty,lsb,loan_end,x128);}''')
t=rep(t,'mc_xor(b, &ct, c, &[], &dirty);','if ht25 && kb>=22 {high_toggle(b,kb,&ct,c);}else{mc_xor(b,&ct,c,&[],&dirty);}')
t=rep(t,'let pre23 = if cap24','let high_a=if ht25{Some(preposition_high_q25(b,&q129a,&fd.sy[..7],act,&dirty))}else{None};\n    let pre23 = if cap24')
t=rep(t,'if relocated19 && kb == k + 1 { continue; }','if relocated19 && kb == k + 1 { continue; }\n            if ht25 && kb>=22 {continue;}')
# HR alone retains its original admitted capacity, despite mixed-column HT25.
start=t.index('    // ---------------- HR: binary search');end=t.index('    // ---------------- HT:',start)
part=t[start:end].replace('0..kmax','0..hrmax').replace('kmax).rev()','hrmax).rev()')
old='''super::payload::trans_one(b, &t, &src[..sl], kk, false, vec![(c, false)], None, sx[0], c0, &[],
                                          &pl.dirty);'''
new='''if precision25 {
                    for (lo,hi,length) in [(1usize,116usize,116usize),(117,255,128)]{
                        sy_interval_toggle(b,&fd.sy,lo,hi,&[(c,false)],ak,&dirty);
                        super::payload::trans_one(b,&t,&q[..length.min(t.len())],kk,false,vec![(ak,false)],None,sx[0],c0,&[],&pl.dirty);
                        sy_interval_toggle(b,&fd.sy,lo,hi,&[(c,false)],ak,&dirty);
                    }
                }else{super::payload::trans_one(b,&t,&src[..sl],kk,false,vec![(c,false)],None,sx[0],c0,&[],&pl.dirty);}'''
part=rep(part,old,new)
for flag in ['false','true']:
    part=rep(part,f'if let Some(norm) = &pad_sy7_zero {{ b.play(norm, {flag}); }}',f'if !precision25 {{if let Some(norm)=&pad_sy7_zero{{b.play(norm,{flag});}}}}')
t=t[:start]+part+t[end:]
# Both A calls have high owner preparation before ordinary parking.
t=rep(t,'if let Some(p)=&pre23{b.play(p,false);}\n        b.play(&park, false);','if let Some(p)=&pre23{b.play(p,false);}\n        if let Some(p)=&high_a{b.play(p,false);}\n        b.play(&park, false);')
t=rep(t,'b.play(&park, false);\n        if let Some(p)=&pre23','b.play(&park, false);\n        if let Some(p)=&high_a{b.play(p,false);}\n        if let Some(p)=&pre23')
a=t.index('            let pre19 = if precision25');z=t.index('            super::frogdrop_col::mark(b, 1501);',a)
t=t[:a]+'''            let pre19 = if precision25 {Some(rec(b,|b|{
                let ranges: &[(usize,usize)]=if ht25{&[(1,98),(102,128)]}else{&[(1,128)]};
                for &(lo,hi) in ranges{if cp.sy.0.max(lo)<=cp.sy.1.min(hi){
                    let p=preposition_qk(b,&q129b,&fd.sy,sx[1],k+1,actl,(cp.sy.0.max(lo),cp.sy.1.min(hi)),&dirty);b.play(&p,false);}
                }
            }))}else{None};
            let high_b=if ht25{Some(preposition_high_q25(b,&q129b,&fd.sy,actl,&dirty))}else{None};
            let late19=if ht25{Some(preposition_qk(b,&q129b,&fd.sy,sx[1],k+1,actl,(cp.sy.0.max(99),cp.sy.1.min(101)),&dirty))}else{None};
'''+t[z:]
t=rep(t,'if let Some(p) = &pre19 { b.play(p, false); }\n            super::frogdrop_col::mark(b, 1502);','if let Some(p)=&pre19{b.play(p,false);}\n            if let Some(p)=&high_b{b.play(p,false);}\n            if let Some(p)=&late19{b.play(p,false);}\n            super::frogdrop_col::mark(b,1502);')
t=rep(t,'super::frogdrop_col::mark(b, 1504);\n            if let Some(p) = &pre19','super::frogdrop_col::mark(b,1504);\n            if let Some(p)=&late19{b.play(p,false);}\n            if let Some(p)=&high_b{b.play(p,false);}\n            if let Some(p) = &pre19')
t+=r'''

// Inclusive full-eight-bit SY interval, represented by disjoint positive cubes.
pub(crate) fn sy_interval_toggle(b:&mut B,sy:&[QubitId],lo:usize,hi:usize,base:&[(QubitId,bool)],target:QubitId,dirty:&[QubitId]){
    if lo>hi{return;}assert_eq!(sy.len(),8);let mut start=lo;
    while start<=hi{let mut block=1usize;while block<256&&start%(block*2)==0&&start+block*2-1<=hi{block*=2;}
        let mask=255usize^(block-1);let mut ctl=base.to_vec();ctl.extend((0..8).filter(|i|mask>>i&1!=0).map(|i|(sy[i],start>>i&1==0)));mc_xor(b,&ctl,target,&[],dirty);start+=block;
    }
}
pub(crate) fn high_q25_toggle(b:&mut B,sy:&[QubitId],kb:usize,base:&[(QubitId,bool)],target:QubitId,dirty:&[QubitId]){
    assert!((22..=24).contains(&kb));sy_interval_toggle(b,sy,1,137-kb,base,target,dirty);
}
pub(crate) fn q25_cadd(b:&mut B,ring:&[QubitId],q:&[QubitId],sy:&[QubitId],kb:usize,span:usize,ctl:QubitId,sub:bool,zeros:&[QubitId],c0:QubitId,h:QubitId,dirty:&[QubitId],lsb:usize,loan_end:usize,flag:QubitId){
    ring_cadd2_loan(b,ring,&q[..116],kb,span,ctl,sub,zeros,c0,h,dirty,lsb.min(116),loan_end.min(116),h);
    for index in 116usize..128{let length=1;
        if span<=index{continue;}sy_interval_toggle(b,sy,index+1,255,&[(ctl,false)],flag,dirty);
        super::frogdrop_col::ring_cadd2(b,ring,&q[index..index+length],kb+index,span-index,flag,sub,zeros,c0,h,dirty);
        sy_interval_toggle(b,sy,index+1,255,&[(ctl,false)],flag,dirty);
    }
}
// Reflection i <-> SY+140-i groups overlapping high quotient owners into
// disjoint transpositions; arbitrary target passengers are restored by replay.
pub(crate) fn preposition_high_q25(b:&mut B,cycle:&[QubitId],sy:&[QubitId],act:QubitId,dirty:&[QubitId])->Vec<G>{
    assert_eq!(cycle.len(),138);assert!(sy.len()==7||sy.len()==8);
    rec(b,|b|{for value in 1usize..=115{
        let mut pairs=std::collections::BTreeSet::new();
        for kb in 22usize..=24{if value>137-kb{continue;}let owner=140-kb;let target=value+kb;if owner!=target{pairs.insert((owner.min(target),owner.max(target)));}}
        let mut controls=vec![(act,false)];controls.extend(sy.iter().enumerate().map(|(i,&wire)|(wire,value>>i&1==0)));
        for (a,z) in pairs{super::mid2::mc_swap(b,&controls,cycle[a],cycle[z],&[],dirty);}
    }})
}
'''
p.write_text(t)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text()
t+=r'''

#[test]
fn ht25_masked_add_full_sy_dirty_owner_inverse_phase(){
    let mut total=0;
    for kb in [0usize,6,24]{
        let mut b=builder();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),692);
        let record=rec(&mut b,|b|super::midg::q25_cadd(b,&ring,&q,&sy,kb,129,ph,false,&[pool[10]],pool[11],pool[9],&dirty,128,128,sx[0]));
        let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let ladder:Vec<_>=(kb..kb+129).map(|i|ring[274-i]).collect();let mut rng=Rng::new(0x20261014_2500+kb as u64);
        for pattern in 0..8{for block in 0..4{
            let mut input:Vec<_>=(0..692).map(|_|rng.next()).collect();for id in [ph,pool[10],pool[11],pool[9],sx[0]]{input[id.0 as usize]=0;}let mut values=vec![];
            for lane in 0..64{let size=block*64+lane;put(&mut input,&sy,lane,N::from(size as u64));let active=(1..=128).contains(&size);let mut y=get(&input,&q,lane);
                if active{y&=(N::from(1u64)<<size)-N::from(1u64);y|=N::from(1u64)<<(size-1);put(&mut input,&q,lane,y);for bit in 22usize..=24{if size<=137-bit&&pattern>>(bit-22)&1!=0{input[q[140-bit].0 as usize]|=1u64<<lane;}}input[ph.0 as usize]|=1u64<<lane;}
                values.push((y,active));
            }
            let mut expected=input.clone();let mask=(N::from(1u64)<<129)-N::from(1u64);
            for (lane,(y,active))in values.iter().enumerate(){if *active{put(&mut expected,&ladder,lane,(get(&input,&ladder,lane)+*y)&mask);}}
            let got=run(&forward,692,&|w|*w=input.clone());assert_eq!(got.q,expected,"HT25 masked add kb{kb} pattern{pattern} block{block}");assert_eq!(got.phase,0);
            let back=run(&inverse,692,&|w|*w=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);total+=64;
        }}
    }
    eprintln!("HT25_MASKED_ADD_PASS cases={total} full_SY_words=256 q22_q23_q24_patterns=8 inactive_dirty=true all_wires_inverse=true phase=0");
}

#[test]
fn ht25_preposition_reflection_and_q17_all_sy_inverse_phase(){
    let mut total=0;
    for mode in 0..2{
        let mut b=builder();let ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),692);
        let control=if mode==1{pool[8]}else{pool[12]};let mut cycle=q.clone();cycle.extend([pool[9],pool[11],pool[10],sx[6],sx[7],pool[6],pool[7],ph]);
        if mode==1{cycle.extend([pool[12],sx[1]]);}else{cycle.extend([pool[8],sy[7]]);}assert_eq!(cycle.len(),138);
        let early=if mode==1{rec(&mut b,|b|for (lo,hi)in [(1usize,98usize),(102,128)]{let p=super::midg::preposition_qk(b,&cycle,&sy,sx[1],17,control,(lo,hi),&dirty);b.play(&p,false);})}else{vec![]};
        let high=super::midg::preposition_high_q25(&mut b,&cycle,if mode==1{&sy}else{&sy[..7]},control,&dirty);
        let late=if mode==1{super::midg::preposition_qk(&mut b,&cycle,&sy,sx[1],17,control,(99,101),&dirty)}else{vec![]};
        let record=rec(&mut b,|b|{b.play(&early,false);b.play(&high,false);b.play(&late,false);});let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let mut rng=Rng::new(0x20261014_2522+mode as u64);
        for pattern in 0..16{for block in 0..4{
            let mut input:Vec<_>=(0..692).map(|_|rng.next()).collect();input[control.0 as usize]=0;
            for lane in 0..64{let size=block*64+lane;put(&mut input,&sy,lane,N::from(size as u64));if !(1..=128).contains(&size){continue;}let mask=1u64<<lane;input[control.0 as usize]|=mask;for &id in &cycle{input[id.0 as usize]&=!mask;}put(&mut input,&sy,lane,N::from(if mode==1{size}else{size&127}as u64));
                for i in 0..size.min(128){if (i+lane)%3!=0{input[q[i].0 as usize]|=mask;}}
                for kb in 22usize..=24{if size<=137-kb&&pattern>>(kb-22)&1!=0{input[q[140-kb].0 as usize]|=mask;}}
                if mode==1&&size<=120&&pattern&8!=0{input[sx[1].0 as usize]|=mask;}
            }
            let mut expected=input.clone();
            // A quotient owner is outside Y on every admitted nonzero bit.
            // The oracle specifies the simultaneous ownership transfer.
            for lane in 0..64{let size=block*64+lane;if !(1..=128).contains(&size){continue;}let mask=1u64<<lane;
                let owners:Vec<_>=(22usize..=24).filter(|kb|size<=137-kb).map(|kb|(q[140-kb],cycle[size+kb])).chain(if mode==1&&size+17<138{Some((sx[1],cycle[size+17]))}else{None}).collect();
                for &(owner,_)in &owners{expected[owner.0 as usize]&=!mask;}
                for &(owner,target)in &owners{let bit=input[owner.0 as usize]&mask;expected[target.0 as usize]=(expected[target.0 as usize]&!mask)|bit;}
            }
            let got=run(&forward,692,&|w|*w=input.clone());assert_eq!(got.q,expected,"HT25 simultaneous ownership mode{mode} pattern{pattern} block{block}");assert_eq!(got.phase,0);
            let back=run(&inverse,692,&|w|*w=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);total+=64;
        }}
    }
    eprintln!("HT25_REFLECTION_OWNER_PASS cases={total} modes=A,B q17_overlap=99,100,101 full_SY_words=256 inactive_dirty=true all_wires_inverse=true phase=0");
}
'''
p.write_text(t)
changed=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines();assert all(p.startswith('src/point_add/')for p in changed)
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/']);(ev/'candidate-ht25-v1.patch').write_bytes(patch)
manifest=dict(scope='HT25 storage arithmetic component; reciprocal head24 still known insufficient; no benchmark authorized',admitted_domain='HT q<2^25; mixedHR q<2^22; strict pureHR q<2^24; original source envelopes/reserve9/EMAX21; no above-capacity fallback',base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),checkout=str(dest),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in changed})
(ev/'candidate-ht25-v1-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
