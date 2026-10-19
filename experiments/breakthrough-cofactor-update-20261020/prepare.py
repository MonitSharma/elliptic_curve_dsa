import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive'
assert not t.exists()
old=ws/'breakthrough-cofactor-history-20261020'
receipt=json.loads((old/'NATIVE-RESULT.json').read_text());assert receipt['tests']==3
oldfreeze=json.loads((old/'NATIVE-SOURCE-FREEZE-v2.json').read_text())
source=old/'primitive/src/point_add/cofactor_history.rs'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==oldfreeze['source_files']['src/point_add/cofactor_history.rs']
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={name:sha(t/name)for name in paths if not name.startswith('src/point_add/')};assert len(protected)==17
codec=source.read_bytes().replace(b'fn erase_history(',b'pub(super) fn erase_history(',1)
codec+=(r/'restore-history.rs').read_bytes()
(t/'src/point_add/cofactor_history.rs').write_bytes(codec)
(r/'cofactor_history.rs').write_bytes(codec)
(t/'src/point_add/cofactor_update.rs').write_bytes((r/'cofactor_update.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as f:f.write(b'\nmod cofactor_history;\nmod cofactor_update;\n')
wrapper=b'''
/// Diagnostic component access to the existing phase-correct carry ladder.
pub(crate) fn cofactor_diagnostic_add(c:&mut Builder,acc:&[QubitId],add:&[QubitId],cin:QubitId){
    let terms:Vec<Vec<QubitId>>=add.iter().map(|&q|vec![q]).collect();
    ladder_parity_add(c,acc,&terms,Some(cin));
}
'''
with(t/'src/point_add/leapfrog.rs').open('ab')as f:f.write(wrapper)
assert all(sha(t/name)==h for name,h in protected.items())
freeze={'status':'NATIVE_ADJOINT_COFACTOR_UPDATE_COMPONENT_ONLY','base':base,'protected_files':protected,
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'Complete signed bounded-word cofactor update, variable shift, 4-flag erasure and inverse. Not integrated into point addition. Integer allocation, endpoint and normalization unresolved.'}
(r/'SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n')
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
