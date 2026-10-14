#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/n275-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-n275/target
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n275-preflight.json
git -C candidate-n275 rev-parse HEAD
sha256sum candidate-n275/src/point_add/{frogdrop.rs,frogdrop_col.rs,midg.rs,pointadd_frogdrop.rs,tests_frogdrop.rs,tests_midg_k24.rs} evidence/candidate-n275.patch
for filter in n275_ ph_owner_ cap24_counterexample8048 reserve9_; do
  /usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-n275/Cargo.toml --bin build_circuit "$filter" -- --nocapture --test-threads=1
done
date -u
