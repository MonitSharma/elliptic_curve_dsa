#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-two-target-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-two-target-20261019/run.exit' EXIT
while [ ! -f ../product-guard-mrfree-20261019/run-v2.exit ]; do sleep 15; done
test "$(cat ../product-guard-mrfree-20261019/run-v2.exit)" = 0
python3 preflight.py > preflight.json
sha256sum two_target.rs io.rs Cargo.toml run.sh cases.py preflight.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin two_target > tests.log 2>&1
cargo build --release --offline --bin two_target > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/two_target" > BINARY.sha256
python3 cases.py > cases.tsv
while IFS=$'\t' read -r name input gap sha; do
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/two_target" "$input" "$name" "$gap" "$sha" > "$name.log" 2>&1
done < cases.tsv
