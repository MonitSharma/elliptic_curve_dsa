#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-paused-pool-audit-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 repair-v2.py > repair-v2.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd observer || exit 1
 /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bin build_circuit > ../build-v2.out 2> ../build-v2.log
 rc=$?
 cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then python3 observe.py > observe.log 2>&1; rc=$?; fi
printf '%s\n' "$rc" > run-v2.exit
exit "$rc"
