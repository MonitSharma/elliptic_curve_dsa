"""Fresh component prototype: Q118 q21; explicitly exclude every carry/read."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,dest,ev=map(lambda s:Path(s).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
def repl(t,a,z):
    assert a in t,a
    return t.replace(a,z)
p=dest/'src/point_add/midg.rs';t=p.read_text()
t=repl(t,'if precision25 && kb==21 {Some(sx[6])}','if precision25 && kb==21 {Some(q[118])}')
t=repl(t,'!q[119..128].contains(qid)','!q[118..128].contains(qid)')
needle='    // tmp ^= [kb >= 258 - s9]'
pos=t.index(needle)
t=t[:pos]+'''    // Q118 contains q21 only for admitted SY1..116; SY117/118 has
    // zero bit118 and SY119..128 holds genuine Y there. Full8 predicates
    // prevent inactive high aliases from selecting the wrong source.
    let q21_cubes=[(255usize,1usize),(254,2),(252,4),(248,8),(240,16),(224,32),(224,64),(240,96),(252,112),(255,116)];
    let q21_toggle=|b:&mut B,base:&[(QubitId,bool)],target:QubitId|{
        for &(mask,value) in &q21_cubes{let mut ctl=base.to_vec();ctl.extend((0..8).filter(|i|mask>>i&1!=0).map(|i|(fd.sy[i],value>>i&1==0)));mc_xor(b,&ctl,target,&[],&dirty);}
    };
    let high_toggle=|b:&mut B,base:&[(QubitId,bool)],target:QubitId,from119:bool|{
        let cubes: &[(usize,usize)]=if from119{&[(255,119),(248,120),(128,128)]}else{&[(255,117),(255,118),(255,119),(248,120),(128,128)]};
        for &(mask,value) in cubes{let mut ctl=base.to_vec();ctl.extend((0..8).filter(|i|mask>>i&1!=0).map(|i|(fd.sy[i],value>>i&1==0)));mc_xor(b,&ctl,target,&[],&dirty);}
    };
''' +t[pos:]
t=repl(t,'b.and_c(a, c, ak);','if precision25 && kb==21 {q21_toggle(b,&[(a,false),(c,false)],ak);} else {b.and_c(a, c, ak);}')
t=repl(t,'b.and_u(a, c, ak);','if precision25 && kb==21 {q21_toggle(b,&[(a,false),(c,false)],ak);} else {b.and_u(a, c, ak);}')
old='ring_cadd2_loan(b, &ring, &q, kb, mt - kb, ctl, sub, &sc.zeros, c0, x128, &dirty, lsb, loan_end, x128);'
new='''if precision25 {
            // Q118 is never a carry or unmasked source while it owns q21.
            // Truncated source plus exact dirty tail covers the whole ladder.
            ring_cadd2_loan(b,&ring,&q[..118],kb,mt-kb,ctl,sub,&sc.zeros,c0,x128,&dirty,lsb.min(118),loan_end.min(118),x128);
            if mt-kb>118 { high_toggle(b,&[(ctl,false)],sx[0],true);
                super::frogdrop_col::ring_cadd2(b,&ring,&q[118..],kb+118,mt-kb-118,sx[0],sub,&sc.zeros,c0,x128,&dirty);
                high_toggle(b,&[(ctl,false)],sx[0],true);
            }
        } else {ring_cadd2_loan(b, &ring, &q, kb, mt - kb, ctl, sub, &sc.zeros, c0, x128, &dirty, lsb, loan_end, x128);}'''
t=repl(t,old,new)
t=repl(t,'mc_xor(b, &ct, c, &[], &dirty);','if precision25 && kb==21 {q21_toggle(b,&ct,c);}else{mc_xor(b, &ct, c, &[], &dirty);}')
t=repl(t,'preposition_qk(b,&q129a,&fd.sy[..7],sx[6],21','preposition_nonlast_qk(b,&q129a,&fd.sy[..7],q[118],21')
t=repl(t,'preposition_qk(b,&q129b,&fd.sy,sx[6],21','preposition_nonlast_qk(b,&q129b,&fd.sy,q[118],21')
old='''super::payload::trans_one(b, &t, &src[..sl], kk, false, vec![(c, false)], None, sx[0], c0, &[],
                                          &pl.dirty);'''
new='''if precision25 {
                    // ak is returned zero here; mask the complete source rather
                    // than storing q21 in a zero pad needed by delayed HR.
                    q21_toggle(b,&[(c,false)],ak);
                    super::payload::trans_one(b,&t,&q[..118.min(t.len())],kk,false,vec![(ak,false)],None,sx[0],c0,&[],&pl.dirty);
                    q21_toggle(b,&[(c,false)],ak);
                    high_toggle(b,&[(c,false)],ak,false);
                    super::payload::trans_one(b,&t,&src[..sl],kk,false,vec![(ak,false)],None,sx[0],c0,&[],&pl.dirty);
                    high_toggle(b,&[(c,false)],ak,false);
                }else{super::payload::trans_one(b, &t, &src[..sl], kk, false, vec![(c, false)], None, sx[0], c0, &[],&pl.dirty);}'''
t=repl(t,old,new)
old='''Some(preposition_owned_qk(b, &q129b, &fd.sy, sx[1], k + 1, actl,
                                     (cp.sy.0.max(1), cp.sy.1.min(128)), &dirty))'''
new='''Some(rec(b,|b|{for &(lo,hi) in &[(cp.sy.0.max(1),cp.sy.1.min(101)),(cp.sy.0.max(103),cp.sy.1.min(128))]{if lo<=hi{let p=preposition_owned_qk(b,&q129b,&fd.sy,sx[1],k+1,actl,(lo,hi),&dirty);b.play(&p,false);}}}))'''
t=repl(t,old,new)
needle='            super::frogdrop_col::mark(b, 1501);'
t=repl(t,needle,'''            let pre16_102 = if precision25 && cp.sy.0<=102 && cp.sy.1>=102 {Some(preposition_owned_qk(b,&q129b,&fd.sy,sx[1],16,actl,(102,102),&dirty))}else{None};
'''+needle)
t=repl(t,'if let Some(p) = &pre21b { b.play(p, false); }\n            super::frogdrop_col::mark(b, 1502);','if let Some(p) = &pre21b { b.play(p, false); }\n            if let Some(p) = &pre16_102 { b.play(p,false); }\n            super::frogdrop_col::mark(b, 1502);')
t=repl(t,'super::frogdrop_col::mark(b, 1504);\n            if let Some(p) = &pre21b','super::frogdrop_col::mark(b, 1504);\n            if let Some(p) = &pre16_102 { b.play(p,false); }\n            if let Some(p) = &pre21b')
p.write_text(t)
# Rebind primitive owner test to the new conditional ordering, preserving v1.
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text()
a=t.index('fn n274_q21_owned_preposition_dirty_inverse_phase');tail=t[a:];head=t[:a]
tail=repl(tail,'super::midg::preposition_owned_qk(&mut b,&cycle,&sy,sx[1],16,control,(1,128),&dirty)','rec(&mut b,|b|{for range in [(1,101),(103,128)]{let p=super::midg::preposition_owned_qk(b,&cycle,&sy,sx[1],16,control,range,&dirty);b.play(&p,false);}})')
tail=repl(tail,'super::midg::preposition_qk(&mut b,&cycle,if mode==1{&sy}else{&sy[..7]},sx[6],21','super::midg::preposition_nonlast_qk(&mut b,&cycle,if mode==1{&sy}else{&sy[..7]},q[118],21')
tail=repl(tail,'let pre22=','let last=if mode==1{super::midg::preposition_owned_qk(&mut b,&cycle,&sy,sx[1],16,control,(102,102),&dirty)}else{vec![]};let pre22=')
tail=repl(tail,'b.play(&pre21,false);b.play(&pre22,false);','b.play(&pre21,false);b.play(&last,false);b.play(&pre22,false);')
tail=repl(tail,'input[sx[6].0 as usize]|=mask;','input[q[118].0 as usize]|=mask;')
tail=repl(tail,'if mode==1{swap(sx[1],size+16);}if size<=116{swap(sx[6],size+21);}','if mode==1&&size!=102{swap(sx[1],size+16);}if size<=116{swap(q[118],size+21);}if mode==1&&size==102{swap(sx[1],size+16);}')
tail=tail.replace('Q21_SX6_OWNER_PASS','Q21_Q118_OWNER_PASS').replace('width=691 scope=normalized_preposition_only','width=691 boundaries=97,102,115,116,117,118,119 scope=normalized_preposition_only')
p.write_text(head+tail)
# Source-bound high-Q masking fixture with an independent integer add oracle.
p=dest/'src/point_add/midg.rs';t=p.read_text()
start=t.index('        if precision25 {\n            // Q118 is never a carry')
end=t.index('\n        super::f1_profile("midg.ring_add"',start)
t=t[:start]+'''        if precision25 {q118_cadd(b,&ring,&q,&fd.sy,kb,mt-kb,ctl,sub,&sc.zeros,c0,x128,&dirty,lsb,loan_end,sx[0]);}
        else{ring_cadd2_loan(b,&ring,&q,kb,mt-kb,ctl,sub,&sc.zeros,c0,x128,&dirty,lsb,loan_end,x128);}'''+t[end:]
t+='''
// Production arithmetic excludes the quotient owner from every carry bank.
pub(crate) fn q118_cadd(b:&mut B,ring:&[QubitId],q:&[QubitId],sy:&[QubitId],kb:usize,span:usize,ctl:QubitId,sub:bool,zeros:&[QubitId],c0:QubitId,h:QubitId,dirty:&[QubitId],lsb:usize,loan_end:usize,flag:QubitId){
    ring_cadd2_loan(b,ring,&q[..118],kb,span,ctl,sub,zeros,c0,h,dirty,lsb.min(118),loan_end.min(118),h);
    if span>118{
        let toggle=|b:&mut B|{for (mask,value) in [(255usize,119usize),(248,120),(128,128)]{let mut lits=vec![(ctl,false)];lits.extend((0..8).filter(|i|mask>>i&1!=0).map(|i|(sy[i],value>>i&1==0)));mc_xor(b,&lits,flag,&[],dirty);}};
        toggle(b);super::frogdrop_col::ring_cadd2(b,ring,&q[118..],kb+118,span-118,flag,sub,zeros,c0,h,dirty);toggle(b);
    }
}
''';p.write_text(t)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text()
t+=r'''

#[test]
fn n274_q118_masked_add_all_sy_dirty_inverse_phase(){
    let mut total=0;
    for kb in [0usize,6,21]{
        let mut b=builder();let ring=b.alloc_n(274);let q=b.alloc_n(128);let sy=b.alloc_n(8);let sx=b.alloc_n(8);let ph=b.alloc();let pool=b.alloc_n(13);let dirty=b.alloc_n(259);assert_eq!(b.width(),691);
        let record=rec(&mut b,|b|super::midg::q118_cadd(b,&ring,&q,&sy,kb,129,ph,false,&[pool[10]],pool[11],pool[9],&dirty,128,128,sx[0]));
        let forward=emitted(&mut b,&record,false);let inverse=emitted(&mut b,&record,true);let ladder:Vec<_>=(kb..kb+129).map(|i|ring[273-i]).collect();let mut rng=Rng::new(0x20261014_1180+kb as u64);
        for block in 0..4{
            let mut input:Vec<_>=(0..691).map(|_|rng.next()).collect();for id in [ph,pool[10],pool[11],pool[9],sx[0]]{input[id.0 as usize]=0;}let mut expected=input.clone();let mut values=vec![];
            for lane in 0..64{let size=block*64+lane;put(&mut input,&sy,lane,N::from(size as u64));let active=(1..=128).contains(&size);let mut y=get(&input,&q,lane);
                if active{y&=(N::from(1u64)<<size)-N::from(1u64);y|=N::from(1u64)<<(size-1);put(&mut input,&q,lane,y);if size<=116 && lane%2==0{input[q[118].0 as usize]|=1u64<<lane;}input[ph.0 as usize]|=1u64<<lane;}
                values.push((y,active));
            }
            expected.clone_from(&input);let mask=(N::from(1u64)<<129)-N::from(1u64);
            for (lane,(y,active))in values.iter().enumerate(){if *active{let value=(get(&input,&ladder,lane)+*y)&mask;put(&mut expected,&ladder,lane,value);}}
            let got=run(&forward,691,&|w|*w=input.clone());assert_eq!(got.q,expected,"Q118 masked add kb{kb} block{block}; exact fullSY inclinactive dirtyowner");assert_eq!(got.phase,0);
            let back=run(&inverse,691,&|w|*w=got.q.clone());assert_eq!(back.q,input);assert_eq!(back.phase,0);total+=64;
        }
    }
    eprintln!("Q118_MASKED_ADD_PASS cases={total} full_SY_words=256 boundaries=116,117,118,119,128,255 inactive_dirty_owner=true all_wires_inverse=true phase=0 scope=source_bound_arithmetic_component");
}
'''
# Add actual original-packet HR/HT boundaries; retain existing failing v1 cases.
script=(source.parent/'qubit-add-k32-column-tests.py').read_text();prefix=script[script.index('def states(dx):'):script.index('\n\nselected={}')];ns={'P':2**256-2**32-977};exec(prefix,ns);states=ns['states'];P=ns['P'];selected={}
for line in (ev/'original-all-packet.tsv').read_text().splitlines():
    if line.startswith('#'):continue
    w=line.split();idx=int(w[0]);tx,ty,ox,oy,ex,ey=[int(x,16)for x in w[1:7]]
    for division,dx in ((1,(tx-ox)%P),(2,(ex-ox)%P)):
        for ci,state in enumerate(states(dx)):
            if state['kind'] in ('HR','HT') and state['sy_actual'] in (102,115,116,117,118,119,128):
                label=f"{state['kind']}_SY{state['sy_actual']}"
                if label not in selected:selected[label]=dict(label=label,shot=idx,division=division,dx=hex(dx),column=ci,**state)
    if len(selected)>=13:break
extra=[]
for label,row in sorted(selected.items()):
    a,z=row['before'],row['after'];extra.append('("'+label+'",'+str(row['column'])+',['+','.join('"'+format(v,'x')+'"'for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"'for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')')
a=t.index('fn n274_v2_full_column_new_boundaries_native');end=t.index('];let (cols',a);t=t[:end]+','+','.join(extra)+t[end:];p.write_text(t)
(ev/'n274-v2-extra-column-fixtures.json').write_text(json.dumps(dict(packet_sha256=hashlib.sha256((ev/'original-all-packet.tsv').read_bytes()).hexdigest(),cases=list(selected.values())),indent=2)+'\n')
changed=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines();assert len(changed)==6
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/']);(ev/'candidate-n274-v2.patch').write_bytes(patch)
manifest=dict(scope='N274-v2 Q118 q21 source-masked candidate; components pending, no builder authorized',base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),checkout=str(dest),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in changed})
(ev/'candidate-n274-v2-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
