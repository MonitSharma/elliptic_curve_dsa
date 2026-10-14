#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
candidate="$root/coordinator-b3-classical"
evidence="$root/coordinator-b3-classical-evidence"
mkdir -p "$evidence/run"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"; python3 "$root/research-receipt.py" "$candidate" "$evidence/receipt" --log "$evidence/run.log" --exit "$evidence/run.exit" --stream "$evidence/run/ops.bin" --score "$evidence/run/score.json" --full-benchmark' EXIT
ulimit -v 16777216
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
sha256sum "$root/prepare-b3-classical.py" "$root/server-b3-classical.sh" > "$evidence/research-source.sha256"
python3 "$root/prepare-b3-classical.py" "$candidate" "$root/product-candidate" "$evidence"
. /home/hclau/.cargo/env
export CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$evidence/target"
cd "$candidate"
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$CARGO_TARGET_DIR" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 cargo test --offline --locked --release --bin build_circuit classical_factors_xor -- --nocapture --test-threads=1
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" CARGO_BUILD_JOBS=4 CARGO_TARGET_DIR="$CARGO_TARGET_DIR" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 cargo build --offline --locked --release --bin build_circuit --bin eval_circuit
sha256sum "$CARGO_TARGET_DIR/release/build_circuit" "$CARGO_TARGET_DIR/release/eval_circuit" > "$evidence/binary.sha256"
cd "$evidence/run"
test ! -e ops.bin && test ! -e results.tsv && test ! -e score.json
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$CARGO_TARGET_DIR/release/build_circuit"
sha256sum ops.bin > "$evidence/stream.sha256"
python3 "$root/product-scan-streams.py" ops.bin --out "$evidence/stream-diagnostic.json"
/usr/bin/time -v env -i HOME="$HOME" PATH="$PATH" USER="$USER" RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$CARGO_TARGET_DIR/release/eval_circuit" --note 'B3 public Toffoli source, unchanged nonce and protected harness, generic exact classical-factor pass'
date -u
