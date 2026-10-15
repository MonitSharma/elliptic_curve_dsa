#!/bin/bash
set -euo pipefail
root=/home/hclau/ecdsa_research/guard-tree-20261015
cd "$root"
echo $$ > before.pid
trap 's=$?;echo "$s" > "$root/before.exit"' EXIT
ulimit -v 52428800
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
python3 /home/hclau/ecdsa_research/server-preflight.py > before-preflight.json
python3 prepare-before.py > before-prepare.log 2>&1
cd tip-before
cargo build --release --locked --offline --bin build_circuit > ../before-build.log 2>&1
/usr/bin/time -v target/release/build_circuit > ../before-generate.log 2>&1
sha256sum ../before-square-finish.bin > ../before-stream.sha256
