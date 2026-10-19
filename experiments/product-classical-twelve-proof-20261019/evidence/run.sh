#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-twelve-proof-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-twelve-proof-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v11.py > preflight.json
sha256sum *.py Cargo.toml run.sh ../autonomous-20261019/preflight_v11.py > SOURCE.sha256
ulimit -v 33554432
python3 prepare.py > prepare.log 2>&1
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bins > build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/classical_twelve_proof" "$CARGO_TARGET_DIR/release/classical_twelve_edits" > BINARY.sha256
export AUDIT_OUT="$r/AUDIT.json"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_twelve_proof" ../product-classical-nine-20261019/candidate/ops.bin "$r/reproduced" 4b81cbc1e247e791ab11ff56c5f84b4da5edc8618d7c19fe590305390fa6f93f > reproduce.log 2>&1
python3 prove.py > prove.log 2>&1
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_twelve_edits" "$r" > edits.log 2>&1
