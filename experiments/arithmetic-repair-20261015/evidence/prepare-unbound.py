"""Native repaired circuit without optimization tables certified for the old stream."""
from pathlib import Path
import hashlib
import json
import subprocess
root=Path(__file__).resolve().parent
dest=root/'candidate-fold104-unbound-b3'
assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root/'diagnostic-b3'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
base=dest/'src/point_add'
(base/'y15_onefold.rs').write_bytes((root/'candidate-fold104-b3/src/point_add/y15_onefold.rs').read_bytes())
p=base/'mod.rs';s=p.read_text()
for name in ['y42_bound_pass','square_guard','linear_restore']:
    needle=f'    ops = {name}::run(ops);'
    assert s.count(needle)==1
    s=s.replace(needle,f'    // {name}: frozen optimization is certified only for the original stream; omit on the repaired circuit.')
p.write_text(s)
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary'])
(root/'fold104-unbound.patch').write_bytes(patch)
changed=subprocess.check_output(['git','-C',str(dest),'diff','--name-only'],text=True).splitlines()
assert all(name.startswith('src/point_add/') for name in changed)
manifest={'source_revision':rev,'status':'pending-generation','patch_sha256':hashlib.sha256(patch).hexdigest(),'changed_files':changed,
          'scope':'Finite step104 mitigation. Three old-stream-only optional optimization tables are omitted; their code, data and binding assertions are unchanged.',
          'qualified_score':None,'independent_correctness':'not yet run; inherited width and exceptional-domain defects are expected to remain'}
(root/'fold104-unbound-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
