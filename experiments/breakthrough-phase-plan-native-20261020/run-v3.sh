#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-phase-plan-native-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 prepare-v3.py > prepare-v3.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd primitive || exit 1
 /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit weighted_plan_tests -- --nocapture > ../tests-v3.log 2>&1
 rc=$?
 cd .. || exit 1
fi
printf '%s\n' "$rc" > run-v3.exit
exit "$rc"
