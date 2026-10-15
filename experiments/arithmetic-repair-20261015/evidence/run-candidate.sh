#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/arithmetic-repair-20261015
echo $$ > "$root/candidate.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/candidate.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/candidate-preflight.json"
python3 "$root/prepare-candidate.py" normal > "$root/candidate-prepare.log" 2>&1
cd "$root/candidate-fold104-b3"
cargo build --release --locked --offline --bin build_circuit > "$root/candidate-build.log" 2>&1
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" > "$root/candidate-binary.sha256"
/usr/bin/time -v "$CARGO_TARGET_DIR/release/build_circuit" > "$root/candidate-generation.log" 2>&1
sha256sum ops.bin "$root/candidate-generation.log" > "$root/candidate-bindings.sha256"
