#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/k32-initial-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/k32-initial-components-preflight.json
sha256sum candidate-k32/src/point_add/frogdrop.rs candidate-k32/src/point_add/midg.rs candidate-k32/src/point_add/tests_midg_k24.rs evidence/candidate-k32-initial.patch
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-k32/Cargo.toml --bin build_circuit k25_counterexample_col35 -- --nocapture --test-threads=1
date -u
