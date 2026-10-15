"""Observe wrapper interface states without assuming the currently failing values."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent;dest=root/'observer-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
parent=root/'wrapped-b3'
for rel in subprocess.check_output(['git','-C',str(parent),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((parent/rel).read_bytes())
base=dest/'src/point_add';(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes());(base/'observed_sim.rs').write_bytes((root.parent/'rail-control-20261015/trace-room-b3/src/point_add/observed_sim.rs').read_bytes())
p=base/'zero_wrapper.rs';s=p.read_text();changes={
' c.cx(zp,z0);xor_constant(c,zp,y,modulus());':' super::payload_trace::mark(c.op_count(),divide,"detected",y,x,&[z0,zp]);\n c.cx(zp,z0);xor_constant(c,zp,y,modulus());',
' if divide{super::leapfrog::divide(c,y,x);}else{super::leapfrog::multiply(c,y,x);}':' super::payload_trace::mark(c.op_count(),divide,"input_oracle",y,x,&[z0,zp]);\n if divide{super::leapfrog::divide(c,y,x);}else{super::leapfrog::multiply(c,y,x);}\n super::payload_trace::mark(c.op_count(),divide,"output_oracle",y,x,&[z0,zp]);',
' xor_constant(c,zp,y,modulus());c.cx(zp,z0);':' xor_constant(c,zp,y,modulus());c.cx(zp,z0);\n super::payload_trace::mark(c.op_count(),divide,"restored",y,x,&[z0,zp]);',
' c.release_clean(zp);c.release_clean(z0);':' super::payload_trace::mark(c.op_count(),divide,"uncomputed",y,x,&[z0,zp]);\n c.release_clean(zp);c.release_clean(z0);'}
for a,b in changes.items():assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)
p=base/'builder.rs';s=p.read_text();needle='    pub fn take_ops(&mut self) -> Vec<Op> {';assert s.count(needle)==1;p.write_text(s.replace(needle,'    pub(crate) fn observation_ops(&self)->&[Op]{&self.ops}\n'+needle))
p=base/'mod.rs';s=p.read_text();needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        payload_trace::run(circ.observation_ops());\n'+needle);needle='    let mut ops = build_point_add();';assert s.count(needle)==1;s='mod payload_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    return ops;');p.write_text(s)
(root/'observer.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
