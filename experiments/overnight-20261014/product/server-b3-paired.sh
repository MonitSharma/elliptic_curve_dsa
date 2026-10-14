#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence=$root/product-evidence/b3-paired
runner=$root/product-b3-replay
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"; exit "$rc"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR=$root/product-b3-replay-target
export RUSTUP_TOOLCHAIN=1.93.0 RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
date -u
hostname
python3 "$evidence/prepare-b3-paired.py" "$root/product-b3-baseline" "$runner"
sha256sum "$runner/src/main.rs" "$runner/Cargo.toml" "$root/product-b3-baseline/src/bin/eval_circuit.rs" "$root/product-b3-baseline/src/sim.rs" "$root/product-b3-baseline/src/circuit.rs" > "$evidence/replay-source.sha256"
cd "$runner"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_paired_diagnostic" > "$evidence/native.sha256"
base=$root/product-evidence/b3-baseline/run/ops.bin
candidate=$root/coordinator-b3-classical-evidence/run/ops.bin
sha256sum "$base" "$candidate" > "$evidence/streams.sha256"
for family in independent structured candidate; do
 /usr/bin/time -v "$CARGO_TARGET_DIR/release/product_paired_diagnostic" "$base" "$candidate" "$family" "$evidence/$family.tsv"
done
sha256sum "$evidence/independent.tsv" "$evidence/structured.tsv" "$evidence/candidate.tsv" > "$evidence/packets.sha256"
date -u
