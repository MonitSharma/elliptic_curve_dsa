#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/ht25-v8-components.pid
trap 'code=$?; echo "$code" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ht25-v8-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/ht25-v8-preflight.json
git clone --quiet --no-hardlinks base candidate-ht25-v8
python3 qubit-create-ht25-v8.py candidate-ht25-v1 candidate-ht25-v8 evidence > evidence/ht25-v8-preparation.log
export CARGO_TARGET_DIR="$root/candidate-ht25-v8/target"
for filter in ht25_ n275_ ph_owner_ cap24_counterexample8048 reserve9_; do
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-ht25-v8/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
sha256sum "$CARGO_TARGET_DIR"/release/deps/build_circuit-*
date -u
