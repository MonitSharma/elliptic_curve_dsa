#!/usr/bin/env bash
set -euo pipefail
evidence=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/positive-production-broader
base=/home/hclau/ecdsa_research/overnight-20261014/product-evidence/positive-production
binary=/home/hclau/ecdsa_research/overnight-20261014/product-positive-production-replay-target/release/product_positive_production_replay
trap 'rc=$?; printf "%s\n" "$rc" > "$evidence/replay.exit"; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 8388608
date -u
sha256sum "$binary" "$base/raw-ops.bin" "$base/metadata.tsv" /home/hclau/ecdsa_research/overnight-20261014/product-positive-production-replay/src/main.rs /home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail/structured.tsv /home/hclau/ecdsa_research/overnight-20261014/product-evidence/classical-xor-factors/independent.tsv > "$evidence/source-native-packets.sha256"
cuts=$(cat "$base/cuts.txt")
wires=$(python3 -c 'import ast,sys; print(",".join(map(str,ast.literal_eval(next(x.split(" ",1)[1] for x in open(sys.argv[1]) if x.startswith("SQUARE_R0_WIRES "))))))' "$base/run.log")
for batch in 1 2 3; do /usr/bin/time -v "$binary" "$base/raw-ops.bin" /home/hclau/ecdsa_research/overnight-20261014/product-evidence/structured-detail/structured.tsv "$cuts" "$wires" "$base/metadata.tsv" "$batch"; done
for batch in 0 1 2 3; do /usr/bin/time -v "$binary" "$base/raw-ops.bin" /home/hclau/ecdsa_research/overnight-20261014/product-evidence/classical-xor-factors/independent.tsv "$cuts" "$wires" "$base/metadata.tsv" "$batch"; done
date -u
