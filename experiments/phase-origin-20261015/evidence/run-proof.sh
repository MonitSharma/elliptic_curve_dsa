#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/phase-origin-20261015
echo $$ > "$root/proof.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$root/proof.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/proof-target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
test ! -e "$CARGO_TARGET_DIR"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$root/proof-preflight.json"
python3 "$root/prepare-proof.py" > "$root/proof-prepare.log" 2>&1
cd "$root/frame-proof-b3"
cargo test --release --locked --offline --bin build_circuit tests_terminal_frame -- --nocapture --test-threads=1 > "$root/proof.log" 2>&1
