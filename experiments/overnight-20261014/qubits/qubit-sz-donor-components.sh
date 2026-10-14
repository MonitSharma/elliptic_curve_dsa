#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
echo "$$" > evidence/sz-donor-components.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/sz-donor-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/sz-donor-components-preflight.json
git -C component-sz-donors rev-parse HEAD
sha256sum component-sz-donors/src/point_add/frogdrop.rs component-sz-donors/src/point_add/midg.rs component-sz-donors/src/point_add/tests_midg_k24.rs evidence/component-sz-donors.patch
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path component-sz-donors/Cargo.toml --bin build_circuit sz_donor_normalization -- --nocapture --test-threads=1
date -u
