"""Build an observation-only forward rail checker from the pristine B3 revision."""
from pathlib import Path
import subprocess, hashlib, json
root=Path(__file__).resolve().parent
old=root.parent/'arithmetic-repair-20261015'
dest=root/'diagnostic-rails-pre-y33-b3'
assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
base=dest/'src/point_add'
(base/'rail_trace.rs').write_bytes((root/'rail_trace.rs').read_bytes())
(base/'observed_sim.rs').write_bytes((old/'diagnostic-reset-b3/src/point_add/observed_sim.rs').read_bytes())
p=base/'mod.rs';s=p.read_text();needle='    let mut ops = build_point_add();';assert s.count(needle)==1
s='mod rail_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    return ops;')
needle='        circ.y33_clears();';assert s.count(needle)==1
s=s.replace(needle,'        rail_trace::run(circ.rail_observation_ops());\n'+needle);p.write_text(s)
p=base/'builder.rs';s=p.read_text();needle='    pub(crate) fn y33_clears(&mut self) {';assert s.count(needle)==1
s=s.replace(needle,'    pub(crate) fn rail_observation_ops(&self) -> &[Op] { &self.ops }\n'+needle);p.write_text(s)
p=base/'leapfrog.rs';s=p.read_text()
needle='fn fwd_tick(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {'
assert s.count(needle)==1
s=s.replace(needle,needle.replace('fwd_tick(', 'fwd_tick_inner('))
s+='\n'+needle+'''
    super::rail_trace::mark(c.op_count(),c.current_phase(),t,false,&wk.r,&[],lowrel());
    fwd_tick_inner(c,wk,t,pay.as_deref_mut());
    super::rail_trace::mark(c.op_count(),c.current_phase(),t,true,&wk.r,wk.tape.last().unwrap(),lowrel());
}
'''
p.write_text(s)
patch=subprocess.check_output(['git','-C',str(dest),'diff','--binary'])
(root/'trace-v2.patch').write_bytes(patch)
protected={name:hashlib.sha256((dest/name).read_bytes()).hexdigest() for name in subprocess.check_output(['git','-C',str(dest),'ls-files'],text=True).splitlines() if not name.startswith('src/point_add/')}
for name,digest in protected.items():
    assert hashlib.sha256(subprocess.check_output(['git','-C',str(dest),'show',rev+':'+name])).hexdigest()==digest
(root/'trace-v2-manifest.json').write_text(json.dumps({'revision':rev,'status':'diagnostic-only-before-retroactive-Y33','qualified_score':None,'patch_sha256':hashlib.sha256(patch).hexdigest(),'protected':protected},indent=2)+'\n')
