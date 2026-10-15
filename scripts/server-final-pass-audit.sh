#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/followup-20261015
evidence="$root/final-pass-audit"
mkdir -p "$evidence"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$evidence/target" RUSTUP_TOOLCHAIN=1.93.0
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
base=/home/hclau/ecdsa_research/overnight-20261014/product-b3-baseline
python3 "$root/prepare-final-pass-audit.py" "$base" "$evidence/crate"
cd "$evidence/crate"
sha256sum src/*.rs Cargo.toml rust-toolchain > "$evidence/source.sha256"
cargo generate-lockfile --offline
cargo build --release --locked --offline > "$evidence/build.log" 2>&1
"$CARGO_TARGET_DIR/release/final_pass_audit" /home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-baseline/run/ops.bin 0 > "$evidence/analysis.log" 2>&1
