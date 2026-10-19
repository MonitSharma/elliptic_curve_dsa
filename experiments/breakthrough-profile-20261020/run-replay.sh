#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-profile-20261020 || exit 1
export CARGO_BUILD_JOBS=2 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 33554432
while [ ! -f run.exit ]; do sleep 15; done
if [ "$(cat run.exit)" != 0 ]; then printf '1\n' > replay.exit; exit 1; fi
python3 prepare-sim.py > prepare-sim.log 2>&1 || { printf '2\n' > replay.exit; exit 2; }
cd tool || exit 1
/home/hclau/.cargo/bin/cargo +1.93.0 test --release > ../replay-tests.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
  /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bins > ../replay-build.log 2>&1
  rc=$?
fi
cd .. || exit 1
if [ "$rc" -eq 0 ]; then
  python3 phase-input.py > phase-input.log 2>&1
  rc=$?
fi
if [ "$rc" -eq 0 ]; then
  /usr/bin/time -v tool/target/release/map-phases observer/prepass.ops.bin observer/ops.bin phase-prepass.tsv phase-final.tsv > phase-map.log 2> phase-map.err
  rc=$?
fi
if [ "$rc" -eq 0 ]; then
  export PHASE_MAP="$PWD/phase-final.tsv"
  /usr/bin/time -v tool/target/release/phase-replay observer/ops.bin breakthrough-cost-profile-20261020-v1 0 512 2 phase-census.jsonl 8 > replay.log 2> replay.err
  rc=$?
fi
printf '%s\n' "$rc" > replay.exit
exit "$rc"
