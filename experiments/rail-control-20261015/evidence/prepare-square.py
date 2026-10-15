"""Integrate the archived exact square contract on the finite rail repair."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'square-room-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root.parent/'rail-margin-20261015/room-candidate.patch')],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root/'square-repair-input.patch')],check=True)
p=dest/'src/point_add/tests_positive_large.rs';s=p.read_text();assert s.count('for cap in [1234,1200]')==2
s=s.replace('for cap in [1234,1200]','for cap in [1267]')
s=s.replace('large_circuit(64,"SQ_B_POLICY",1200,true)','large_circuit(64,"SQ_B_POLICY",1267,true)');p.write_text(s)
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/'square-candidate.patch').write_bytes(patch)
protected={}
for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines():
    if not name.startswith('src/point_add/'):
        b=(dest/name).read_bytes();assert b==subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name]);protected[name]=hashlib.sha256(b).hexdigest()
(root/'square-manifest.json').write_text(json.dumps({'revision':rev,'score':None,'status':'prepared diagnostic','scope':'Unchanged archived exact square arithmetic, on cap1267/+1 interior rails/tick104 source. Native and all-MR component contracts rerun at cap1267; full fixed packets follow.','input_patch_sha256':hashlib.sha256((root/'square-repair-input.patch').read_bytes()).hexdigest(),'patch_sha256':hashlib.sha256(patch).hexdigest(),'protected_sha256':protected,'test_source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (dest/'src/point_add').glob('tests_positive*.rs')}},indent=2)+'\n')
