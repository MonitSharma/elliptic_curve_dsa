#!/usr/bin/env bash
set -euo pipefail
label=$1
case "$label" in unbound-base|unbound-full-cross) ;; *) exit 2;; esac
packet=${2:-/home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail/structured.tsv}
evidence="/home/hclau/ecdsa_research/overnight-20261014/product-evidence/$label"
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/consumer.exit"' EXIT
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RUSTUP_TOOLCHAIN=1.93.0
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/product-anf-analysis/target
ulimit -v 8388608
. /home/hclau/.cargo/env
date -u
cd /home/hclau/ecdsa_research/overnight-20261014/product-consumer-prefix-replay
sha256sum src/main.rs Cargo.toml "$evidence/raw-ops.bin" "$packet" > "$evidence/consumer-source.sha256"
/usr/bin/time -v cargo build --offline --release
sha256sum "$CARGO_TARGET_DIR/release/product_consumer_prefix_replay" > "$evidence/consumer-native.sha256"
cuts=$(python3 -c 'import sys; d={}; [d.update({x.split()[1]:int(x.split()[3])}) for x in open(sys.argv[1]) if x.startswith("PHASE_ANCHOR ")]; print(",".join(k+":"+str(v) for k,v in d.items()))' "$evidence/run.log")
wires=$(python3 -c 'import ast,sys; print(",".join(map(str,ast.literal_eval(next(x.split(" ",1)[1] for x in open(sys.argv[1]) if x.startswith("SQUARE_R0_WIRES "))))))' "$evidence/run.log")
/usr/bin/time -v "$CARGO_TARGET_DIR/release/product_consumer_prefix_replay" "$evidence/raw-ops.bin" "$packet" "$cuts" "$wires"
date -u
