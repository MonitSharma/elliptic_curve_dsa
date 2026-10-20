import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fold-square-ripple-20261020'
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
    if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/modular.rs';raw=p.read_bytes()
needle=b'&&known_terminal.is_none()&&borrowed.is_none(){';assert raw.count(needle)==1;raw=raw.replace(needle,b'&&borrowed.is_none(){')
needle=b'if c.current_phase()!="square"||a.len()!=b.len(){return false;}';assert raw.count(needle)==1
raw=raw.replace(needle,b'if c.current_phase()!="square"||a.is_empty()||a.len()>b.len(){return false;}')
needle=b'let mut target=b.to_vec();let mut terms:Vec<Vec<QubitId>>=a.iter().map(|&q|vec![q]).collect();';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    terms.resize(b.len(),Vec::new()); // Exact zero-extension, no extra quantum wires.')
needle=b'let first=usize::from(cin.is_none());if first+need>n-2{return false;}\n    let indices:Vec<_>=(first..first+need).collect();';assert raw.count(needle)==1
raw=raw.replace(needle,b'''let first=usize::from(cin.is_none());
    let mut counts=std::collections::BTreeMap::new();for row in &terms{for q in row{*counts.entry(q.0).or_insert(0usize)+=1;}}
    let mut indices:Vec<_>=(first..n-2).filter(|&i|terms[i].iter().any(|q|counts[&q.0]==1&&Some(*q)!=cin)).collect();
    if indices.len()<need{return false;}indices.truncate(need);''');p.write_bytes(raw)
p=t/'src/point_add/parity_bridge.rs';p.write_bytes(p.read_bytes()+(r/'short-source-tests.rs').read_bytes())
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233],'scope':'Zero-extended source words in exact square carries. Full addition satisfies any inherited terminal-bit promise without relying on it; preserve copy/deferred/known-output/external-carry contracts. No windows/iterations changed; resource feasibility only.'},indent=2)+'\n')
