#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-direct-transport-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 prepare-v2.py > prepare-v2.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd observer || exit 1
 export PEBBLE_HARD_CAP=1234
 /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit phase_pebble -- --nocapture > ../tests-v2.log 2>&1
 rc=$?
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit phase_fit -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit phase_fusion -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit zero_carry -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit plan7_tests -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit terminal_contract_tests -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit terminal_birth_phase_tests -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit direct_transport_tests -- --nocapture >> ../tests-v2.log 2>&1; rc=$?; fi
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bin build_circuit > ../build-v2.out 2> ../build-v2.log; rc=$?; fi
 cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then python3 sweep.py > sweep-v2.log 2>&1; rc=$?; fi
printf '%s\n' "$rc" > run-v2.exit
exit "$rc"
