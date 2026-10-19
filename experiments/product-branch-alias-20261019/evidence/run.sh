#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-branch-alias-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-branch-alias-20261019/run.exit' EXIT
while [ ! -f ../product-two-target-20261019/run.exit ]; do sleep 15; done
test "$(cat ../product-two-target-20261019/run.exit)" = 0
python3 preflight.py > preflight.json
sha256sum alias_probe.rs io.rs Cargo.toml run.sh preflight.py prepare.py qualify.py > SOURCE.sha256
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=stable
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo test --release --offline --bin branch_alias_probe > tests.log 2>&1
cargo build --release --offline --bin branch_alias_probe > build.log 2>&1
sha256sum Cargo.lock "$CARGO_TARGET_DIR/release/branch_alias_probe" > BINARY.sha256
/usr/bin/time -v "$CARGO_TARGET_DIR/release/branch_alias_probe" ../product-pareto-20261019/parent/ops.bin probe > probe.log 2>&1
python3 qualify.py > QUALIFICATION.json
