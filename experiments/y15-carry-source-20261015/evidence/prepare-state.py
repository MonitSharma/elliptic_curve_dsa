"""Instrument the Y21 top-cut cleanup without modifying protected source."""
from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent;dest=root/'state-b3';assert not dest.exists();rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'y15-unseeded-20261015/wide-b3'
for rel in subprocess.check_output(['git','-C',str(source),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines():assert rel.startswith('src/point_add/');(dest/rel).write_bytes((source/rel).read_bytes())
base=dest/'src/point_add';(base/'joint_trace.rs').write_bytes((root/'joint_trace.rs').read_bytes());(base/'observed_sim.rs').write_bytes((root.parent/'rail-control-20261015/trace-room-b3/src/point_add/observed_sim.rs').read_bytes())
p=base/'y15_onefold.rs';full=p.read_text();a=full.index('fn body(');z=full.index('fn body_capped(',a);s=full[a:z]
needle='    let (e_start, a_start) = (c.expected_total(), c.active_qubits());';assert s.count(needle)==1;s=s.replace(needle,needle+'\n    {super::super::joint_trace::mark(c.op_count(),t+usize::from(rev)*1000,"entry",tg,b,&s,None,0);}')
needle='        c.cx_all(s[1], b);\n        e_add1 = c.expected_total();';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        if top1 {super::super::joint_trace::mark(c.op_count(),t+usize::from(rev)*1000,"after_add1",tg,b,&[m0,m1,s[1]],None,0);}')
start=s.index('    } else if top1 {\n        // y21, top cut:');end=s.index('    } else if Y15_JOINT_M {',start);part=s[start:end]
needle='        lin_xor_into(c, &s1f(N - 1), m0); // m0 = g0 ^ h1';assert part.count(needle)==1;part=part.replace(needle,needle+'\n        {super::super::joint_trace::mark(c.op_count(),t+usize::from(rev)*1000,"preface",tg,b,&[m0,m1,s[0],s[1],s[2]],None,0);}')
needle='            super::super::compare::cmp_lt_phase(c, &tg[lo..split], &b[lo..split], seed0.map(|sd| b[sd]));';assert part.count(needle)==1;part=part.replace(needle,'            {super::super::joint_trace::mark(c.op_count(),t+usize::from(rev)*1000,"cmp",&tg[lo..split],&b[lo..split],&[],seed0.map(|sd| b[sd]),0);}\n'+needle)
needle='        c.hmr(m0, bit0);';assert part.count(needle)==1;part=part.replace(needle,'        {super::super::joint_trace::mark(c.op_count(),t+usize::from(rev)*1000,"hmr",tg,b,&[m0],None,bit0.0 as usize);}\n'+needle)
needle='        c.cz(hb, hb);';assert part.count(needle)==1;part=part.replace(needle,'        {super::super::joint_trace::mark(c.op_count(),t+usize::from(rev)*1000,"chain",tg,b,&[hb],None,0);}\n'+needle)
s=s[:start]+part+s[end:];p.write_text(full[:a]+s+full[z:])
p=base/'builder.rs';s=p.read_text();needle='    pub fn take_ops(&mut self) -> Vec<Op> {';assert s.count(needle)==1;s=s.replace(needle,'    pub(crate) fn observation_ops(&self)->&[Op]{&self.ops}\n'+needle);p.write_text(s)
p=base/'mod.rs';s=p.read_text();needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        joint_trace::run(circ.observation_ops());\n'+needle);needle='    let mut ops = build_point_add();';assert s.count(needle)==1;s='mod joint_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    return ops;');p.write_text(s)
(root/'state.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'state-manifest.json').write_text(json.dumps({'revision':rev,'score':None,'scope':'Raw pre-Y33 observation at the attributed Y21 top-cut cleanup; fixed zero-slope input, all-zero measurements and a single flipped measurement. Protected simulator full-state comparison.'},indent=2)+'\n')
