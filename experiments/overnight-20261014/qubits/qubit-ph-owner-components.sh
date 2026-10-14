#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/ph-owner-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ph-owner-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-ph-owner/target
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/ph-owner-preflight.json
git -C candidate-ph-owner rev-parse HEAD
sha256sum candidate-ph-owner/src/point_add/frogdrop.rs candidate-ph-owner/src/point_add/midg.rs candidate-ph-owner/src/point_add/pointadd_frogdrop.rs candidate-ph-owner/src/point_add/tests_midg_k24.rs evidence/candidate-ph-owner.patch evidence/ph-owner-structured-fixture.json
for filter in ph_owner_ cap24_counterexample8048 reserve9_; do
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-ph-owner/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
date -u
