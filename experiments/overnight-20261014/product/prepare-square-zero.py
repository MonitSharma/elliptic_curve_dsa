"""Add a diagnostic-only zero-representative component test; defaults untouched."""
from pathlib import Path
import sys,difflib
base=Path(sys.argv[1]);dest=Path(sys.argv[2]);source=(base/'square.rs').read_text()
tests=source[source.index('#[cfg(test)]\nmod g3_tests'):]
tests=tests.replace('mod g3_tests','mod research_zero_representative').replace('fn g3_square_unit()','fn research_square_zero_representative()')
start=tests.index('                let (xv, yv) = match (b, shot) {');end=tests.index('                sim.set_register(&rx, xv, shot);',start)
tests=tests[:start]+'''                let xv=if shot<32{U256::ZERO}else{rnd()};
                let yv=if shot%2==0{U256::ZERO}else{p};
'''+tests[end:]
tests=tests.replace('if o.reduce_mod(p) != e.0 && (b > 0 || shot >= 6) { bad += 1; }','''if o.reduce_mod(p) != e.0 { bad += 1; }
                if b==0 {eprintln!("ZERO_REP shot={shot} y={:#x} got={:#x} expected={:#x} delta={:#x} phase={}",e.2,o,e.0,e.0.add_mod(p-o.reduce_mod(p),p),(sim.phase>>shot)&1);}''')
tests=tests.replace('let pm = if b == 0 { sim.phase & !0x3f } else { sim.phase };','let pm = sim.phase;')
tests=tests.replace('G3_UT','ZERO_REP_DIAGNOSTIC')
dest.mkdir(parents=True,exist_ok=True)
target=dest/'square.rs';before=(base/'square.rs').read_bytes()
target.write_bytes(before+b'\n'+tests.encode())
patch=''.join(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n' for line in difflib.unified_diff(before.decode().splitlines(keepends=True),target.read_bytes().decode().splitlines(keepends=True),fromfile='a/src/point_add/square.rs',tofile='b/src/point_add/square.rs'))
(dest/'square-zero-test.patch').write_bytes(patch.encode())
