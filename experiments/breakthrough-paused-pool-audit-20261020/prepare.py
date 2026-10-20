"""Trace the failed physical-pool contract, without changing arithmetic."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-paused-read-20261020'
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'
ad=json.loads((old/'ADMISSION-RESULT.json').read_text());assert [x['exit']for x in ad['cases']]==[0,101]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/builder.rs';raw=p.read_bytes()
needle=b'            let q = self.next_qubit;';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n            if q>=1233{eprintln!("NEW_PHYSICAL_ID\\t{}\\t{}\\t{}\\t{}\\t{}\\t{:?}\\t{:?}",self.phase,self.ops.len(),self.active_qubits,q,std::panic::Location::caller(),self.free_qubits,self.avoid_ids);}')
needle=b'    pub fn alloc_qubits(&mut self, n: usize) -> Vec<QubitId> {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n        if self.active_qubits as usize+n>=1233{eprintln!("ARRAY_ENTRY\\t{}\\t{}\\t{}\\t{}\\t{}",self.phase,self.ops.len(),self.active_qubits,n,std::panic::Location::caller());}')
needle=b'        self.active_qubits += 1;';assert raw.count(needle)==3
raw=raw.replace(needle,needle+b'\n        if self.active_qubits>=1233{eprintln!("LOGICAL_HIGH\\t{}\\t{}\\t{}\\t{}",self.phase,self.ops.len(),self.active_qubits,std::panic::Location::caller());}')
needle=b'        assert_eq!(sorted(&self.free_qubits), sorted(&before.0), "y42: the payload op changed the set of free wires");';assert raw.count(needle)==1
raw=raw.replace(needle,b'''        if sorted(&self.free_qubits)!=sorted(&before.0){
            eprintln!("FAILED_POOL_PREFIX\\t{}\\t{}\\t{}\\t{}",self.phase,self.ops.len(),self.active_qubits,self.next_qubit);
            super::break_profile::save_ops("failure-prefix.ops.bin",&self.ops);
        }
'''+needle);p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'observer-only.patch').write_bytes(subprocess.check_output(['git','diff','--no-index',str(old/'observer/src/point_add/builder.rs'),str(p)],check=False))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'Builder metadata only relative to failed paused-read source. Trace fresh physical IDs and array/logical high water; retain the y42 consistency assertion and dump only the failed debug prefix. Baseline full raw must remain13f6; candidate must preserve the same generation failure. No scored result or final gate.'},indent=2)+'\n')
