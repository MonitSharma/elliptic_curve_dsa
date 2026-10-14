#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/reserve9-payload-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/reserve9-payload-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-reserve9-payload/target
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/reserve9-payload-preflight.json
git -C candidate-reserve9-payload rev-parse HEAD
sha256sum candidate-reserve9-payload/src/point_add/frogdrop.rs candidate-reserve9-payload/src/point_add/midg.rs candidate-reserve9-payload/src/point_add/tests_midg_k24.rs evidence/candidate-reserve9-payload.patch
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-reserve9-payload/Cargo.toml --bin build_circuit reserve9_crossing_payload_3713 -- --nocapture --test-threads=1
date -u
