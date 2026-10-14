#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/dirty-k32-components.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/dirty-k32-components-preflight.json
git -C component-dirty-k32 rev-parse HEAD
git -C component-dirty-k32 status --short
sha256sum component-dirty-k32/src/point_add/frogdrop.rs component-dirty-k32/src/point_add/midg.rs component-dirty-k32/src/point_add/tests_midg_k24.rs evidence/component-dirty-k32.patch
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path component-dirty-k32/Cargo.toml --bin build_circuit compact_dirty_remainder_partition -- --nocapture --test-threads=1
/usr/bin/time -v cargo +1.93.0 test --release --locked --offline --manifest-path component-dirty-k32/Cargo.toml --bin build_circuit compact_k32_borrowed -- --nocapture --test-threads=1
date -u
