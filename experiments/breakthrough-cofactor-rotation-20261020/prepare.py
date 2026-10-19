"""Transfer the incumbent's exact three-reflection rotation to the component."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive'
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
assert not t.exists()
old=ws/'breakthrough-cofactor-update-20261020'
assert(old/'run.exit').read_text().strip()=='0'
previous=json.loads((old/'SOURCE_FREEZE.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(old/'primitive'/p)==h for p,h in {**previous['source_files'],**previous['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
protected=previous['protected_files'];assert all(sha(t/p)==h for p,h in protected.items())
for name in ['cofactor_history.rs','cofactor_update.rs','mod.rs','leapfrog.rs']:
    (t/'src/point_add'/name).write_bytes((old/'primitive/src/point_add'/name).read_bytes())
p=t/'src/point_add/cofactor_update.rs';raw=p.read_bytes()
old_call=b'rotate(c,word,-2,Some(k2));rotate(c,word,-1,Some(k1));rotate(c,word,-3,None);'
assert raw.count(old_call)==1
raw=raw.replace(old_call,b'rotate_four(c,word,k1,k2,false);rotate(c,word,-3,None);')
old_call=b'rotate(c,word,3,None);rotate(c,word,1,Some(k1));rotate(c,word,2,Some(k2));'
assert raw.count(old_call)==1
raw=raw.replace(old_call,b'rotate(c,word,3,None);rotate_four(c,word,k1,k2,true);')
assert raw.count(b'count(),93);')==1
raw=raw.replace(b'count(),93);',b'count(),86);')
raw+=(r/'rotation.rs').read_bytes()
p.write_bytes(raw)
(r/'cofactor_update.rs').write_bytes(raw)
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'status':'ROTATION_COMPONENT_ONLY','protected_files':protected,
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'Existing exact reflection construction replaces two cyclic shifts. Inherited six component controls plus exhaustive small word and formula checks; no point-add candidate.'},indent=2)+'\n')
