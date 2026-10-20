"""Read-only allocation/contract tracing on both frozen control streams."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fold-square-ripple-20261020'
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
    if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/builder.rs';raw=p.read_bytes();needle=b'        self.active_qubits += 1;'
assert raw.count(needle)==2
raw=raw.replace(needle,needle+b'\n        if self.active_qubits>=1233{eprintln!("HIGH_WATER\\t{}\\t{}\\t{}\\t{}\\t{}",self.phase,self.ops.len(),self.active_qubits,self.next_qubit,std::panic::Location::caller());}')
p.write_bytes(raw)
p=t/'src/point_add/modular.rs';raw=p.read_bytes();needle=b'    if go_copy0.is_some(){assert!(carry_in.is_none() && known_output.is_none() && owned>0);}'
assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    if circ.current_phase()=="square" && circ.active_qubits()as usize+owned>=1233{
        eprintln!("RIPPLE_CONTRACT\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",circ.op_count(),width,k,circ.active_qubits(),usize::from(c0==Carry0::Full),usize::from(c1==Carry1::Full),usize::from(deferred.is_some()),usize::from(known_output.is_some()),usize::from(known_terminal.is_some()),usize::from(borrowed.is_some()),usize::from(go_copy0.is_some()),usize::from(carry_out.is_some()));
    }
''');p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'controls':{'1234':'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b','1233':'d89649df7d74b8e93b9dbe40172e6f4fcffc84dc4473dfaca49b9101c8780f7c'},
 'scope':'Allocation/contract observation only. Both complete raw stream hashes must be unchanged; no new candidate or score.'},indent=2)+'\n')
