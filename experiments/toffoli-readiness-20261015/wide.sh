#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/toffoli-readiness-20261015
evidence="$root/wide-evidence"
mkdir -p "$evidence"
echo $$ > "$root/wide.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/run.exit"' EXIT
ulimit -v 16777216
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR="$root/target" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
python3 "$root/prepare-wide.py" > "$evidence/prepare.log" 2>&1
cd "$root/candidate-wide-v1"
python3 /home/hclau/ecdsa_research/followup-20261015/research-receipt.py "$PWD" "$evidence/before"
cargo test --release --locked --offline --bin build_circuit wide_cache_ -- --nocapture --test-threads=1 > "$evidence/native.log" 2>&1
grep -q '2 passed; 0 failed' "$evidence/native.log"
cargo build --release --locked --offline --bin build_circuit > "$evidence/build.log" 2>&1
cp "$CARGO_TARGET_DIR/release/build_circuit" "$evidence/build_circuit"
sha256sum "$evidence/build_circuit" > "$evidence/binary.sha256"
/usr/bin/time -v "$evidence/build_circuit" > "$evidence/generation.log" 2>&1
sha256sum ops.bin > "$evidence/stream.sha256"
python3 /home/hclau/ecdsa_research/followup-20261015/research-receipt.py "$PWD" "$evidence/terminal" --stream "$PWD/ops.bin"
