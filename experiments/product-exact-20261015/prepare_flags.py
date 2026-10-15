from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dest=root/'flags-tool'
shutil.copytree(root/'analyzer',dest,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
for name in ['lazy_cache_retained.rs','lazy_cache_anf.rs']:
    path=dest/'src'/name;text=path.read_text()
    needle='    let mut starts:HashMap<usize,Vec<usize>>=HashMap::new();'
    assert text.count(needle)==1
    text=text.replace(needle,'''    // Each donor's selected leases are disjoint. Three private classical
    // flags are reset before and after every lease, at top-level boundaries.
    // Snapshotted PushCondition scopes end before this reset/reuse boundary.
    let donors:std::collections::BTreeSet<_>=chosen.iter().map(|(q,_)|*q).collect();
    let flags:HashMap<usize,u64>=donors.into_iter().enumerate().map(|(j,q)|(q,nb+3*j as u64)).collect();
    for (j,(q,_)) in chosen.iter().enumerate(){println!("LAZY_FLAG lease={j} base={}",flags[q]);}
'''+needle)
    text=text.replace('nb+3*j as u64','flags[q]',2) if False else text
    # Every render-time reference to the old lease-index flags is replaced
    # with the donor-index assignment; the mapping definition stays intact.
    text=text.replace('let valid=nb+3*j as u64;', 'let valid=flags[q];')
    text=text.replace('for b in nb+3*j as u64..nb+3*j as u64+3', 'for b in flags[q]..flags[q]+3')
    text=text.replace('let q=chosen[j].0 as u64;let valid=nb+3*j as u64;', 'let q=chosen[j].0 as u64;let valid=flags[&(q as usize)];')
    # q is u64 only at a use; earlier generic replacement uses flags[q].
    text=text.replace('let q=chosen[j].0 as u64;let valid=flags[q];', 'let q=chosen[j].0 as u64;let valid=flags[&(q as usize)];')
    text=text.replace('assert!(bb[4..10].iter().all(|b|*b==0));','assert!(bb[4..7].iter().all(|b|*b==0));assert_eq!(&ab[7..],&bb[7..]);')
    path.write_text(text)
# Independent complete-operation reconstruction understands the explicit
# flag map, retaining the original fallback for all frozen historical stages.
replay=root/'flags-replay'
shutil.copytree(root/'exact-replay',replay,ignore=shutil.ignore_patterns('target'),dirs_exist_ok=True)
path=replay/'src/main.rs';text=path.read_text()
needle='    assert!(!plans.is_empty());let mut start='
assert text.count(needle)==1
text=text.replace(needle,'''    let mut flag_bases=std::collections::HashMap::<usize,u64>::new();
    for line in log.lines().filter(|l|l.starts_with("LAZY_FLAG ")) {
        let field=|name:&str|->u64{line.split_whitespace().find_map(|s|s.strip_prefix(name)).unwrap().parse().unwrap()};
        assert!(flag_bases.insert(field("lease=")as usize,field("base=")).is_none());
    }
    let flag=|j:usize|->u64{flag_bases.get(&j).copied().unwrap_or(nb+3*j as u64)};
    assert!(!plans.is_empty());let mut start=''')
text=text.replace('let v=nb+3*j as u64;', 'let v=flag(j);')
text=text.replace('for b in nb+3*j as u64..nb+3*j as u64+3', 'for b in flag(j)..flag(j)+3')
path.write_text(text)
