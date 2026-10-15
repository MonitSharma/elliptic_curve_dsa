"""Gate-inert boundary/tick instrumentation on the no-wrapper control."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent;dest=root/'observer-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
parent=root.parent/'zero-payload-20261015/control-b3'
for rel in subprocess.check_output(['git','-C',str(parent),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((parent/rel).read_bytes())
base=dest/'src/point_add';(base/'division_trace.rs').write_bytes((root/'division_trace.rs').read_bytes());(base/'observed_sim.rs').write_bytes((root.parent/'rail-control-20261015/trace-room-b3/src/point_add/observed_sim.rs').read_bytes())
p=base/'mod.rs';s=p.read_text();needle='        if seams { leapfrog::divide_seamed(circ, y, x, ox); } else { leapfrog::divide(circ, y, x); }';assert s.count(needle)==1;s=s.replace(needle,'        division_trace::mark(circ.op_count(),"input",0,y,x,&[]);\n'+needle+'\n        division_trace::mark(circ.op_count(),"output",0,y,x,&[]);');needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        division_trace::run(circ.observation_ops());\n'+needle);needle='    let mut ops = build_point_add();';assert s.count(needle)==1;s='mod division_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    return ops;');p.write_text(s)
p=base/'builder.rs';s=p.read_text();needle='    pub fn take_ops(&mut self) -> Vec<Op> {';assert s.count(needle)==1;p.write_text(s.replace(needle,'    pub(crate) fn observation_ops(&self)->&[Op]{&self.ops}\n'+needle))
p=base/'leapfrog.rs';s=p.read_text();start=s.index('pub(crate) fn divide_dbg(');end=s.index('/// `y <- y * x',start);part=s[start:end]
needle='        let letter = wk.tape[t].clone();';assert part.count(needle)==1;part=part.replace(needle,needle+'\n        super::division_trace::mark(c.op_count(),"before",t,&pay[t%2],&pay[1-t%2],&letter);')
needle='        lr_unpad(c, pads);';assert part.count(needle)==1;part=part.replace(needle,needle+'\n        super::division_trace::mark(c.op_count(),"after",t,&pay[t%2],&pay[1-t%2],&letter);')
needle='        fwd_tick(c, &mut wk, t, Some(&mut pay));';assert part.count(needle)==1;part=part.replace(needle,'        super::division_trace::mark(c.op_count(),"before",t,&pay[t%2],&pay[1-t%2],&[]);\n'+needle+'\n        super::division_trace::mark(c.op_count(),"after",t,&pay[t%2],&pay[1-t%2],&wk.tape[t]);')
s=s[:start]+part+s[end:];p.write_text(s)
(root/'observer.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
