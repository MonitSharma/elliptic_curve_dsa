#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-classical-nine-proof-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-classical-nine-proof-20261019/run.exit' EXIT
python3 ../autonomous-20261019/preflight_v6.py > preflight.json
sha256sum prepare.py prove.py run.sh Cargo.toml ../autonomous-20261019/preflight_v6.py > SOURCE.sha256
python3 prepare.py > prepare.log 2>&1
ulimit -v 33554432
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=1 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export RUSTUP_TOOLCHAIN=stable CARGO_TARGET_DIR=/home/hclau/ecdsa_research/product-order-20261019/target
cargo build --release --offline --bin classical_nine_proof > build.log 2>&1
sha256sum "$CARGO_TARGET_DIR/release/classical_nine_proof" > BINARY.sha256
export AUDIT_OUT="$r/AUDIT.json"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/classical_nine_proof" ../product-pareto-20261019/candidate-parent4/ops.bin "$r/reproduced" 97c40ed1dd3f5123c9554ebf29c54c433960804c0effce63dc7bba52844ae9ae > reproduce.log 2>&1
python3 prove.py > prove.log 2>&1
