#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
name=$1
out=tail-precision-20261016
trap 'rc=$?; echo "$rc" > "$root/$out/$name-build.exit"' EXIT
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/$name-build-preflight.json"
python3 prepare_tail_precision.py "$name" > "$out/$name-prepare.log" 2>&1
cd "candidate-product-tail-$name"
cargo build --release --locked --offline --bin build_circuit > "../$out/$name-build.log" 2>&1
/usr/bin/time -v ./target/release/build_circuit > "../$out/$name-generate.log" 2>&1
sha256sum ops.bin > "../$out/$name-stream.sha256"
cargo test --release --locked --offline --bin build_circuit point_add -- --test-threads=1 > "../$out/$name-native-tests.log" 2>&1
cd "$root"
python3 stream_resources.py "candidate-product-tail-$name/ops.bin" > "$out/$name-resources.jsonl"
