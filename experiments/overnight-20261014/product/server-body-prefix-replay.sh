#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/body-prefix-replay
runner=$root/product-body-prefix-replay
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-body-prefix-replay-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 "$evidence/prepare-body-prefix-replay.py" "$root/product-b3-baseline" "$runner" "$root/product-evidence/b3-arithmetic-compare"
sha256sum "$runner/src/main.rs" "$runner/Cargo.toml" "$runner/expected-finals.tsv" "$root/product-b3-baseline/src/bin/eval_circuit.rs" "$root/product-b3-baseline/src/sim.rs" "$root/product-b3-baseline/src/circuit.rs" > "$evidence/source.sha256"
cd "$runner"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
while ! test -e "$root/product-evidence/b3-body-boundaries/run.exit"; do sleep 5; done
test "$(cat "$root/product-evidence/b3-body-boundaries/run.exit")" = 0
test "$(cat "$root/product-evidence/c5-body-boundaries/run.exit")" = 0
sha256sum "$root/product-evidence/c5-body-boundaries/raw-body.bin" "$root/product-evidence/c5-body-boundaries/boundaries.tsv" "$root/product-evidence/b3-body-boundaries/raw-body.bin" "$root/product-evidence/b3-body-boundaries/boundaries.tsv" "$root/product-b3-arithmetic-compare/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" > "$evidence/input.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$root/product-evidence/c5-body-boundaries/raw-body.bin" "$root/product-evidence/c5-body-boundaries/boundaries.tsv" "$root/product-evidence/b3-body-boundaries/raw-body.bin" "$root/product-evidence/b3-body-boundaries/boundaries.tsv" "$root/product-b3-arithmetic-compare/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" "$runner/expected-finals.tsv"
date -u
