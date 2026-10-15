"""Scratch-only control: exactly the prior room variant with original rail table."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'scratch-only-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root.parent/'rail-margin-20261015/room-candidate.patch')],check=True)
rel='src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt'
(dest/rel).write_bytes(subprocess.check_output(['git','-C',str(dest),'show',rev+':'+rel]))
control=root.parent/'rail-margin-20261015/margin-room-b3'
different=[];protected={}
for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines():
    b=(dest/name).read_bytes()
    if b!=(control/name).read_bytes():different.append(name)
    if not name.startswith('src/point_add/'):
        assert b==subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name]);protected[name]=hashlib.sha256(b).hexdigest()
assert different==[rel],different
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/'candidate.patch').write_bytes(patch)
(root/'manifest.json').write_text(json.dumps({'revision':rev,'score':None,'status':'prepared diagnostic','hypothesis':'Separate interior rail headroom from the existing planner cap1267; tick104 repair and all other sources identical to room variant.','only_difference_from_room_variant':different,'patch_sha256':hashlib.sha256(patch).hexdigest(),'protected_sha256':protected},indent=2)+'\n')
