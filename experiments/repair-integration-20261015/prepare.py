"""Combine the independently tested square repair and longer wider walk."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;old=root.parent/'rail-control-20261015';dest=root/'combined-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
for p in [old/'margin3-tail2.patch',old/'square-repair-input.patch']:subprocess.run(['git','-C',str(dest),'apply',str(p)],check=True)
p=dest/'src/point_add/tests_positive_large.rs';s=p.read_text();assert s.count('for cap in [1234,1200]')==2
s=s.replace('for cap in [1234,1200]','for cap in [1267]').replace('large_circuit(64,"SQ_B_POLICY",1200,true)','large_circuit(64,"SQ_B_POLICY",1267,true)');p.write_text(s)
for rel in ['square.rs','tests_positive_bias.rs','tests_positive_large.rs','tests_positive_phase_polynomial.rs']:
    assert (dest/'src/point_add'/rel).read_bytes()==(old/'square-room-b3/src/point_add'/rel).read_bytes(),rel
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/'combined.patch').write_bytes(patch)
protected={}
for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines():
    if not name.startswith('src/point_add/'):
        b=(dest/name).read_bytes();assert b==subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name]);protected[name]=hashlib.sha256(b).hexdigest()
(root/'combined-manifest.json').write_text(json.dumps({'revision':rev,'score':None,'status':'prepared diagnostic','scope':'Cap1267, +3 interior rails,140 rounds,tick104 fold repair,and exact +2 square contract. Square arithmetic/test files byte-identical to prior tested integration.','patch_sha256':hashlib.sha256(patch).hexdigest(),'protected_sha256':protected},indent=2)+'\n')
