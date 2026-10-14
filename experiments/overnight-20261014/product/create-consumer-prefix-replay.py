"""Extend the source-bound signed-R0 observer with official final value/phase/scratch checks."""
from pathlib import Path
import subprocess,sys
base=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2]).resolve();folder=Path(__file__).parent
subprocess.run([sys.executable,str(folder/'create-raw-prefix-replay.py'),str(base),str(dest)],check=True)
s=dest.joinpath('src/main.rs').read_text()
needle='  for(lane,v)in vals.iter().enumerate(){let den='
new='''  let mut xb=0;let mut yb=0;let mut joint=0;let mut cb=0;
'''+needle
assert s.count(needle)==1;s=s.replace(needle,new)
needle='   if label=="square" {'
new='''   if label=="coord_y_sub_final" {
    let xbad=x.reduce_mod(p)!=v[4];let ybad=y.reduce_mod(p)!=v[5];
    xb+=usize::from(xbad);yb+=usize::from(ybad);joint+=usize::from(xbad||ybad);
    let classical_bad=sim.get_register(&regs[2],lane)!=v[2]||sim.get_register(&regs[3],lane)!=v[3];
    cb+=usize::from(classical_bad);
    let dirty=sim.qubits.iter().skip(512).any(|q|((q>>lane)&1)!=0);
    println!("FINAL_CONSUMER_SHOT index={lane} family={} x_bad={xbad} y_bad={ybad} phase_bad={} dirty={dirty} classical_input_changed={classical_bad}",families[lane],(sim.phase>>lane)&1);
   }
'''+needle
assert s.count(needle)==1;s=s.replace(needle,new)
needle=' println!("DIAGNOSTIC_ONLY prefix_shots='
at=s.index(needle)
# Insert before the cut-loop closing brace, after the per-lane loop.
before=s[:at];closing=before.rfind('\n }\n')
assert closing!=-1
code='''
  if label=="coord_y_sub_final" {
   let dirty=sim.qubits.iter().skip(512).fold(0u64,|a,b|a|b);
   let dirty_wires=sim.qubits.iter().skip(512).filter(|&&q|q!=0).count();
   println!("FINAL_CONSUMER_CHECK shots={} x_bad={xb} y_bad={yb} joint_bad={joint} classical_input_changed={cb} phase_bad_shots={} phase_bad_batches={} dirty_shots={} dirty_wires={dirty_wires} score=NONE",vals.len(),sim.phase.count_ones(),usize::from(sim.phase!=0),dirty.count_ones());
  }
'''
s=s[:closing]+code+s[closing:]
dest.joinpath('src/main.rs').write_text(s,newline='\n')
t=dest.joinpath('Cargo.toml').read_text().replace('name="product_raw_prefix_replay"','name="product_consumer_prefix_replay"')
dest.joinpath('Cargo.toml').write_text(t,newline='\n')
