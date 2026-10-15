#!/usr/bin/env bash
set -eu
ROOT=/home/hclau/ecdsa_research/q692_readiness_20261015
BASE=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$ROOT"
echo "$$" > "$ROOT/components-v7.pid"
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/q692_readiness_20261015/components-v7.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
python3 /home/hclau/ecdsa_research/server-preflight.py > components-v7-preflight.json
python3 prepare-cost-v7.py "$ROOT" > prepare-cost-v7.log
export CARGO_TARGET_DIR="$ROOT/candidate-target-v7"
for filter in ht25_ n275_ ph_owner_ cap24_counterexample8048 reserve9_; do
 /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-control-fold-v7/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
python3 "$BASE/qubit-prepare-ht25-bankswap-v2-decision-proof.py" "$ROOT/candidate-control-fold-v7" "$BASE/base" "$ROOT/phase-control-fold-v7" "$BASE/evidence/ht25-bankswap-v2-decision/crate/phase-audit-kernel.rs" > phase-v7-source.json
export CARGO_TARGET_DIR="$ROOT/phase-target-v7"
cargo +1.93.0 generate-lockfile --offline --manifest-path phase-control-fold-v7/Cargo.toml
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path phase-control-fold-v7/Cargo.toml coordinator_ -- --nocapture --test-threads=1 > phase-v7-proof.log 2>&1
python3 prepare-counter-profile.py "$ROOT/candidate-control-fold-v7" "$BASE/base" "$ROOT/counter-control-fold-v7"
export CARGO_TARGET_DIR="$ROOT/counter-target-v7" F1_PROFILE=1
cargo +1.93.0 generate-lockfile --offline --manifest-path counter-control-fold-v7/Cargo.toml
/usr/bin/time -v cargo +1.93.0 run --release --locked --offline --manifest-path counter-control-fold-v7/Cargo.toml > counter-control-fold-v7.log 2>&1
date -u
