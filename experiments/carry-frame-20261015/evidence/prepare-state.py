"""Capture the actual carry predicate across the terminal fold before Y33."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'state-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'phase-origin-20261015/terminal-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
base=dest/'src/point_add';(base/'carry_trace.rs').write_bytes((root/'carry_trace.rs').read_bytes());(base/'observed_sim.rs').write_bytes((root.parent/'rail-control-20261015/trace-room-b3/src/point_add/observed_sim.rs').read_bytes())
p=base/'pingpong.rs';s=p.read_text();start=s.index('    pub(crate) fn add_consume_exact(');end=s.index('    /// Bits below `split`',start);part=s[start:end]
needle='        let ov = circ.alloc_qubit();';assert part.count(needle)==1;part=part.replace(needle,'''        let watched=m.0==562 && split==254 && circ.current_phase()=="multiply";
        if watched {super::super::carry_trace::mark(circ.op_count(),"before_fold",m,&acc[..split],&addend[..split],0,None);}
'''+needle)
needle="        circ.record_replay_site('B', round, split, k);";assert part.count(needle)==1;part=part.replace(needle,needle+'''
        if watched {super::super::carry_trace::mark(circ.op_count(),"after_fold",m,&acc[..split],&addend[..split],k,borrow);}
''');s=s[:start]+part+s[end:];p.write_text(s)
p=base/'builder.rs';s=p.read_text();needle='    pub fn take_ops(&mut self) -> Vec<Op> {';assert s.count(needle)==1;s=s.replace(needle,'    pub(crate) fn observation_ops(&self)->&[Op]{&self.ops}\n'+needle);p.write_text(s)
p=base/'mod.rs';s=p.read_text();needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        carry_trace::run(circ.observation_ops());\n'+needle);needle='    let mut ops = build_point_add();';assert s.count(needle)==1;s='mod carry_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    return ops;');p.write_text(s)
(root/'state.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'state-manifest.json').write_text(json.dumps({'revision':rev,'score':None,'scope':'Raw pre-Y33 carry observation on the first preserved zero-slope input; all-zero measurement outcomes. Full state compared to protected simulator. Not a final-stream phase proof.','packet_sha256':hashlib.sha256((root.parent/'arithmetic-repair-20261015/packets/structured.tsv').read_bytes()).hexdigest()},indent=2)+'\n')
