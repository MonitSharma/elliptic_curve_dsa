"""Predetermined larger rail margin, with a separate two-round tail control."""
from pathlib import Path
import subprocess,hashlib,json,sys
root=Path(__file__).resolve().parent;mode=sys.argv[1];assert mode in ['margin3','margin3-tail2']
dest=root/(mode+'-b3');assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root.parent/'rail-margin-20261015/room-candidate.patch')],check=True)
rel='src/point_add/leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt'
original=subprocess.check_output(['git','-C',str(dest),'show',rev+':'+rel]).decode().splitlines();lines=[];rows=0
for line in original:
    if not line.strip() or line.startswith('#'):lines.append(line);continue
    values=list(map(int,line.split()));assert len(values)==5
    revised=[min(v+3,258) for v in values] if 2<=rows<137 else values
    lines.append(' '.join(map(str,revised)));rows+=1
assert rows==138
if mode.endswith('tail2'):lines.extend(['6 6 6 6 5','6 6 6 6 5'])
(dest/rel).write_text('\n'.join(lines)+'\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/(mode+'.patch')).write_bytes(patch)
protected={}
for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines():
    if not name.startswith('src/point_add/'):
        b=(dest/name).read_bytes();assert b==subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name]);protected[name]=hashlib.sha256(b).hexdigest()
(root/(mode+'-manifest.json')).write_text(json.dumps({'revision':rev,'score':None,'status':'prepared diagnostic','mode':mode,'scope':'Uniform +3 interior margin, capped258, fixed seed boundary, planner1267, tick104 fold repair. Tail variant appends two width6 rows; round count follows table length, preserving odd final target. No exactness claim for fitted envelope.','rounds':140 if mode.endswith('tail2') else 138,'patch_sha256':hashlib.sha256(patch).hexdigest(),'protected_sha256':protected},indent=2)+'\n')
