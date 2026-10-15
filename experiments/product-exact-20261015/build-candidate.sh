#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > candidate.pid
trap 'rc=$?; echo "$rc" > "$root/candidate.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > candidate-preflight.json
python3 prepare_candidate.py > candidate-prepare.log 2>&1
cd candidate-split128
cargo build --release --locked --offline --bin build_circuit > ../candidate-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../candidate-generate.log 2>&1
sha256sum ops.bin > ../candidate.sha256
cmp ops.bin ../split-128-density.bin
