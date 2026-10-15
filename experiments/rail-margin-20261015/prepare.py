"""Uniform rail headroom diagnostic, independent of sampled failing inputs."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'margin-one-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
subprocess.run(['git','-C',str(dest),'apply',str(root.parent/'rail-repair-20261015/flex-baseline.patch')],check=True)
base=dest/'src/point_add'
p=base/'y15_onefold.rs';s=p.read_text();needle='if PAYLOAD_FOLD_PREFIX && !rev && t <= 55 { 57 } else { Y15_WIN }';assert s.count(needle)==1
p.write_text(s.replace(needle,'if !rev && ((PAYLOAD_FOLD_PREFIX && t <= 55) || t == 104) { 57 } else { Y15_WIN }'))
p=base/'leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt';lines=p.read_text().splitlines();changes=[]
for i,line in enumerate(lines):
    if not line.strip() or line.startswith('#'):continue
    values=[int(x) for x in line.split()];assert len(values)==5
    widened=[min(v+1,258) for v in values]
    changes.append({'tick':len(changes),'old':values,'new':widened});lines[i]=' '.join(map(str,widened))
assert len(changes)==138
p.write_text('\n'.join(lines)+'\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/'candidate.patch').write_bytes(patch)
protected={}
for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines():
    if not name.startswith('src/point_add/'):
        b=(dest/name).read_bytes();assert b==subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name]);protected[name]=hashlib.sha256(b).hexdigest()
(root/'manifest.json').write_text(json.dumps({'revision':rev,'score':None,'status':'prepared, not qualified','scope':'Uniform +1 on all fitted rail widths, capped at 258; finite tick104 fold repair retained. No input-specific table fitting. Same 138 rounds and existing supported dynamic allocator.','patch_sha256':hashlib.sha256(patch).hexdigest(),'protected_sha256':protected,'rows':changes},indent=2)+'\n')
