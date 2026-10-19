#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-type-probe-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-type-probe-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v5.py > preflight.json
sha256sum type_probe.rs io.rs Cargo.toml run.sh ../autonomous-20261019/preflight_v5.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin classical_type_probe > tests.log 2>&1
cargo build --release --offline --bin classical_type_probe > build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/classical_type_probe" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_type_probe" ../product-pareto-20261019/parent/ops.bin public.json 429af1c31b54064e17e7602be516b519c066c241e218d56f002287ea02b16842 > public.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_type_probe" ../product-classical-factors-refresh-20261019/parent4.ops.bin after-eight.json f64a9d8c59cdc89e9b683988da84eb34fa78c5a884f0324ce824e4c07a00fa53 > after-eight.log 2>&1
