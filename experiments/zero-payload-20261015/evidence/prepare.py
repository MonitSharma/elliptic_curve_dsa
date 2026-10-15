"""Explicit-interface control and zero-payload wrapper from the same wide parent."""
from pathlib import Path
import subprocess,sys,json,hashlib
root=Path(__file__).resolve().parent;mode=sys.argv[1];assert mode in ['control','wrapped'];dest=root/(mode+'-b3');assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
parent=root.parent/'dynamic-pool-20261015/wide-b3'
for rel in subprocess.check_output(['git','-C',str(parent),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((parent/rel).read_bytes())
base=dest/'src/point_add';p=base/'leapfrog.rs';s=p.read_text()
for a,b in [('("LF_SEAMS", "1")','("LF_SEAMS", "0")'),('("SL_RT0", "1")','("SL_RT0", "0")'),('("LF_T6_SEEDFUSE", "1")','("LF_T6_SEEDFUSE", "0")')]:assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)
(base/'zero_wrapper.rs').write_bytes((root/'zero_wrapper.rs').read_bytes());(base/'zero_proof.rs').write_bytes((root.parent/'arithmetic-repair-20261015/proof_kernel.rs').read_bytes())
p=base/'mod.rs';s=p.read_text();s='mod zero_wrapper;\n#[cfg(test)] mod zero_proof;\n'+s
if mode=='wrapped':
 for name in ['divide','multiply']:
  a=f'if seams {{ leapfrog::{name}_seamed(circ, y, x, ox); }} else {{ leapfrog::{name}(circ, y, x); }}'
  b=f'assert!(!seams); zero_wrapper::apply(circ,y,x,{str(name=="divide").lower()});'
  assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)
(root/(mode+'.patch')).write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/(mode+'-manifest.json')).write_text(json.dumps({'revision':rev,'parent':str(parent),'score':None,'scope':'Both candidates disable LF_SEAMS, SL_RT0 and LF_T6_SEEDFUSE. Wrapped adds a reversible two-zero-encoding payload extension around divide/multiply. Requires nonzero denominator/multiplier and verified nonzero-output contracts.','new_sources_sha256':{f:hashlib.sha256((base/f).read_bytes()).hexdigest() for f in ['zero_wrapper.rs','zero_proof.rs']}},indent=2)+'\n')
