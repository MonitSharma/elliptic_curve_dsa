"""Observe the preserved +1 rail/cap1267 circuit before retroactive Y33 edits."""
from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parent;dest=root/'trace-room-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root.parent/'rail-margin-20261015/margin-room-b3';base=dest/'src/point_add'
for name in subprocess.check_output(['git','-C',str(source),'diff','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');(dest/name).write_bytes((source/name).read_bytes())
old=root.parent/'rail-repair-20261015/flex-trace-repair-b3/src/point_add'
s=(old/'rail_trace.rs').read_text().replace('rail-repair-20261015','rail-control-20261015').replace('["known15","independent"]','["known15","independent","structured","candidate"]')
(base/'rail_trace.rs').write_text(s)
(base/'observed_sim.rs').write_bytes((old/'observed_sim.rs').read_bytes())
p=base/'mod.rs';s=p.read_text();needle='    let mut ops = build_point_add();';assert s.count(needle)==1
s='mod rail_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    return ops;')
needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        rail_trace::run(circ.rail_observation_ops());\n'+needle);p.write_text(s)
p=base/'builder.rs';s=p.read_text();needle='    pub(crate) fn y33_clears(&mut self) {';assert s.count(needle)==1
s=s.replace(needle,'    pub(crate) fn rail_observation_ops(&self) -> &[Op] { &self.ops }\n'+needle);p.write_text(s)
p=base/'leapfrog.rs';s=p.read_text();needle='fn fwd_tick(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {';assert s.count(needle)==1
s=s.replace(needle,needle.replace('fwd_tick(', 'fwd_tick_inner('))
s+='\n'+needle+'''
    super::rail_trace::mark(c.op_count(),c.current_phase(),t,false,&wk.r,&[],lowrel());
    fwd_tick_inner(c,wk,t,pay.as_deref_mut());
    super::rail_trace::mark(c.op_count(),c.current_phase(),t,true,&wk.r,wk.tape.last().unwrap(),lowrel());
}
''';p.write_text(s)
(root/'trace.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
packets=root/'packets';packets.mkdir()
for src in [root.parent/'rail-repair-20261015/known15.tsv',*(root.parent/'arithmetic-repair-20261015/packets').glob('*.tsv')]:
    (packets/src.name).write_bytes(src.read_bytes())
(root/'trace-manifest.json').write_text(json.dumps({'revision':rev,'score':None,'scope':'Raw pre-Y33 forward rail observation, endpoint capture, and exact whole-state equality to unchanged simulator. Not a full optimized-source proof.','packet_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in packets.glob('*.tsv')}},indent=2)+'\n')
