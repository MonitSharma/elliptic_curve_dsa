"""Freeze exact carry borrowing before a deterministic capacity admission sweep."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-parity-integration-20261020'
assert not t.exists();assert(old/'run.exit').read_text().strip()=='0'and(old/'replay.exit').read_text().strip()=='0'
f=json.loads((old/'SOURCE_FREEZE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
base=f['base'];subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
for name in['builder.rs','record.rs','break_profile.rs','mod.rs','leapfrog.rs','parity_bridge.rs']:
    (t/'src/point_add'/name).write_bytes((old/'observer/src/point_add'/name).read_bytes())
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'    let break_cap = std::env::var("BREAK_CAP").expect("Diagnostic BREAK_CAP required");';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    let break_bridge=std::env::var("BREAK_BRIDGE").expect("Diagnostic bridge switch required");')
needle=b'std::env::set_var("LF_SQUARE_CAP", &break_cap);';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    std::env::set_var("PARITY_BRIDGE_ON",&break_bridge);');p.write_bytes(raw)
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes();needle=b'    const TARGET:usize=1200;';assert raw.count(needle)==1
raw=raw.replace(needle,b'    if std::env::var("PARITY_BRIDGE_ON").as_deref()!=Ok("1"){return false;}\n    let target=cells::cap();')
assert raw.count(b'.saturating_sub(TARGET)')==1;raw=raw.replace(b'.saturating_sub(TARGET)',b'.saturating_sub(target)')
needle=b'fn rail_add(c: &mut Builder, a: &[QubitId], b: &[QubitId], cin: Option<QubitId>) {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    if b.len()>=3&&!a.is_empty()&&!y28_pending(){
        let sign=*a.last().unwrap();
        let terms:Vec<Vec<QubitId>>=(0..b.len()).map(|i|vec![if i<a.len(){a[i]}else{sign}]).collect();
        if parity_bridge_try(c,b,&terms,cin){return;}
    }
''');p.write_bytes(raw)
assert len(f['protected_files'])==17 and all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':f['protected_files'],
    'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
    'cases':[[1234,False],[1234,True],[1233,True],[1230,True],[1226,True],[1224,True],[1200,True]],
    'scope':'Predeclared raw capacity admission only. Exact source-exclusive borrowing before rail splitting and in plain parity ladders; skip all pending hooks and paused callbacks. All arithmetic windows and iterations retained. No packet, final census, nonce or score.'},indent=2)+'\n')
