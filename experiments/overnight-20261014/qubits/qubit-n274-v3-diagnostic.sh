#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/n274-v3-diagnostic-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n274-v3-diagnostic-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/diagnostic-n274-v3/target
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n274-v3-diagnostic-preflight.json
for filter in n274_diagnostic_payload3713_stages; do
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path diagnostic-n274-v3/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
sha256sum diagnostic-n274-v3/target/release/deps/build_circuit-*
date -u
