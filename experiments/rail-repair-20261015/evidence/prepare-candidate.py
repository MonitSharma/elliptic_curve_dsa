"""Test the independently diagnosed rail109 overflow; no packet tuning."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent
old=root.parent/'arithmetic-repair-20261015'
dest=root/'candidate-rail109-b3'
assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
base=dest/'src/point_add'
for name in ['mod.rs','y15_onefold.rs']:
    (base/name).write_bytes((old/'candidate-fold104-unbound-b3/src/point_add'/name).read_bytes())
p=base/'leapfrog_data/pack_t0hat_tail0_138_steps_k770_lw2.txt'
lines=p.read_text().splitlines(); rows=[i for i,l in enumerate(lines) if l.strip() and not l.startswith('#')]
at=rows[109]; values=[int(v) for v in lines[at].split()];assert values==[62,62,61,60,59]
# The choice result is a full even word despite the bit-zero-less input.
# Both its adder output and the pre-barrel word require the additional bit.
lines[at]='62 62 61 61 60'
p.write_text('\n'.join(lines)+'\n')
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary'])
(root/'candidate-rail109.patch').write_bytes(patch)
protected={name:hashlib.sha256((dest/name).read_bytes()).hexdigest() for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines() if not name.startswith('src/point_add/')}
for name,digest in protected.items():
    assert hashlib.sha256(subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name])).hexdigest()==digest
(root/'candidate-manifest.json').write_text(json.dumps({'revision':rev,'status':'pending-generation','qualified_score':None,'hypothesis':'Fix finite rail109 signed overflow through choice and barrel; inherit fold104 repair, omit old-stream-only postpasses. Not a universal rail schedule repair.','patch_sha256':hashlib.sha256(patch).hexdigest(),'protected':protected},indent=2)+'\n')
