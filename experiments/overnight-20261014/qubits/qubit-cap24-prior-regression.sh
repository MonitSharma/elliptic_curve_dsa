#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/cap24-prior-regression.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/cap24-prior-regression.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/candidate-cap24-purehr/target
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/cap24-prior-regression-preflight.json
sha256sum candidate-cap24-purehr/src/point_add/frogdrop.rs candidate-cap24-purehr/src/point_add/midg.rs candidate-cap24-purehr/src/point_add/pointadd_frogdrop.rs candidate-cap24-purehr/src/point_add/tests_midg_k24.rs
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path candidate-cap24-purehr/Cargo.toml --bin build_circuit reserve9_ -- --nocapture --test-threads=1
date -u
