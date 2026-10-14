#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/k32-column-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/k32-column-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/k32-column-components-preflight.json
git -C component-k32-columns rev-parse HEAD
sha256sum component-k32-columns/src/point_add/frogdrop.rs component-k32-columns/src/point_add/midg.rs component-k32-columns/src/point_add/tests_midg_k24.rs evidence/component-k32-columns.patch evidence/k32-column-fixtures.json
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path component-k32-columns/Cargo.toml --bin build_circuit k32_exact_column_crossings -- --nocapture --test-threads=1
date -u
