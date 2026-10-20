import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-budget-c3-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v2.json').read_text())
assert not t.exists() and (old/'run-v2.exit').read_text().strip()=='0'
assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
needle=b'    let core_room=cells::cap().saturating_sub(after_tt);';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    eprintln!("C3_ACTIVATION\\t{}\\t{}\\t{}\\t{}\\t{mw}\\t{drop}\\t{fin}\\t{ttm}\\t{core_room}",c.current_phase(),c.op_count(),c.active_qubits(),super::super::phase_fit::cap());\n')
needle=b'        let t = and_new(c, k1, k2);\n        let mut at:';start=raw.index(b'struct T0Phase');end=raw.index(b'\n}',raw.index(b'impl T0Phase',start))+2;region=raw[start:end];assert region.count(needle)==1
region=region.replace(needle,b'        eprintln!("T0_ACTIVATION\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",c.current_phase(),c.op_count(),c.active_qubits(),super::super::phase_fit::cap(),k1.0,k2.0);\n'+needle);raw=raw[:start]+region+raw[end:];p.write_bytes(raw)
subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'Metadata only activation audit; require exact 13f6 and 99b8 full stream reproduction. No final gate or score.'},indent=2)+'\n')
