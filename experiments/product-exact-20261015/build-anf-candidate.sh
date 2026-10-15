#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > candidate-anf.pid
trap 'rc=$?; echo "$rc" > "$root/candidate-anf.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=2 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > candidate-anf-preflight.json
python3 prepare_anf_candidate.py > candidate-anf-prepare.log 2>&1
cd candidate-anf512
cargo build --release --locked --offline --bin build_circuit > ../candidate-anf-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../candidate-anf-generate.log 2>&1
sha256sum ops.bin > ../candidate-anf.sha256
cmp ops.bin ../cache-anf-512.bin
