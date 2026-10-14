#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
mkdir -p evidence
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/base-stream.exit' EXIT
ulimit -v 134217728
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_BUILD_JOBS=4
unset D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
. /home/hclau/.cargo/env
date -u
hostname
git -C base rev-parse HEAD
git -C base status --short
sha256sum base/src/point_add/mod.rs base/src/point_add/midg.rs base/src/point_add/frogdrop.rs
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/base-stream-preflight.json
cd base
cargo +1.93.0 build --release --offline --locked --bin build_circuit
export LOWQ_EXACT_STREAM_PATH=/home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/base-ops.bin
/usr/bin/time -v target/release/build_circuit
sha256sum "$LOWQ_EXACT_STREAM_PATH"
date -u
