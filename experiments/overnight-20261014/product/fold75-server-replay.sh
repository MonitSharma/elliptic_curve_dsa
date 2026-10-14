#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/fold75-replay
runner=$root/product-fold75-replay
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-fold75-replay-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 "$evidence/fold75-prepare-replay.py" "$root/product-b3-baseline" "$runner" "$root/product-evidence/b3-arithmetic-compare"
sha256sum "$runner/src/main.rs" "$runner/src/y33_copy.rs" "$runner/Cargo.toml" "$runner/expected-finals.tsv" "$root/product-b3-baseline/src/point_add/y33_clears.rs" "$root/product-b3-baseline/src/bin/eval_circuit.rs" "$root/product-b3-baseline/src/sim.rs" "$root/product-b3-baseline/src/circuit.rs" > "$evidence/source.sha256"
cmp "$root/product-c5-fold75/src/point_add/y33_clears.rs" "$root/product-b3-baseline/src/point_add/y33_clears.rs"
cd "$runner"
/usr/bin/time -v cargo test --offline --release -- --nocapture --test-threads=1
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
for kind in c5 b3; do
 while ! test -e "$root/product-evidence/$kind-fold75/run.exit"; do sleep 5; done
 test "$(cat "$root/product-evidence/$kind-fold75/run.exit")" = 0
done
sha256sum "$root/product-evidence/c5-fold75/fold-frames.tsv" "$root/product-evidence/b3-fold75/fold-frames.tsv" "$root/product-evidence/c5-fold75/raw-body.bin" "$root/product-evidence/c5-fold75/pre-y33.bin" "$root/product-evidence/c5-fold75/boundaries.tsv" "$root/product-evidence/b3-fold75/raw-body.bin" "$root/product-evidence/b3-fold75/pre-y33.bin" "$root/product-evidence/b3-fold75/boundaries.tsv" "$root/product-b3-arithmetic-compare/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" > "$evidence/input.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/product-evidence/c5-fold75/raw-body.bin" "$root/product-evidence/c5-fold75/boundaries.tsv" "$root/product-evidence/b3-fold75/raw-body.bin" "$root/product-evidence/b3-fold75/boundaries.tsv" "$root/product-b3-arithmetic-compare/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" "$runner/expected-finals.tsv" "$root/product-evidence/c5-fold75/pre-y33.bin" "$root/product-evidence/b3-fold75/pre-y33.bin" "$root/product-evidence/c5-fold75/fold-frames.tsv" "$root/product-evidence/b3-fold75/fold-frames.tsv"
date -u
