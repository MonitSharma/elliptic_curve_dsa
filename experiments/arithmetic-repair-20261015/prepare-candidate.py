"""Integrate the finite tick-104 borrow mitigation with checked allocator normalization."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
root=Path(__file__).resolve().parent
mode=sys.argv[1] if len(sys.argv)>1 else 'normal'
assert mode in ['normal','raw']
dest=root/('candidate-fold104-b3' if mode=='normal' else 'diagnostic-fold104-b3')
assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root/'diagnostic-b3'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
pool=json.loads((root/'pool104.json').read_text())
base=dest/'src/point_add'
p=base/'y15_onefold.rs';s=p.read_text()
needle='if PAYLOAD_FOLD_PREFIX && !rev && t <= 55 { 57 } else { Y15_WIN }'
assert s.count(needle)==1
s=s.replace(needle,'if !rev && ((PAYLOAD_FOLD_PREFIX && t <= 55) || t == 104) { 57 } else { Y15_WIN }')
needle='fn body_capped(c: &mut Builder, t: usize, s: [QubitId; 3], k1: QubitId, k2: QubitId, b: &[QubitId], tg: &[QubitId], proxy: usize, rev: bool) {'
assert s.count(needle)==1
before=f'(vec!{pool["before_q"]}, vec!{pool["before_b"]}, {pool["before_next"]}u32)'
s=s.replace(needle,needle+f'''
    // A wider forward fold fixes the saved missing-borrow counterexample.
    // Normalize only returned scratch; live owners and all existing checks remain.
    let repair_pool = (!rev && t==104 && c.current_phase()=="divide").then(|| {{
        let actual=c.y42_alloc_state();
        let expected={before};
        assert_eq!(actual,expected,"fold104: changed entry allocator; recertify the repair");
        actual
    }});
''')
needle='    super::C35_CMP_FX.with(|x| x.set(false));'
assert s.count(needle)==1
s=s.replace(needle,f'''
    if let Some(before)=repair_pool {{
        // y42_alloc_set verifies that all borrowed quantum/classical scratch was returned.
        // The saved ordering restores later source-bound allocator fingerprints.
        c.y42_alloc_set(&before, &{pool['after_q']}, 0, &{pool['after_b']}, {pool['after_next']});
    }}
'''+needle)
p.write_text(s)
if mode=='raw':
    for name in ['mod.rs','leapfrog.rs','observed_sim.rs','payload_trace.rs']:
        (base/name).write_bytes((root/'diagnostic-payload-b3/src/point_add'/name).read_bytes())
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary'])
(root/('fold104.patch' if mode=='normal' else 'fold104-raw.patch')).write_bytes(patch)
changed=subprocess.check_output(['git','-C',str(dest),'diff','--name-only'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed)
manifest={'source_revision':rev,'mode':mode,'status':'pending-generation','patch_sha256':hashlib.sha256(patch).hexdigest(),
          'pool_sha256':hashlib.sha256((root/'pool104.json').read_bytes()).hexdigest(),'changed_files':changed,
          'scope':'Finite tick-104 borrow mitigation; does not repair inherited width truncations or structured exceptional cases.'}
(root/f'fold104-{mode}-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
