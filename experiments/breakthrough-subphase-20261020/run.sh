#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-subphase-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
  cd observer || exit 1
  /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bin build_circuit > ../build.log 2>&1
  rc=$?
  if [ "$rc" -eq 0 ]; then
    BREAK_CAP=1234 /usr/bin/time -v target/release/build_circuit > ../generate.out 2> ../generate.log
    rc=$?
  fi
  cd .. || exit 1
fi
if [ "$rc" -eq 0 ]; then
  python3 segments.py > segments.log 2>&1
  rc=$?
fi
if [ "$rc" -eq 0 ]; then
  export PHASE_MAP="$PWD/segment-map.tsv"
  /usr/bin/time -v ../breakthrough-profile-20261020/tool/target/release/phase-replay observer/ops.bin breakthrough-raw-subphase-cost-v1 0 512 2 region-census.jsonl 8 > replay.out 2> replay.err
  rc=$?
fi
printf '%s\n' "$rc" > run.exit
exit "$rc"
