#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-factors-refresh-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-factors-refresh-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum refresh_factors.rs hash_ops.rs proof/*.rs io.rs Cargo.toml run.sh preflight.py prepare.py EXTRACTION.json > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin refresh_classical_factors > tests.log 2>&1
cargo build --release --offline --bins > build.log 2>&1
ln -s "$CARGO_TARGET_DIR/release/hash_classical_ops" hash_ops
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/refresh_classical_factors" "$CARGO_TARGET_DIR/release/hash_classical_ops" > BINARY.sha256
python3 cases.py > cases.tsv
while IFS=$'\t' read -r name input sha; do
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/refresh_classical_factors" "$input" "$name" "$sha" > "$name.log" 2>&1
done < cases.tsv
