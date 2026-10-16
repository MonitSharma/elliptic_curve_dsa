"""Lease inside the uses' lexical LCA; globally initialize private flags."""
import shutil
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'scoped-cache-tool'
assert not d.exists()
shutil.copytree(r/'guard-cache-weighted-tool',d,ignore=shutil.ignore_patterns('target'))
p=d/'src/lazy_cache_retained.rs';s=p.read_text()
start=s.index('    let mut depth=0usize;let mut fence=0usize;')
stop=s.index('    let mut symbolic=',start)
s=s[:start]+'''    let mut guards=super::guard_bdd::analyze(&ops);
    let mut stack=vec![];let mut contexts=HashMap::<usize,Vec<usize>>::new();let mut pops=vec![usize::MAX;ops.len()];
    for (i,o) in ops.iter().enumerate() {
        if o.kind==K::CCX {contexts.insert(i,stack.clone());}
        match o.kind {K::PushCondition=>stack.push(i),K::PopCondition=>{let at=stack.pop().unwrap();pops[at]=i;},_=>{}}
    }
    assert!(stack.is_empty());
    let mut next=vec![usize::MAX;nq];let mut fences=vec![usize::MAX;ops.len()];
    for (i,o) in ops.iter().enumerate().rev(){
        if o.kind==K::CCX {fences[i]=next[o.q_control1.0 as usize].min(next[o.q_control2.0 as usize]);}
        match o.kind {K::X|K::CX|K::CCX|K::R|K::Hmr=>next[o.q_target.0 as usize]=i,
            K::Swap=>{next[o.q_target.0 as usize]=i;next[o.q_control1.0 as usize]=i;},_=>{}}
    }
'''+s[stop:]
start=s.index('    if std::env::var("CACHE_SEMANTIC_END")')
stop=s.index('    let mut proposals=',start)
s=s[:start]+s[stop:]
s=s.replace('                if !end_ok[*us.last().unwrap()] {continue;}','                let Some((start,end))=lease_bounds(&us,&contexts,&pops,&fences) else {continue;};')
s=s.replace('start:starts[us[0]],end:ends[*us.last().unwrap()]','start,end')
s=s.replace('            while uses.len()>1&&!end_ok[*uses.last().unwrap()] {uses.pop();}', '            while uses.len()>1&&lease_bounds(&uses,&contexts,&pops,&fences).is_none() {uses.pop();}')
s=s.replace('            if uses.len()<2 {continue;}\n            let weight_sum=', '            if uses.len()<2 {continue;}\n            let (start,end)=lease_bounds(&uses,&contexts,&pops,&fences).unwrap();\n            let weight_sum=')
s=s.replace('start:starts[uses[0]],end:ends[*uses.last().unwrap()]','start,end')
assert 'end_ok' not in s and 'starts[us' not in s
needle='fn gate(k:K,'
index=s.index(needle)
s=s[:index]+'''// First use starts the physical lease. Cleanup stays within the lexical
// common ancestor of every use: if any use activates valid, this ancestor's
// snapshotted guard is active. Flags are zero before every lease by induction
// from the unconditional global prefix and each guarded end/reset.
fn lease_bounds(uses:&[usize],contexts:&HashMap<usize,Vec<usize>>,pops:&[usize],fences:&[usize])->Option<(usize,usize)> {
    let first=uses[0];let last=*uses.last().unwrap();let a=&contexts[&first];let b=&contexts[&last];
    let common=a.iter().zip(b).take_while(|(x,y)|x==y).count();
    let end=if common==b.len(){last+1}else{pops[b[common]]+1};
    if fences[last]<end {None}else{Some((first,end))}
}
'''+s[index:]
needle='    for i in 0..=ops.len(){'
assert s.count(needle)==1
s=s.replace(needle,'''    let mut bases:Vec<_>=flags.values().copied().collect();bases.sort_unstable();
    println!("LAZY_GLOBAL_FLAGS bases={bases:?}");
    for base in bases {for b in base..base+3 {out.push(store(b,false));}}
'''+needle)
tests='''
    #[test]
    fn scoped_leases_borrow_busy_donor_under_independent_snapshots() {
        let mut p=program()[..10].to_vec();
        for bit in [0,1] {
            p.push(push(bit));
            p.extend([gate(K::X,None,None,Some(5),None,None),gate(K::X,None,None,Some(5),None,None)]);
            if bit==0 {p.push(gate(K::BitInvert,None,None,None,Some(0),None));}
            p.extend([gate(K::CCX,Some(0),Some(1),Some(4),None,None),gate(K::CCX,Some(0),Some(1),Some(4),None,None)]);
            p.extend([gate(K::X,None,None,Some(5),None,None),gate(K::X,None,None,Some(5),None,None),pop()]);
        }
        let q=optimize_impl(p.clone(),true);
        assert_eq!(q.iter().filter(|o|o.kind==K::Hmr).count(),2);
        for word in [0,u64::MAX,0xa5a5a5a5a5a5a5a5] {let mut saved=0;for batch in 0..8 {
            let (aq,bq,ab,bb,ap,bp,ac,bc)=run_case(&p,&q,batch,word);
            assert_eq!(aq,bq);assert_eq!(&ab[..4],&bb[..4]);assert_eq!(ap,bp);assert!(bb[4..7].iter().all(|v|*v==0));assert_eq!(&ab[7..],&bb[7..]);saved+=ac-bc;
        }assert_eq!(saved,512);}
    }
    #[test]
    fn scoped_sibling_cleanup_and_global_flag_initialization_are_required() {
        let mut p=program()[..10].to_vec();p.push(push(0));
        p.extend([gate(K::X,None,None,Some(5),None,None),gate(K::X,None,None,Some(5),None,None),push(1)]);
        let first=p.len();p.push(gate(K::CCX,Some(0),Some(1),Some(4),None,None));p.push(pop());
        p.push(gate(K::BitInvert,None,None,None,Some(1),None));p.push(push(1));
        let second=p.len();p.push(gate(K::CCX,Some(0),Some(1),Some(4),None,None));p.push(pop());
        p.push(gate(K::BitInvert,None,None,None,Some(1),None));let last=p.len();p.push(gate(K::CCX,Some(0),Some(1),Some(4),None,None));
        p.extend([gate(K::X,None,None,Some(5),None,None),gate(K::X,None,None,Some(5),None,None),pop()]);
        let q=render(p.clone(),vec![(5,Window{uses:vec![first,second,last],start:first,end:last+1,proxy:0.5,donors:vec![5]})],4,6);
        let bad=q[3..].to_vec();let mut fault=false;
        for word in [0,u64::MAX,0xa5a5a5a5a5a5a5a5] {let mut saved=0;for batch in 0..8 {
            let (aq,bq,ab,bb,ap,bp,ac,bc)=run_case(&p,&q,batch,word);assert_eq!(aq,bq);assert_eq!(&ab[..4],&bb[..4]);assert_eq!(ap,bp);assert!(bb[4..7].iter().all(|v|*v==0));saved+=ac-bc;
            let (aq,bq,_,_,ap,bp,_,_)=run_case(&p,&bad,batch,word);fault|=aq!=bq||ap!=bp;
        }assert_eq!(saved,256);}assert!(fault,"removing the global initialization must expose dirty private flags");
    }
'''
assert s.endswith('}\n');s=s[:-2]+tests+'}\n';p.write_text(s)
replay=r/'scoped-replay';assert not replay.exists()
shutil.copytree(r/'anchored-replay',replay,ignore=shutil.ignore_patterns('target'))
p=replay/'src/main.rs';s=p.read_text();needle='    let mut skipped=0;'
assert s.count(needle)==1
prefix='''    let global:Vec<_>=log.lines().filter_map(|l|l.strip_prefix("LAZY_GLOBAL_FLAGS bases=")).collect();
    assert!(global.len()<=1);
    if let Some(text)=global.first() {
        let bases:Vec<u64>=text.trim_start_matches('[').trim_end_matches(']').split(',').filter(|v|!v.trim().is_empty()).map(|v|v.trim().parse().unwrap()).collect();
        let expected:std::collections::BTreeSet<_>=flag_bases.values().copied().collect();
        assert_eq!(bases,expected.into_iter().collect::<Vec<_>>());
        for base in bases {for b in base..base+3 {emit(store(b,false),usize::MAX);}}
        let mut stack=vec![];let mut contexts=HashMap::<usize,Vec<usize>>::new();let mut pops=vec![usize::MAX;left.len()];
        for (i,o) in left.iter().enumerate(){if o.kind==K::CCX {contexts.insert(i,stack.clone());}match o.kind {K::PushCondition=>stack.push(i),K::PopCondition=>{pops[stack.pop().unwrap()]=i;},_=>{}}}
        assert!(stack.is_empty());
        for p in &plans {let first=p.uses[0];let last=*p.uses.last().unwrap();let a=&contexts[&first];let b=&contexts[&last];let common=a.iter().zip(b).take_while(|(x,y)|x==y).count();
            assert_eq!(p.start,first);assert_eq!(p.end,if common==b.len(){last+1}else{pops[b[common]]+1});
            let controls=[left[last].q_control1,left[last].q_control2];
            for o in &left[last+1..p.end] {match o.kind {K::X|K::CX|K::CCX|K::R|K::Hmr=>assert!(!controls.contains(&o.q_target)),K::Swap=>assert!(!controls.contains(&o.q_target)&&!controls.contains(&o.q_control1)),_=>{}}}
            for o in &left[p.start..p.end] {if o.kind!=K::R {assert!(![o.q_control1.0,o.q_control2.0,o.q_target.0].contains(&p.donor));}}
        }
    }
'''
s=s.replace(needle,prefix+needle);p.write_text(s)
print('Scoped leases plus unconditional private-flag prefix; independent full renderer and lexical/write/donor fence reconstruction ready.')
