#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/positive-production
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/replay.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-positive-production-replay-target
ulimit -v 8388608
. /home/hclau/.cargo/env
date -u
cd /home/hclau/ecdsa_research/overnight-20261014/product-positive-production-replay
sha256sum src/main.rs Cargo.toml "$evidence/raw-ops.bin" "$evidence/metadata.tsv" > "$evidence/replay-source.sha256"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_positive_production_replay" > "$evidence/replay-native.sha256"
cuts=$(python3 /home/hclau/ecdsa_research/overnight-20261014/map-producer-observations.py "$evidence/run.log" "$evidence/metadata.tsv")
wires=$(python3 -c 'import ast,sys; print(",".join(map(str,ast.literal_eval(next(x.split(" ",1)[1] for x in open(sys.argv[1]) if x.startswith("SQUARE_R0_WIRES "))))))' "$evidence/run.log")
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_positive_production_replay" "$evidence/raw-ops.bin" /home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail/structured.tsv "$cuts" "$wires" "$evidence/metadata.tsv" 0
date -u
