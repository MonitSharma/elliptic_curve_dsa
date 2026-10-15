#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
FROZEN=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-ht25-bankswap-v2
LIB=/home/hclau/ecdsa_research/overnight-20261014/qubits/base
cd "$ROOT"
echo "$$" > components-v1.pid
trap 's=$?; echo "$s" > components-v1.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > components-v1-preflight.json
python3 prepare-cost-v1.py "$FROZEN" /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/candidate-ht25-bankswap-v2.patch "$ROOT"
for name in frozen control-fold-v1; do
  SOURCE="$FROZEN"
  if [ "$name" = control-fold-v1 ]; then SOURCE="$ROOT/candidate-control-fold-v1"; fi
  python3 prepare-component-profile.py "$SOURCE" "$LIB" "$ROOT/profile-$name"
  export CARGO_TARGET_DIR="$ROOT/profile-target"
  cargo +1.93.0 generate-lockfile --offline --manifest-path "profile-$name/Cargo.toml"
  /usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path "profile-$name/Cargo.toml" > "profile-$name.log" 2>&1
done
export CARGO_TARGET_DIR="$ROOT/candidate-target-v1"
for filter in ht25_ n275_ ph_owner_ cap24_counterexample8048 reserve9_; do
 /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-control-fold-v1/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
sha256sum candidate-control-fold-v1/src/point_add/midg.rs
date -u
