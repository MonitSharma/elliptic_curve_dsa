"""Exact source-allocation profile; no input-packet data or arithmetic edits."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-paused-pool-audit-20261020'
assert not t.exists()and(old/'run-v2.exit').read_text().strip()=='0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
def edit(name,needle,replacement):
 p=t/'src/point_add'/name;raw=p.read_bytes();assert raw.count(needle)==1,(name,needle,raw.count(needle));p.write_bytes(raw.replace(needle,replacement))
needle=b'    let ((), peak) = c.r3_peak(|c| body(c, t, s, k1, k2, b, tg, proxy, rev));'
edit('y15_onefold.rs',needle,b'    let storage_a=c.active_qubits();let storage_op=c.op_count();\n'+needle+b'\n    eprintln!("BODY_STORAGE\\t{}\\t{t}\\t{}\\t{storage_a}\\t{peak}\\t{storage_op}\\t{}",c.current_phase(),usize::from(rev),c.op_count());')
needle=b'fn lin_and(c: &mut Builder, a: &Lin, b: &Lin) -> QubitId {'
edit('leapfrog.rs',needle,b'#[track_caller]\n'+needle+b'\n    if c.active_qubits()>=1232{eprintln!("LIN_ALLOC_SITE\\t{}\\t{}\\t{}\\t{}",c.current_phase(),c.op_count(),c.active_qubits(),std::panic::Location::caller());}')
needle=b'fn m_carry(c: &mut Builder, acc: QubitId, add: &Lin, ci: QubitId) -> QubitId {'
edit('leapfrog.rs',needle,b'#[track_caller]\n'+needle)
needle=b'fn m_fold_y16(c: &mut Builder, acc: &[QubitId], ov: QubitId, recs: &mut Recs, plan: &[usize], k: usize,\r\r\n          hook: impl FnOnce(&mut Builder, &mut Recs, [Lin; 4], bool) -> Vec<Lin>) {'
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes()
if needle not in raw:needle=needle.replace(b'\r\r\n',b'\n')
assert raw.count(needle)==1
wrapper=b'''#[track_caller]
fn m_fold_y16(c: &mut Builder, acc: &[QubitId], ov: QubitId, recs: &mut Recs, plan: &[usize], k: usize,
          hook: impl FnOnce(&mut Builder, &mut Recs, [Lin; 4], bool) -> Vec<Lin>) {
    let active=c.active_qubits();let from=c.op_count();let caller=std::panic::Location::caller();
    let((),peak)=c.r3_peak(|c|m_fold_y16_inner(c,acc,ov,recs,plan,k,hook));
    eprintln!("GENERIC_FOLD_STORAGE\\t{}\\t{from}\\t{}\\t{active}\\t{peak}\\t{}\\t{k}\\t{caller}",c.current_phase(),c.op_count(),acc.len());
}
'''
p.write_bytes(raw.replace(needle,wrapper+needle.replace(b'fn m_fold_y16(',b'fn m_fold_y16_inner(')))
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'Metadata only on original-planner failed paused source: Y15 body and generic-fold allocation peaks, true Lin/carry callers. Require complete original13f6 and failed candidate debug-prefix66ba9d6c byte identity. Profiles concern exact construction storage, never empirical arithmetic cuts or packet tuning.'},indent=2)+'\n')
