#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-phase-cubic-reserve-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1 PEBBLE_HARD_CAP=1234
ulimit -v 33554432
python3 prepare.py > prepare-v2.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd observer || exit 1
 for filter in phase_cubic_cap_tests phase_pebble phase_fit phase_fusion zero_carry plan7_tests terminal_contract_tests terminal_birth_phase_tests direct_transport_tests; do
  /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit "$filter" -- --nocapture >> ../tests-v2.log 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then break; fi
 done
 if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bin build_circuit > ../build-v2.out 2> ../build-v2.log; rc=$?; fi
 cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then python3 sweep.py > sweep-v2.log 2>&1; rc=$?; fi
printf '%s\n' "$rc" > run-v2.exit
exit "$rc"
