#!/usr/bin/env bash
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/n275-v2-serializer.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-serializer.exit' EXIT
ulimit -v 16777216
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_TARGET_DIR="$root/candidate-n275-v2/target"
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n275-v2-serializer-preflight.json
sha256sum candidate-n275-v2/src/point_add/builder.rs candidate-n275-v2/src/bin/build_circuit.rs evidence/candidate-n275-v2.patch
/usr/bin/time -v cargo +1.93.0 test --release --offline --locked --manifest-path candidate-n275-v2/Cargo.toml --bin build_circuit serializer_matches_unchanged_harness_bytes -- --nocapture --test-threads=1
date -u
