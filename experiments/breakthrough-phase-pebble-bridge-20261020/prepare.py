"""One more legal existing Cuccaro bridge only when the hard limit needs it."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-pebble-modular-20261020';audit=ws/'breakthrough-phase-modular-audit-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'and(audit/'run.exit').read_text().strip()=='0'
ad=json.loads((old/'ADMISSION-RESULT.json').read_text());assert[x['exit']for x in ad['cases']]==[0,101]
assert json.loads((audit/'MODULAR-STORAGE-AUDIT.json').read_text())['cases'][1]['fresh_ids'][0].split('\t')[2:4]==['1234','1233']
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/bridge.rs';raw=p.read_bytes();needle=b'    let owned=if cout.is_some(){n-1}else{n-2};assert!(bridges<owned);';assert raw.count(needle)==1
raw=raw.replace(needle,b'''    let owned=if cout.is_some(){n-1}else{n-2};
    let hard=super::phase_fit::cap();
    let need=if hard<1234{(c.active_qubits()as usize+owned-bridges).saturating_sub(hard)}else{0};
    let desired=bridges+need;
    let bridges=if need>0&&desired<owned&&(owned-desired..owned).all(|i|a.iter().filter(|&&q|q==a[i]).count()==1&&Some(a[i])!=cin){
        eprintln!("PHASE_EXTRA_BRIDGE\\t{}\\t{}\\t{}\\t{n}\\t{bridges}\\t{desired}",c.current_phase(),c.op_count(),c.active_qubits());desired
    }else{bridges};
    assert!(bridges<owned);''');p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],
 'scope':'Retain fresh phase-pebble source. Increase existing contiguous direct bridge count only when actual owned-carry admission exceeds hardcap and every bridge pivot is unique across the full source and distinct from cin; keep count<owned. Original split wrapper decisions, windows, iterations and protected17 unchanged. Exact13f6 control; no final gate/nonce or score.'},indent=2)+'\n')
