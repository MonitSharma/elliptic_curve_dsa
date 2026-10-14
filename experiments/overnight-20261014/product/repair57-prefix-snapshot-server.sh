#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/repair57-prefix-snapshot
runner=$root/product-repair57-prefix-snapshot
trap 'rc=$?; echo "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-repair57-prefix-snapshot-target RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 "$root/product-evidence/repair57-prefix-snapshot-prepare.py" "$root/product-fold75-replay" "$runner" "$evidence" "$root/product-evidence/repair57-production-pool"
sha256sum "$runner/src/main.rs" "$runner/src/y33_copy.rs" "$runner/Cargo.toml" "$root/product-evidence/c5-fold75/"{raw-body.bin,pre-y33.bin,boundaries.tsv} "$evidence/snapshot-frame.tsv" "$root/product-evidence/repair57-production-pool/before.json" > "$evidence/source-input.sha256"
cd "$runner"
/usr/bin/time -v cargo test --offline --locked --release -- --nocapture --test-threads=1 > "$evidence/tests.log" 2>&1
grep -q '3 passed; 0 failed' "$evidence/tests.log"
/usr/bin/time -v cargo build --offline --locked --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/product-evidence/c5-fold75/raw-body.bin" "$root/product-evidence/c5-fold75/boundaries.tsv" "$root/product-evidence/c5-fold75/raw-body.bin" "$root/product-evidence/c5-fold75/boundaries.tsv" "$root/product-b3-arithmetic-compare/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" "$runner/expected-finals.tsv" "$root/product-evidence/c5-fold75/pre-y33.bin" "$root/product-evidence/c5-fold75/pre-y33.bin" "$evidence/snapshot-frame.tsv" "$evidence/snapshot-frame.tsv"
sha256sum "$evidence/"*.tsv > "$evidence/output.sha256"
