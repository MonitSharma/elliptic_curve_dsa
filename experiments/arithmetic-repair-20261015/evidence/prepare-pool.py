"""Capture exact B3 tick-104 allocator context without changing any operation."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
dest=root/'pool-observer-b3'
assert not dest.exists()
subprocess.run(['git','clone','--shared','--no-checkout',str(root/'diagnostic-b3'),str(dest)],check=True)
subprocess.run(['git','-C',str(dest),'checkout','--detach','b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7'],check=True)
base=dest/'src/point_add'
for name in ['mod.rs','leapfrog.rs','observed_sim.rs','payload_trace.rs']:
    (base/name).write_bytes((root/'diagnostic-payload-b3/src/point_add'/name).read_bytes())
p=base/'y15_onefold.rs';s=p.read_text()
needle='fn body_capped(c: &mut Builder, t: usize, s: [QubitId; 3], k1: QubitId, k2: QubitId, b: &[QubitId], tg: &[QubitId], proxy: usize, rev: bool) {'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n    let repair_pool = (!rev && t==104 && c.current_phase()=="divide").then(|| c.y42_alloc_state());')
needle='    super::C35_CMP_FX.with(|x| x.set(false));'
assert s.count(needle)==1
s=s.replace(needle,'''    if let Some(before)=repair_pool {
        let after=c.y42_alloc_state();
        let text=format!("{{\\\"before_q\\\":{:?},\\\"before_b\\\":{:?},\\\"before_next\\\":{},\\\"after_q\\\":{:?},\\\"after_b\\\":{:?},\\\"after_next\\\":{}}}",before.0,before.1,before.2,after.0,after.1,after.2);
        std::fs::write("/home/hclau/ecdsa_research/arithmetic-repair-20261015/pool104.json",text).unwrap();
    }
'''+needle)
p.write_text(s)
(root/'pool-tracked.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
