from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-hardcarry-20261020'
for name in['launch.py','sweep.py']:(r/name).write_bytes((old/name).read_bytes())
s=(old/'run.sh').read_bytes().replace(b'breakthrough-hardcarry-20261020',b'breakthrough-phase-pebble-integration-20261020')
start=s.index(b'  /home/')if b'  /home/'in s else -1
# Explicit runner below avoids inheriting any old fixture or environment repair.
(r/'run.sh').write_bytes(b'''#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-phase-pebble-integration-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd observer || exit 1
 /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit phase_pebble -- --nocapture > ../tests.log 2>&1
 rc=$?
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit phase_fit -- --nocapture >> ../tests.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit phase_fusion -- --nocapture >> ../tests.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bin build_circuit > ../build.out 2> ../build.log; rc=$?; fi
 cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then python3 sweep.py > sweep.log 2>&1; rc=$?; fi
printf '%s\\n' "$rc" > run.exit
exit "$rc"
''')
