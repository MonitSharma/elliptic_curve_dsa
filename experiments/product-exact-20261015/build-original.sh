#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
echo $$ > original.pid
trap 'rc=$?; echo "$rc" > "$root/original.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 62914560
python3 /home/hclau/ecdsa_research/server-preflight.py > original-preflight.json
cd tip
cargo build --release --locked --offline --bin build_circuit > ../original-build.log 2>&1
/usr/bin/time -v ./target/release/build_circuit > ../original-generate.log 2>&1
sha256sum ops.bin > ../original.sha256
