"""Fresh v3: generalized existing owner decoder accepts crossing reserve."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
source,dest,ev=map(lambda s:Path(s).resolve(),sys.argv[1:4])
assert not subprocess.check_output(['git','-C',str(dest),'status','--porcelain'],text=True).strip()
for name in subprocess.check_output(['git','-C',str(source),'diff','HEAD','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');shutil.copyfile(source/name,dest/name)
for relative in ['src/point_add/midg.rs','src/point_add/tests_midg_k24.rs']:
    p=dest/relative;t=p.read_text();old=t
    t=t.replace('preposition_nonlast_qk(b,&q129a,&fd.sy[..7],q[118],21','preposition_owned_qk(b,&q129a,&fd.sy[..7],q[118],21')
    t=t.replace('preposition_nonlast_qk(b,&q129b,&fd.sy,q[118],21','preposition_owned_qk(b,&q129b,&fd.sy,q[118],21')
    t=t.replace('preposition_nonlast_qk(&mut b,&cycle,if mode==1{&sy}else{&sy[..7]},q[118],21','preposition_owned_qk(&mut b,&cycle,if mode==1{&sy}else{&sy[..7]},q[118],21')
    assert t!=old; p.write_text(t)
changed=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--name-only'],text=True).splitlines();assert len(changed)==6
patch=subprocess.check_output(['git','-C',str(dest),'diff','HEAD','--','src/point_add/']);(ev/'candidate-n274-v3.patch').write_bytes(patch)
manifest=dict(scope='N274-v3 Q118 q21: accepts crossing reserve in owned decoder; components pending',base_revision=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip(),checkout=str(dest),candidate_changed_paths=changed,protected_files_modified=False,patch_sha256=hashlib.sha256(patch).hexdigest(),source_sha256={p:hashlib.sha256((dest/p).read_bytes()).hexdigest()for p in changed})
(ev/'candidate-n274-v3-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
