"""Observe both flexible-layout raw circuits on the fixed counterexamples."""
from pathlib import Path
import subprocess,sys,hashlib,json
root=Path(__file__).resolve().parent;mode=sys.argv[1];assert mode in ['baseline','repair']
dest=root/f'flex-trace-{mode}-b3';assert not dest.exists()
rev='b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'
subprocess.run(['git','clone','--shared','--no-checkout',str(root.parent/'upstream'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach',rev],check=True)
source=root/f'flex-{mode}-b3';base=dest/'src/point_add'
for name in subprocess.check_output(['git','-C',str(source),'diff','--name-only'],text=True).splitlines():
    assert name.startswith('src/point_add/');(dest/name).write_bytes((source/name).read_bytes())
script=(root/'rail_trace.rs').read_text().replace('arithmetic-repair-20261015','rail-repair-20261015').replace('["independent","structured","candidate"]','["known15","independent"]')
needle='                    if !m.after{entry=vals;entry_at=m.at;continue;}'
script=script.replace(needle,needle+'''
                    if m.tick==137 { for lane in 0..rows.len(){if vals[lane].iter().any(|v|*v!=U256::from(1)&&*v!=p-U256::from(1)){eprintln!("ENDPOINT_BAD family={family} shot={} phase={} rails={:#x},{:#x}",batch*64+lane,m.phase,vals[lane][0],vals[lane][1]);}}}
''')
needle='final_bad+=1;';assert script.count(needle)==1
script=script.replace(needle,needle+'eprintln!("FINAL_BAD family={family} shot={} x_bad={} y_bad={}",batch*64+lane,sim.get_register(&regs[0],lane)!=v[4],sim.get_register(&regs[1],lane)!=v[5]);')
(base/'rail_trace.rs').write_text(script)
(base/'observed_sim.rs').write_bytes((root/'diagnostic-rails-pre-y33-b3/src/point_add/observed_sim.rs').read_bytes())
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
(root/f'flex-trace-{mode}.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
packets=root/'packets';packets.mkdir(exist_ok=True)
for src in [root/'known15.tsv',root.parent/'arithmetic-repair-20261015/packets/independent.tsv']:
    dst=packets/src.name
    if dst.exists():assert dst.read_bytes()==src.read_bytes()
    else:dst.write_bytes(src.read_bytes())
