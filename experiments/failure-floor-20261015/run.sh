#!/bin/bash
set -uo pipefail
cd /home/hclau/ecdsa_research/failure-floor-20261015
echo $$ > run.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/failure-floor-20261015/run.exit; exit "$s"' EXIT
ulimit -v 62914560
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > preflight.json
if [ ! -d observer-b3 ]; then python3 prepare.py > prepare.log 2>&1 || exit $?; fi
cd observer-b3
cargo build --release --locked --offline --bin build_circuit > ../build.log 2>&1 || exit $?
/usr/bin/time -v target/release/build_circuit > ../generate.log 2>&1 || exit $?
sha256sum ops.bin > ../stream.sha256
sha256sum target/release/build_circuit > ../binary.sha256
git diff --binary > ../observer-tracked.patch
