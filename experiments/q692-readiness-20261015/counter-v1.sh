#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
LIB=/home/hclau/ecdsa_research/overnight-20261014/qubits/base
FROZEN=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-ht25-bankswap-v2
cd "$ROOT"
echo "$$" > counter-v1.pid
trap 's=$?; echo "$s" > counter-v1.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1 F1_PROFILE=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL FROGDROP_CK
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > counter-v1-preflight.json
for name in frozen control-fold-v1; do
 SOURCE="$FROZEN"
 if [ "$name" = control-fold-v1 ]; then SOURCE="$ROOT/candidate-control-fold-v1"; fi
 python3 prepare-counter-profile.py "$SOURCE" "$LIB" "$ROOT/counter-$name"
 export CARGO_TARGET_DIR="$ROOT/counter-target"
 cargo +1.93.0 generate-lockfile --offline --manifest-path "counter-$name/Cargo.toml"
 /usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path "counter-$name/Cargo.toml" > "counter-$name.log" 2>&1
done
date -u
