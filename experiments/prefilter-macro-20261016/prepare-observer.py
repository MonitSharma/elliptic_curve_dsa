from pathlib import Path
import subprocess,shutil,json,hashlib
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');base=root.parent/'precision-repair-20261016/observer-tip';dest=root/'observer-tip'
subprocess.run(['git','-C',str(base),'worktree','add','--detach',str(dest),'4b2ec52fc55da796aa8f5ef851290297e8706424'],check=True)
shutil.copytree(base/'src/point_add',dest/'src/point_add',dirs_exist_ok=True)
p=dest/'src/point_add/fold_marks.rs';s=p.read_text().replace('precision-repair-20261016"','prefilter-macro-20261016"');assert s.count('ops.len());}')==1;s=s.replace('ops.len());}','ops.len());eprintln!("MACRO_MAP_COMPONENT_ONLY gate-inert raw source; no score");std::process::exit(0);}')
p.write_text(s)
p=dest/'src/point_add/y15_onefold.rs';s=p.read_text();needle='''        // y21, top cut: x257 (on m1) is measured first; x256 (on m0) holds X1[256]''';assert s.count(needle)==1;s=s.replace(needle,'''        eprintln!("MACRO_TOP1_ENTER rev={} tick={} at={}",rev,t,c.op_count());
'''+needle)
needle='''        c.push_condition(nbx);
        c.push_condition(bit0);
        let (rb, rrb) = chain(c);''';assert s.count(needle)==1;s=s.replace(needle,'''        eprintln!("MACRO_TOP1_FALSE_BEGIN rev={} tick={} at={} nbx={} bit0={}",rev,t,c.op_count(),nbx.0,bit0.0);
'''+needle+'''
        eprintln!("MACRO_TOP1_FALSE_CHAIN rev={} tick={} at={} scratch={:?}",rev,t,c.op_count(),rrb.iter().map(|x|x.0.0).collect::<Vec<_>>());''')
needle='''        cmp0(c, &rb);
        unchain(c, rrb);
        c.pop_condition();
        c.pop_condition();''';assert s.count(needle)==1;s=s.replace(needle,'''        eprintln!("MACRO_TOP1_FALSE_COMPARE_BEGIN rev={} tick={} at={}",rev,t,c.op_count());
        cmp0(c, &rb);
        eprintln!("MACRO_TOP1_FALSE_COMPARE_END rev={} tick={} at={}",rev,t,c.op_count());
        unchain(c, rrb);
        c.pop_condition();
        c.pop_condition();
        eprintln!("MACRO_TOP1_FALSE_END rev={} tick={} at={}",rev,t,c.op_count());''')
p.write_text(s)
# Trace all comparator call sites with source lines and raw operation positions.
p=dest/'src/point_add/compare.rs';s=p.read_text();needle='    if super::leapfrog::C35_TRACE {';assert s.count(needle)==1;s=s.replace(needle,'    if true {');p.write_text(s)
(root/'observer.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'observer-source.json').write_text(json.dumps(dict(base='4b2ec52fc55da796aa8f5ef851290297e8706424',gate_inert=True,component_only=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
