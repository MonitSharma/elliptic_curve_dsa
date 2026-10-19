#!/bin/bash
set -euo pipefail
r=/home/hclau/ecdsa_research/product-anf-20261019
cd "$r"
trap 'rc=$?; printf "%s\n" "$rc" > /home/hclau/ecdsa_research/product-anf-20261019/run.exit' EXIT
python3 preflight.py > preflight.json
sha256sum anf.rs io.rs Cargo.toml run.sh preflight.py > SOURCE.sha256
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export RUSTUP_TOOLCHAIN=stable
cargo test --release --offline --bin anf > tests.log 2>&1
cargo build --release --offline --bin anf > build.log 2>&1
sha256sum Cargo.lock target/release/anf > BINARY.sha256
/usr/bin/time -v target/release/anf ../product-pareto-20261019/parent/ops.bin public-parent > scan.log 2>&1
