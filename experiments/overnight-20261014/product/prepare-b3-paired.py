"""Fresh independent B3 packets, exact full-state pairing, no scorer writes."""
from pathlib import Path
import hashlib, subprocess, sys

base, dest = map(Path, sys.argv[1:3])
subprocess.run([sys.executable, str(Path(__file__).with_name('create-paired-replay.py')), str(base), str(dest)], check=True)
p = dest / 'src/main.rs'
s = p.read_text()
s = s.replace('product-independent-structured-v1', 'product-b3-independent-structured-v1')
s = s.replace('product-paired-fixed-measurement-v1', 'product-b3-paired-fixed-measurement-v1')
s = s.replace('let mut xof=if a[3]=="baseline"{fiat_shamir_seed(&left)}', 'let mut xof=if a[3]=="candidate"{fiat_shamir_seed(&right)}else if a[3]=="baseline"{fiat_shamir_seed(&left)}')
s = s.replace('if a[3]=="baseline"{NUM_TESTS}', 'if a[3]=="baseline"||a[3]=="candidate"{NUM_TESTS}')
s = s.replace(' let nr=|ops:', ' let mut official_left=xof.clone();let mut official_right=xof;\n let nr=|ops:')
s = s.replace('let mut lr=h.clone().finalize_xof();let mut rr=h.finalize_xof();', 'let mut lr=if a[3]=="candidate"{official_left.clone()}else{h.clone().finalize_xof()};let mut rr=if a[3]=="candidate"{official_right.clone()}else{h.finalize_xof()};')
s = s.replace('eprintln!("PAIRED_BATCH {batch} equal={eq} left_phase={:#x} right_phase={:#x}",ls.phase&live,rs.phase&live);', 'eprintln!("PAIRED_BATCH {batch} equal={eq} left_phase={:#x} right_phase={:#x}",ls.phase&live,rs.phase&live);\n  drop(ls);drop(rs);if a[3]=="candidate"{official_left=lr;official_right=rr;}')
old = 'assert_eq!(nr(&left),nr(&right),"paired RNG requires unchanged measurement/reset order");'
new = '''assert_eq!(nr(&left),nr(&right),"paired RNG requires unchanged measurement/reset order");
 let measurement = |ops:&[Op]|ops.iter().filter(|o|matches!(o.kind,OperationType::R|OperationType::Hmr)).copied().collect::<Vec<_>>();
 assert_eq!(measurement(&left),measurement(&right),"all measurement/reset operations, wires, classical slots and explicit conditions must match in order");
 eprintln!("B3_SOURCE_BOUND_DIAGNOSTIC library={} measurements={} packets_domain=product-b3-independent-structured-v1 phase_shots_follow=true score=NONE", LIBRARY_SOURCE, nr(&left));
 let (mut left_phase_shots,mut right_phase_shots)=(0u32,0u32);
'''
assert s.count(old) == 1
s = s.replace(old, new)
old = 'left_phase+=usize::from(ls.phase&live!=0);right_phase+=usize::from(rs.phase&live!=0);'
new = '''left_phase+=usize::from(ls.phase&live!=0);right_phase+=usize::from(rs.phase&live!=0);
  left_phase_shots+=(ls.phase&live).count_ones();right_phase_shots+=(rs.phase&live).count_ones();
  for (lane,v) in points.iter().enumerate(){let lb=ls.get_register(&regs[0],lane)!=v[4]||ls.get_register(&regs[1],lane)!=v[5];let rb=rs.get_register(&regs[0],lane)!=v[4]||rs.get_register(&regs[1],lane)!=v[5];if lb||rb{eprintln!("B3_COUNTEREXAMPLE index={} family={} left_bad={} right_bad={} target_x={:#x} target_y={:#x} offset_x={:#x} offset_y={:#x} left_x={:#x} left_y={:#x} expected_x={:#x} expected_y={:#x}",batch*64+lane,if a[3]=="structured"{if (batch*64+lane)%2==0{"minus2A"}else{"zero_slope"}}else{"independent"},lb,rb,v[0],v[1],v[2],v[3],ls.get_register(&regs[0],lane),ls.get_register(&regs[1],lane),v[4],v[5]);}}
'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('left_phase_batches={left_phase}', 'left_phase_shots={left_phase_shots} right_phase_shots={right_phase_shots} left_phase_batches={left_phase}')
s = 'const LIBRARY_SOURCE:&str='+repr(str(base.resolve())).replace("'", '"')+';\n'+s
p.write_text(s, newline='\n')
print('b3_diagnostic_sha256='+hashlib.sha256(p.read_bytes()).hexdigest())
