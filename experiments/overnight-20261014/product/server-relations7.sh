#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/overnight-20261014/product
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/relations7
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-target
ulimit -v 16777216
. /home/hclau/.cargo/env
date -u
hostname
git rev-parse HEAD
git status --short
git diff --binary > "$evidence/modified.patch"
find src/point_add -type f -print0 | sort -z | xargs -0 sha256sum > "$evidence/source.sha256"
printf '%s\n' 'CARGO_BUILD_JOBS=4 library_threads=1 limit_vmem_kib=16777216' > "$evidence/settings.txt"
/usr/bin/time -v cargo test --offline --locked --release --bin build_circuit truth7_simplify -- --nocapture
/usr/bin/time -v cargo build --offline --locked --release --bin build_circuit --bin eval_circuit
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum ops.bin > "$evidence/ops.sha256"
cp ops.bin "$evidence/ops.bin"
date -u
