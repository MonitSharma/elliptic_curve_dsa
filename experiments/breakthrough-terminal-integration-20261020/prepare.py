import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-pebble-plan7-20261020';term=ws/'breakthrough-terminal-pebble-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());tf=json.loads((term/'SOURCE_FREEZE-v3.json').read_text())
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'and(term/'run-v3.exit').read_text().strip()=='0'
for parent,freeze,sub in[(old,f,'observer'),(term,tf,'primitive')]:assert all(sha(parent/sub/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for name in['phase_pebble.rs','terminal_pebble.rs']:(t/'src/point_add'/name).write_bytes((term/'primitive/src/point_add'/name).read_bytes())
# Restore all zero-carry source forms before exposing its true first carry.
p=t/'src/point_add/terminal_pebble.rs';raw=p.read_bytes();needle=b'c.ccx(q,acc[0],carry);hook(c,1,carry);';assert raw.count(needle)==1;raw=raw.replace(needle,b'c.ccx(q,acc[0],carry);')
needle=b'for &r in row[1..].iter().rev(){c.cx(r,q);}';assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'hook(c,1,carry);');p.write_bytes(raw)
with(t/'src/point_add/mod.rs').open('ab')as out:out.write(b'\nmod terminal_pebble;\n')
p=t/'src/point_add/modular.rs';raw=p.read_bytes();needle=b'    if go_copy0.is_none()&&c0==Carry0::Full&&c1==Carry1::Full&&deferred.is_none()&&known_output.is_none()&&known_terminal.is_none()&&borrowed.is_none(){';assert raw.count(needle)==1
raw=raw.replace(needle,b'''
    if go_copy0.is_none()&&c0==Carry0::Full&&c1==Carry1::Full&&deferred.is_none()&&known_output.is_none()&&borrowed.is_none()&&carry_out.is_none(){
        if let Some(desired)=known_terminal{if phase_known_modular(circ,addend,acc,carry_in,desired){return;}}
    }
'''+needle)
raw+=b'''
fn phase_known_modular(c:&mut Builder,a:&[QubitId],b:&[QubitId],cin:Option<QubitId>,desired:bool)->bool{
    let hard=super::phase_fit::cap();let n=b.len();if hard>=1234||a.is_empty()||a.len()>n||n<4{return false;}
    let need=(c.active_qubits()as usize+n-2).saturating_sub(hard);if need==0{return false;}
    // Original in-place source folding must not alias another source stage.
    if a.iter().map(|q|q.0).collect::<std::collections::BTreeSet<_>>().len()!=a.len(){return false;}
    let mut rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();rows.resize(n,Vec::new());let offset=usize::from(cin.is_none());
    let Some(drops)=super::phase_fit::choose(&rows[offset..],need,false,&vec![true;n-offset])else{return false;};
    let before=c.op_count();let active=c.active_qubits();
    if super::terminal_pebble::apply_with_hook(c,b,&rows,&vec![false;n],cin,&drops,desired,&mut|c,i,q|if i<=a.len(){dsq_apply(c,b[i-1],a[i-1],q);}){
        eprintln!("PHASE_KNOWN_TERMINAL\\t{}\\t{before}\\t{}\\t{active}\\t{n}\\t{}\\t{need}\\t{drops:?}",c.current_phase(),c.op_count(),usize::from(cin.is_some()));true
    }else{assert_eq!(before,c.op_count());false}
}
'''
term_source=(term/'primitive/src/point_add/modular.rs').read_bytes();raw+=term_source[term_source.index(b'#[cfg(test)]mod terminal_contract_tests{'):];p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'Integrate exact measured known-top channel on full plain original modular calls only: no output carry/copy/deferred/known-output/borrowed contracts, distinct physical source stages, zero/live cin. Preserve global DSQ_APPLY on true carry birth. Restore zero-carry source forms before hook. Original outer planners/windows/iterations remain. Native direct original-channel/deferred-phase regressions, exact13f6 baseline, then complete candidate construction. No finalgate/nonce/point-add score.'},indent=2)+'\n')
