import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-phase-pebble-boundary-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists()and(old/'run-v2.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes();needle=b'const Y28_PLAN8:';assert raw.count(needle)==1
raw=raw.replace(needle,b'const Y28_PLAN7: ([usize; 12], [usize; 5]) = ([7,6,6,5,5,4,4,3,3,2,2,3], [0,2,4,6,8]);\n'+needle)
needle=b'fn ladder_drop(c: &mut Builder, acc: &[QubitId], add: &[Lin], lo0: usize, cin0: QubitId, plan: &[usize], drops: &[usize]) {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    let hard=super::super::phase_fit::cap();
    let selected=if hard<1234&&plan==Y28_PLAN8.0&&drops==Y28_PLAN8.1&&c.active_qubits()as usize+8>hard{
        assert!(c.active_qubits()as usize+7<=hard);Some((&Y28_PLAN7.0[..],&Y28_PLAN7.1[..]))
    }else if hard<1234&&plan==Y28_PLAN9.0&&drops==Y28_PLAN9.1&&c.active_qubits()as usize+9>hard{
        assert!(c.active_qubits()as usize+8<=hard);Some((&Y28_PLAN8.0[..],&Y28_PLAN8.1[..]))
    }else{None};
    let (plan,drops)=if let Some((p,d))=selected{eprintln!("PHASE_LOCAL_BOUNDARY_PLAN\\t{}\\t{}\\t{}\\t{:?}\\t{:?}",c.current_phase(),c.op_count(),c.active_qubits(),p,d);(p,d)}else{(plan,drops)};
''')
raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'Source-local recognized old Y28 plan8->native plan7 or9->8 when actual fixed storage requires1 wire. Original global walk/square planners, fold eligibility, windows/iterations and arithmetic contracts retained. Native oldplan7/8 and all exactphase components before control/candidate generation. No finalgate/nonce/score.'},indent=2)+'\n')
