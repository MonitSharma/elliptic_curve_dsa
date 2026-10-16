#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=category-restore-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
source /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 41943040
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
python3 prepare_category_restore.py > "$out/prepare.log" 2>&1
cd candidate-product-restore-deletions
cargo build --release --locked --offline --bin build_circuit > "../$out/build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "../$out/generate.log" 2>&1
sha256sum ops.bin > "../$out/stream.sha256"
cargo test --release --locked --offline --bin build_circuit point_add -- --test-threads=1 > "../$out/native-tests.log" 2>&1
cd "$root"
python3 stream_resources.py candidate-product-restore-deletions/ops.bin > "$out/resources.jsonl"
