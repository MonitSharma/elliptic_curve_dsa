"""Separate reserve-bank R32 loan for SY96..103; source-bound precision experiment."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,re
source,dest,ev=map(lambda x:Path(x).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
def rep(t,a,z):
    assert a in t,a
    return t.replace(a,z)
p=dest/'src/point_add/payload.rs';t=p.read_text()
old='''            mc_xor(b, &l, th[i], temps, dirty);'''
new='''            // At midpoint, source prefix holds arbitrary up-ripple
            // values. Its last lane is the carry control; every earlier
            // source is disjoint from the tail and may be borrowed, then
            // restored before the down pass reads it again.
            let mut tail_dirty=dirty.to_vec();
            for &wire in &s[..s.len().saturating_sub(1)]{
                if !l.iter().any(|&(control,_)|control==wire)&&wire!=th[i]&&!tail_dirty.contains(&wire){tail_dirty.push(wire);}
            }
            mc_xor(b,&l,th[i],temps,&tail_dirty);'''
assert t.count(old)==1;t=t.replace(old,new);p.write_text(t)
p=dest/'src/point_add/midg.rs';t=p.read_text()
a=t.index('pub(crate) fn stage1_v_compact_partitioned(');z=t.index('///',a+20)
old=t[a:z];assert 'b.end()'in old
new=old.replace('stage1_v_compact_partitioned(','stage1_v_compact_bank_partition(').replace('small: bool) -> Vec<G>','small: bool, bank: bool) -> Vec<G>')
new=rep(new,'let selectors = size_partition(sy, small);','''let selectors=if bank {vec![vec![(sy[3],true),(sy[4],true),(sy[5],false),(sy[6],false)]]}
        else{vec![vec![(sy[0],true),(sy[1],true),(sy[2],true),(sy[3],true),(sy[4],true),(sy[5],true),(sy[6],true)],vec![(sy[3],false),(sy[5],false),(sy[6],false)],vec![(sy[4],false),(sy[5],false),(sy[6],false)]]};''')
# Bank96..103 = low7 1100xxx; complement active104..128 is104..111,
#112..127,128. These positive cubes are disjoint and never read SY7.
new=new.replace('vec![(sy[3],false),(sy[5],false),(sy[6],false)],vec![(sy[4],false),(sy[5],false),(sy[6],false)]','vec![(sy[3],false),(sy[4],true),(sy[5],false),(sy[6],false)],vec![(sy[4],false),(sy[5],false),(sy[6],false)]')
t=t[:z]+new+t[z:]
needle='    // enter / leave the V form on the act shots'
idx=t.index(needle)
t=t[:idx]+'''    // At both active V calls with SY96..103, every parked quotient
    // lies at index<=127. The complete reserve bank is therefore clean.
    // SW-as-SZ9 columns are excluded by ht25's cp.sz.1<=255 condition.
    let bank32=if ht25{
        let bank=[x128,c0,pzero,sx[6],sx[7],ph,sc.sw,fd.sy[7]];
        assert_eq!(bank.iter().copied().collect::<std::collections::BTreeSet<_>>().len(),8);
        assert!(!bank.iter().any(|id|zh.contains(id)||win.contains(id)||*id==act||*id==s1.f||*id==s1.zero||*id==s1.sgn||s1.gt.contains(id)||s1.anc.contains(id)||s1.andc.contains(id)||s1.chain.contains(id)||dirty.contains(id)||s1.r.contains(id)));
        let mut rs=s1.r.clone();rs.extend(bank);let bs=S1{r:rs,..s1.clone()};let z32=ring[n-32..n].to_vec();
        let f=stage1_v_compact_bank_partition(b,&z32,&win,&sc.sz,szr,&bs,act,true,&fd.sy,false,true);
        let r=stage1_v_compact(b,&z32,&win,&sc.sz,szr,&bs,act,false);
        let f24=stage1_v_compact_bank_partition(b,&zh,&win,&sc.sz,szr,&s1,act,true,&fd.sy,false,false);
        Some((f,r,f24))
    }else{None};
'''+t[idx:]
t=rep(t,'b.play(f25,false); b.play(&fr,true);','''if let Some((bf,br,f24))=&bank32{b.play(f24,false);b.play(&fr,true);b.play(bf,false);b.play(br,true);}
            else{b.play(f25,false);b.play(&fr,true);}''')
p.write_text(t)
p=dest/'src/point_add/tests_midg_k24.rs';t=p.read_text()
# Actual independently generated input; compile source-bound full-column oracle.
script=(source.parent/'qubit-add-k32-column-tests.py').read_text();prefix=script[script.index('def states(dx):'):script.index('\n\nselected={}')];ns={'P':2**256-2**32-977};exec(prefix,ns)
state=ns['states'](int('b99d62d1aa557c0a85f9ea89739eded4eb025ed76459a15b2551efaae60665bd',16))[86];assert state['quotient']==22815568
cases=[]
def case(label,state):
    a,z=state['before'],state['after'];return '("'+label+'",86,['+','.join('"'+format(v,'x')+'"'for v in a[:3])+'],'+','.join(str(v)for v in a[3:])+',['+','.join('"'+format(v,'x')+'"'for v in z[:3])+'],'+','.join(str(v)for v in z[3:])+')'
cases.append(case('fixed2379_div2',state))
P=ns['P'];Y=2**99+7;R=(Y-1)//2
for quotient in [2**24-1,2**24,2**25-1,2**25]:
    X=quotient*Y+R;zb=(-2*P)%Y;Z=P//X-((P//X-zb)%Y);Tp=(P-Z*X)//Y;Zn=Tp+quotient*Z
    assert Z>0 and 0<=Tp<Z and Z*X+Tp*Y==P and Zn*Y+Z*R==P
    s=dict(before=[Z,Y,X,100,1,0],after=[Zn,R,Y,100,1,0]);cases.append(case('q'+str(quotient),s))
a=t.index('#[test]\nfn n275_v2_full_column_new_boundaries_native');z=t.find('#[test]',a+10);z=len(t)if z<0 else z;test=t[a:z];test=test.replace('n275_v2_full_column_new_boundaries_native','ht25_fixed2379_and_quotient_boundaries_native')
x=test.index('let cases=&[')+len('let cases=&[');y=test.index('];let (cols',x);test=test[:x]+','.join(cases)+test[y:]
old='assert_eq!(got.q,expected,"case {label} col{ci} exact Euclid shadow plus all scratch/passengers");assert_eq!(got.phase,0,"case {label}");'
test=rep(test,old,'''if label=="q33554432"{assert_ne!(got.q,expected,"above capacity has no fallback");eprintln!("HT25_ABOVE_CAPACITY_EXPECTED_NEGATIVE quotient=33554432");continue;}
        assert_eq!(got.q,expected,"case {label} col{ci} exact Euclid shadow plus all scratch/passengers");assert_eq!(got.phase,0,"case {label}");''')
test=test.replace('N275_NEW_BOUNDARY_CASE_PASS','HT25_FULL_COLUMN_CASE_PASS').replace('N275_NEW_BOUNDARY_SUITE_PASS','HT25_FULL_COLUMN_SUITE_PASS')
t+='\n'+test
# Normal HT payload uses the previous-R boundary and its positive offset.
a=t.index('#[test]\nfn reserve9_crossing_payload_3713_exact_shadow_native');z=t.index('#[test]',a+10);test=t[a:z]
for old,new in [('reserve9_crossing_payload_3713_exact_shadow_native','ht25_fixed2379_exact_payload_native'),('dbc03838c8e3ef33e7b222ced5415f372fbdf32febb8ead3f55c4e58c4f81f55','b99d62d1aa557c0a85f9ea89739eded4eb025ed76459a15b2551efaae60665bd'),('let j=60','let j=86'),('cols[60]','cols[86]'),('assert!(cp.psw&&cp.ht)','assert!(!cp.psw&&cp.ht)'),('371300','237900'),('pre_boundary=258-t[j].bit_len()','pre_boundary=r[j-1].bit_len()'),('else{w.bit(258-l)}','else{w.wrapping_add(N::from(1u64)<<(258-pre_boundary)).bit(258-l)}'),('&rev[..r[j-1].bit_len()],lane,r[j-1]','&rev[..r[j].bit_len()],lane,r[j]'),('&q,lane,r[j]','&q,lane,r[j-1]'),('N::from(r[j-1].bit_len()as u64)','N::from(r[j].bit_len()as u64)'),('RESERVE9_PAYLOAD','HT25_PAYLOAD'),('column=60 euclid_step=60 first_HT_refill=true quotient=375614','column=86 euclid_step=86 first_HT_refill=false quotient=22815568')]:test=rep(test,old,new)
# The broad replacement above also affected expected Q: its expected Y
# remains r[j], as specified by the independent arithmetic recurrence.
test=rep(test,'put(&mut expected,&q,lane,r[j-1])','put(&mut expected,&q,lane,r[j])')
test=rep(test,'2=>p-N::from(1u64),_=>','2=>p-N::from(1u64),3=>r[j-1]-N::from(1u64),4=>r[j]-N::from(1u64),_=>')
t+='\n'+test;p.write_text(t)
changed=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines();assert all(p.startswith('src/point_add/')for p in changed)
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/']);(ev/'candidate-ht25-v2.patch').write_bytes(patch)
manifest=dict(scope='HT25 storage plus R32 reserve-bank loan SY96..103; component pending; SY104+ precision and above-capacity excluded from general guarantee',base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),checkout=str(dest),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in changed})
(ev/'candidate-ht25-v2-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
