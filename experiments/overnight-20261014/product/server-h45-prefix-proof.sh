#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/h45-prefix-proof
runner=$root/product-h45-prefix-proof
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-h45-prefix-proof-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 "$evidence/prepare-h45-prefix-proof.py" "$root/product-h45-fold-trace" "$runner" "$evidence/h45-original-fold-contexts.json" "$root/product-h45-actual-contexts/src/point_add/product_h45_phase_kernel.rs"
sha256sum "$runner/src/main.rs" "$runner/Cargo.toml" "$runner/contexts.tsv" "$runner/src/product_phase_kernel.rs" "$root/product-h45-fold-trace/src/bin/eval_circuit.rs" "$root/product-h45-fold-trace/src/sim.rs" "$root/product-h45-fold-trace/src/circuit.rs" > "$evidence/source.sha256"
cd "$runner"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
raw=$root/product-evidence/raw-handoff/raw-ops.bin
independent=$root/product-evidence/classical-xor-factors/independent.tsv
structured=$root/product-evidence/classical-xor-factors/structured.tsv
sha256sum "$raw" "$independent" "$structured" > "$evidence/input.sha256"
sha256sum -c <(printf 'eca53f6002583b148973ec0ebfb453839038b92984e3356bec8e24e6c662e683  %s\n' "$raw")
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$raw" "$runner/contexts.tsv" "$root/product-evidence/h45-production-export/components" "$independent" "$structured" "$evidence/component-cost.tsv"
date -u
