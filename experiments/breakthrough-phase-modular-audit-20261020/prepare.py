"""Metadata-only trace of the frozen modular integration's t87 failure."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-pebble-modular-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0';ad=json.loads((old/'ADMISSION-RESULT.json').read_text());assert [x['exit']for x in ad['cases']]==[0,101]
assert'y42: the payload op changed the set of free wires'in ad['cases'][1]['failure_tail'];assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
def edit(name,needle,replacement):
 p=t/'src/point_add'/name;raw=p.read_bytes();assert raw.count(needle)==1,(name,needle,raw.count(needle));p.write_bytes(raw.replace(needle,replacement))
needle=b'            let q = self.next_qubit;';edit('builder.rs',needle,needle+b'\n            if q>=1233{eprintln!("NEW_PHYSICAL_ID\\t{}\\t{}\\t{}\\t{}\\t{}\\t{:?}\\t{:?}",self.phase,self.ops.len(),self.active_qubits,q,std::panic::Location::caller(),self.free_qubits,self.avoid_ids);}')
needle=b'        assert_eq!(sorted(&self.free_qubits), sorted(&before.0), "y42: the payload op changed the set of free wires");'
edit('builder.rs',needle,b'        if sorted(&self.free_qubits)!=sorted(&before.0){super::break_profile::save_ops("failure-prefix.ops.bin",&self.ops);eprintln!("FAILED_POOL_PREFIX\\t{}\\t{}\\t{}\\t{}",self.phase,self.ops.len(),self.active_qubits,self.next_qubit);}\n'+needle)
needle=b'fn lin_and(c: &mut Builder, a: &Lin, b: &Lin) -> QubitId {'
edit('leapfrog.rs',needle,b'#[track_caller]\n'+needle+b'\n    if c.active_qubits()>=1232{eprintln!("LIN_ALLOC_SITE\\t{}\\t{}\\t{}\\t{}",c.current_phase(),c.op_count(),c.active_qubits(),std::panic::Location::caller());}')
needle=b'fn m_carry(c: &mut Builder, acc: QubitId, add: &Lin, ci: QubitId) -> QubitId {';edit('leapfrog.rs',needle,b'#[track_caller]\n'+needle)
needle=b'fn phase_chunk_try(c:&mut Builder,acc:&[QubitId],add:&[Lin],cin:QubitId,output:bool,direct:bool)->Option<Option<QubitId>>{'
edit('leapfrog.rs',needle,needle+b'''
    let owned_trace=if output{acc.len()}else{acc.len().saturating_sub(1+usize::from(direct))};
    if c.active_qubits()as usize+owned_trace>=1233{let rows:Vec<_>=add.iter().map(|v|v.w.clone()).collect();eprintln!("CHUNK_ADMISSION\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",c.current_phase(),c.op_count(),c.active_qubits(),acc.len(),usize::from(output),usize::from(direct),owned_trace,usize::from(super::phase_fit::source_ok(acc,&rows,cin)));}
''')
needle=b'    if go_copy0.is_some(){assert!(carry_in.is_none() && known_output.is_none() && owned>0);}'
edit('modular.rs',needle,needle+b'''
    if circ.active_qubits()as usize+owned>=1233{eprintln!("MODULAR_CONTRACT\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",circ.current_phase(),circ.op_count(),circ.active_qubits(),width,usize::from(c0==Carry0::Full),usize::from(c1==Carry1::Full),usize::from(deferred.is_some()),usize::from(known_output.is_some()),usize::from(known_terminal.is_some()),usize::from(borrowed.is_some()),usize::from(go_copy0.is_some()));}
''')
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'scope':'Metadata-only on frozen failed t87 source. Trace true carry/Lin allocation callers, chunk admission, modular contracts and fresh IDs. Keep Y42 consistency assertions. Complete control must remain13f6 and same candidate failure must reproduce. Debug prefix explicitly incomplete; no score/final gate/nonce.'},indent=2)+'\n')
