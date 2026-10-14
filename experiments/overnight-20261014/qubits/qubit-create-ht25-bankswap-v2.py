"""Separate component-only bank transfer; frozen HT25-v9 remains unchanged."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,dest,ev=map(lambda x:Path(x).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
def rep(t,a,z):
    assert a in t,a
    return t.replace(a,z)
p=dest/'src/point_add/midg.rs';t=p.read_text()
old='''let selectors=if bank {vec![vec![(sy[3],true),(sy[4],true),(sy[5],false),(sy[6],false)]]}'''
new='''let selectors=if bank {let mut v=size_partition(sy,true);v.push(vec![(sy[3],true),(sy[4],true),(sy[5],false),(sy[6],false)]);v}'''
t=rep(t,old,new)
t=rep(t,'let k32 = if precision25 {','let k32 = if precision25 && !ht25 {')
old='''let mut rs=s1.r.clone();rs.extend(bank);let bs=S1{r:rs,..s1.clone()};let z32=ring[n-32..n].to_vec();
        let f=stage1_v_compact_bank_partition(b,&z32,&win,&sc.sz,szr,&bs,act,true,&fd.sy,false,true);
        let r=stage1_v_compact(b,&z32,&win,&sc.sz,szr,&bs,act,false);
        let f24=stage1_v_compact_bank_partition(b,&zh,&win,&sc.sz,szr,&s1,act,true,&fd.sy,false,false);
        Some((f,r,f24))'''
new='''let mut rs=s1.r.clone();rs.extend(&q[120..128]);let bs=S1{r:rs,..s1.clone()};let z32=ring[n-32..n].to_vec();
        assert!(!bank.iter().any(|id|z32.contains(id)||sc.sz.contains(id)));
        assert!(!bank.iter().any(|id|bs.r.contains(id)||bs.anc.contains(id)||bs.andc.contains(id)||bs.chain.contains(id)));
        let transfer=transfer_bank32(b,&q[120..128],&bank,&fd.sy,act,sx[0],&dirty);
        let f=stage1_v_compact_bank_partition(b,&z32,&win,&sc.sz,szr,&bs,act,true,&fd.sy,true,true);
        let r=stage1_v_compact(b,&z32,&win,&sc.sz,szr,&bs,act,false);
        let f24=stage1_v_compact_bank_partition(b,&zh,&win,&sc.sz,szr,&s1,act,true,&fd.sy,false,false);
        Some((transfer,f,r,f24))'''
t=rep(t,old,new)
old='''if let Some((f25,f32,r32)) = &k32 {
            if let Some((bf,br,f24))=&bank32{b.play(f24,false);b.play(&fr,true);b.play(bf,false);b.play(br,true);}
            else{b.play(f25,false);b.play(&fr,true);}
            b.play(f32,false); b.play(r32,true);
        } else { b.play(&fv,false); b.play(&fr,true); }'''
new='''if let Some((transfer,f32,r32,f24))=&bank32{
            b.play(transfer,false);
            b.play(f24,false);b.play(&fr,true);
            b.play(f32,false);b.play(r32,true);
            b.play(transfer,true);
        }else if let Some((f25,f32,r32))=&k32{
            b.play(f25,false);b.play(&fr,true);b.play(f32,false);b.play(r32,true);
        }else{b.play(&fv,false);b.play(&fr,true);}'''
t=rep(t,old,new)
t+=r'''

// On active admitted medium-size shots, SY96..103 and highestpark<=127;
// reserve is clean and all Q-bank passengers belong to parked quotient.
// Low7 SY is immutable while SY7 is transferred. Inactive high aliases
// cannot borrow because act=0. SX0 must enter zero and returns before R use.
pub(crate) fn transfer_bank32(b:&mut B,qbank:&[QubitId],reserve:&[QubitId],sy:&[QubitId],act:QubitId,flag:QubitId,dirty:&[QubitId])->Vec<G>{
    assert_eq!(qbank.len(),8);assert_eq!(reserve.len(),8);assert_eq!(sy.len(),8);
    assert!(!qbank.iter().any(|id|reserve.contains(id)||sy[..7].contains(id)||*id==act||*id==flag||dirty.contains(id)));
    assert!(!reserve.iter().any(|id|sy[..7].contains(id)||*id==act||*id==flag||dirty.contains(id)));
    let controls=[(act,false),(sy[3],true),(sy[4],true),(sy[5],false),(sy[6],false)];
    rec(b,|b|{mc_xor(b,&controls,flag,&[],dirty);for i in 0..8{b.cswap(flag,qbank[i],reserve[i]);}mc_xor(b,&controls,flag,&[],dirty);})
}
''';p.write_text(t)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text()
t+=r'''

#[test]
fn ht25_transfer_bank32_full_sy_dirty_quotient_inverse_phase(){
    let mut b=builder();let _ring=b.alloc_n(275);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),692);
    let bank=[pool[9],pool[11],pool[10],sx[6],sx[7],ph,pool[8],sy[7]];let act=pool[12];let record=super::midg::transfer_bank32(&mut b,&q[120..128],&bank,&sy,act,sx[0],&dirty);let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let mut rng=Rng::new(0x20261014_325a);let mut total=0;
    for pattern in 0..16{for block in 0..4{let mut input:Vec<_>=(0..692).map(|_|rng.next()).collect();input[act.0 as usize]=0;input[sx[0].0 as usize]=0;
        for lane in 0..64{let value=block*64+lane;put(&mut input,&sy,lane,N::from(value as u64));if (1..=128).contains(&value){input[act.0 as usize]|=1u64<<lane;}if (96..=103).contains(&value){for &id in &bank{input[id.0 as usize]&=!(1u64<<lane);}put(&mut input,&sy,lane,N::from(value as u64));for (i,&id)in q[120..128].iter().enumerate(){input[id.0 as usize]=(input[id.0 as usize]&!(1u64<<lane))|((((pattern as u64*17+lane as u64)>>i)&1)<<lane);}}}
        let mut expected=input.clone();for lane in 0..64{let value=block*64+lane;if !(96..=103).contains(&value){continue;}for i in 0..8{let a=q[120+i].0 as usize;let z=bank[i].0 as usize;let delta=((input[a]^input[z])>>lane)&1;expected[a]^=delta<<lane;expected[z]^=delta<<lane;}}
        let got=run(&forward,692,&|w|*w=input.clone());assert_eq!(got.q,expected);assert_eq!(got.phase,0);let back=run(&inverse,692,&|w|*w=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);total+=64;
    }}
    eprintln!("HT25_BANK_TRANSFER_PASS cases={total} fullSY_words=256 medium=96..103 active_highbank_dirty=true inactive_arbitrary=true bothbanks_restored=true flag_returned=true all_wire_inverse=true native_phase=0");
}
''';p.write_text(t)
changed=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines();assert all(p.startswith('src/point_add/')for p in changed)
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/']);(ev/'candidate-ht25-bankswap-v2.patch').write_bytes(patch)
manifest=dict(scope='Separate component prototype; one Q-bank R32 driver via reversible reserve transfer; frozenHT25-v9 unchanged; pending native/ALLMR',parent_source='candidate-ht25-v9',base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),checkout=str(dest),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in changed})
(ev/'candidate-ht25-bankswap-v2-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
