#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/b3-arithmetic-compare
runner=$root/product-b3-arithmetic-compare
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-b3-arithmetic-compare-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 "$evidence/prepare-b3-arithmetic-compare.py" "$root/product-b3-baseline" "$runner" "$root/product-evidence/b3-paired"
sha256sum "$runner/src/main.rs" "$runner/Cargo.toml" "$runner/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv" > "$evidence/source-packets.sha256"
cd "$runner"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
c5=$root/product-evidence/raw-handoff/raw-ops.bin
b3=$root/product-evidence/b3-earlier-stages/raw-body.bin
positive=$root/product-evidence/positive-production/raw-ops.bin
sha256sum "$c5" "$b3" "$positive" > "$evidence/streams.sha256"
sha256sum -c <(printf 'eca53f6002583b148973ec0ebfb453839038b92984e3356bec8e24e6c662e683  %s\nada7ef5264de0d6e600707c2e0672593014006038e454c24e6c74b19b7ca5e10  %s\nf6b272fc274c47db4d5a8f135144acd00582b9cf31022d18fb48e1cd262c346a  %s\n' "$c5" "$b3" "$positive")
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$c5" "$b3" "$positive" "$runner/known-official-failures.tsv" "$root/product-evidence/b3-paired/independent.tsv"
date -u
