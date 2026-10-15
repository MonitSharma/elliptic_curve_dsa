"""Observe the division invariant P_i = slope * R_i mod p on fixed inputs."""
from pathlib import Path
import subprocess
root = Path(__file__).resolve().parent
dest = root / 'diagnostic-payload-b3'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-checkout',str(root/'diagnostic-b3'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach','b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'],check=True)
base=dest/'src/point_add'
(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes())
(base/'observed_sim.rs').write_bytes((root/'diagnostic-reset-b3/src/point_add/observed_sim.rs').read_bytes())
p=base/'mod.rs';s=p.read_text();needle='    let mut ops = build_point_add();';assert s.count(needle)==1
s='mod payload_trace;\nmod observed_sim;\n'+s.replace(needle,needle+'\n    payload_trace::run(&ops);\n    return ops;');p.write_text(s)
p=base/'leapfrog.rs';s=p.read_text()
needle='        return fwd_tick_fast(c, wk, t, pay);';assert s.count(needle)==1
s=s.replace(needle,'''        fwd_tick_fast(c, wk, t, pay.as_deref_mut());
        if c.current_phase()=="divide" { super::payload_trace::mark(c.op_count(), "rail", t, &wk.r, pay.as_deref(), lowrel()); }
        return;''')
needle='fn pay_fwd_tick(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {'
assert s.count(needle)==1
s=s.replace(needle,'''fn pay_fwd_tick(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {
    pay_fwd_tick_body(c,t,letter,p);
    if c.current_phase()=="divide" { super::payload_trace::mark(c.op_count(), "payload", t, &[Vec::new(),Vec::new()], Some(p), lowrel()); }
}
fn pay_fwd_tick_body(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {''')
# The original type is Vec<QubitId>; keep the copied body signature exact.
s=s.replace('p: &mut [Vec<QubitId>; 2]) {\n    let', 'p: &mut [Vec<QubitId>; 2]) {\n    let')
p.write_text(s)
(root/'payload-tracked.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
