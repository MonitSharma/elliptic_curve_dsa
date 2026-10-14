#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/phase-anchors
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/prefix.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis/target
ulimit -v 8388608
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/overnight-20261014/product-match-phase-anchors.py /home/hclau/ecdsa_research/overnight-20261014/product-scan-streams.py "$evidence/run.log" "$evidence/ops.bin" "$evidence/anchors8.json" 8
cd /home/hclau/ecdsa_research/overnight-20261014/product-prefix-replay
sha256sum src/main.rs Cargo.toml "$evidence/ops.bin" > "$evidence/prefix-source.sha256"
/usr/bin/time -v cargo build --offline --release
cuts=$(python3 -c 'import json,sys; j=json.load(open(sys.argv[1])); print(",".join(x["phase"]+":"+str(x["prefix_end"]) for x in j["selected"] if x["raw_distance"]==0))' "$evidence/anchors8.json")
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_prefix_replay" "$evidence/ops.bin" /home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail/structured.tsv "$cuts"
