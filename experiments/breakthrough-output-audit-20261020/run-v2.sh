#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-output-audit-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 prepare-v2.py > prepare-v2.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
 cd tool-v2 || exit 1
 CARGO_TARGET_DIR=/home/hclau/ecdsa_research/breakthrough-output-audit-20261020/tool/target /home/hclau/.cargo/bin/cargo +1.93.0 build --release > ../build-v2.out 2> ../build-v2.log
 rc=$?
 cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then python3 observe-v2.py > observe-v2.log 2>&1; rc=$?; fi
printf '%s\n' "$rc" > run-v2.exit
exit "$rc"
