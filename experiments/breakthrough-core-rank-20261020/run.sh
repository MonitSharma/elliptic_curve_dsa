#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-core-rank-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd primitive || exit 1
 /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit core_rank_audit_tests -- --nocapture > ../tests.log 2>&1
 rc=$?
 cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then python3 rank.py > rank.log 2>&1; rc=$?; fi
printf '%s\n' "$rc" > run.exit
exit "$rc"
