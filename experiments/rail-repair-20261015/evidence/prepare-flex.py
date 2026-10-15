"""Use the source's supported dynamic allocator for arithmetic experiments.

The frozen old-layout tables and their assertions remain intact but unused.
Both baseline and repaired variants use exactly the same allocator policy.
"""
from pathlib import Path
import subprocess,hashlib,json,sys
root=Path(__file__).resolve().parent
mode=sys.argv[1];assert mode in ['baseline','repair']
dest=root/f'flex-{mode}-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
base=dest/'src/point_add'
p=base/'mod.rs';s=p.read_text()
for name in ['y42_bound_pass','square_guard','linear_restore']:
    needle=f'    ops = {name}::run(ops);';assert s.count(needle)==1
    s=s.replace(needle,f'    // {name}: optional table applies only to the old stream; retained unchanged but not applied here.')
p.write_text(s)
p=base/'leapfrog.rs';s=p.read_text()
for before,after in [('pub(crate) const Y42_UNBOUND: bool = false;','pub(crate) const Y42_UNBOUND: bool = true;'),('pub(crate) const Y42_ALLOC: bool = Y42;','pub(crate) const Y42_ALLOC: bool = false;')]:
    assert s.count(before)==1;s=s.replace(before,after)
p.write_text(s)
if mode=='repair':
    p=base/'y15_onefold.rs';s=p.read_text();needle='if PAYLOAD_FOLD_PREFIX && !rev && t <= 55 { 57 } else { Y15_WIN }';assert s.count(needle)==1
    s=s.replace(needle,'if !rev && ((PAYLOAD_FOLD_PREFIX && t <= 55) || t == 104) { 57 } else { Y15_WIN }');p.write_text(s)
    p=base/'leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt';lines=p.read_text().splitlines();rows=[i for i,l in enumerate(lines) if l.strip() and not l.startswith('#')]
    at=rows[109];assert [int(v) for v in lines[at].split()]==[62,62,61,60,59]
    lines[at]='62 62 61 61 60';p.write_text('\n'.join(lines)+'\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary']);(root/f'flex-{mode}.patch').write_bytes(patch)
protected={name:hashlib.sha256((dest/name).read_bytes()).hexdigest() for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines() if not name.startswith('src/point_add/')}
for name,digest in protected.items():assert hashlib.sha256(subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name])).hexdigest()==digest
(root/f'flex-{mode}-manifest.json').write_text(json.dumps({'revision':rev,'status':'pending-generation','qualified_score':None,'policy':'Existing Y42 dynamic allocator branch with checked scratch return; old-layout optional tables unused, not rebound.','patch_sha256':hashlib.sha256(patch).hexdigest(),'protected':protected},indent=2)+'\n')
