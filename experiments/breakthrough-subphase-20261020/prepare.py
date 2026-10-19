import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-cap-cost-20261020/observer'
assert not t.exists()
assert(ws/'breakthrough-cap-cost-20261020/continuation-v3.exit').read_text().strip()=='0'
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={name:sha(t/name)for name in paths if not name.startswith('src/point_add/')};assert len(protected)==17
for name in['builder.rs','record.rs','break_profile.rs','mod.rs']:(t/'src/point_add'/name).write_bytes((old/'src/point_add'/name).read_bytes())
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes()
oldmark=b'    c.expected_total()'
start=raw.index(b'fn pmark(c: &Builder) -> f64 {');end=raw.index(b'fn pacc(',start)
part=raw[start:end];assert part.count(oldmark)==1
part=part.replace(oldmark,b'''    let value=c.expected_total();
    let native=c.report_totals().expect("Diagnostic phase counters required").0;
    BREAK_MARKS.with(|m| {
        let mut m=m.borrow_mut();let key=(c as *const Builder as usize,value.to_bits());
        match m.entry(key) {
            std::collections::hash_map::Entry::Occupied(e)=>assert_eq!(e.get().1,native,"Expected-weight collision crossed a scored gate"),
            std::collections::hash_map::Entry::Vacant(e)=>{e.insert((c.op_count(),native));}
        }
    });
    value''')
raw=raw[:start]+part+raw[end:]
needle=b'fn pacc(c: &Builder, name: &str, t0: f64) {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    BREAK_MARKS.with(|m| {
        let map=m.borrow();let &(start,_)=map.get(&(c as *const Builder as usize,t0.to_bits())).expect("Diagnostic mark absent");
        eprintln!("BREAK_REGION\\t{}\\t{}\\t{}\\t{}",c.current_phase(),name,start,c.op_count());
    });''')
raw+=b'''
thread_local! { static BREAK_MARKS:std::cell::RefCell<std::collections::HashMap<(usize,u64),(usize,usize)>> = const { std::cell::RefCell::new(std::collections::HashMap::new()) }; }
'''
p.write_bytes(raw)
assert all(sha(t/name)==h for name,h in protected.items())
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'scope':'Raw accepted arithmetic region observation only','expected_native_raw_sha256':'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b','protected_files':protected,'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()}},indent=2)+'\n')
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
