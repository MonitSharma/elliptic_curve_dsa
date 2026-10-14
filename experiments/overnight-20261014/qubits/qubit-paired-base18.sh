#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
mkdir -p evidence
trap 's=$?; echo "$s" > evidence/base-paired-batch18.exit' EXIT
test "$(cat evidence/base-stream-generation.exit)" = 0
ulimit -v 134217728
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_BUILD_JOBS=4
date -u
hostname
git -C base rev-parse HEAD
git -C base status --short
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/base-paired-batch18-preflight.json
sha256sum evidence/base-ops.bin evidence/compact-packet.tsv replay/src/main.rs
/usr/bin/time -v replay/target/release/qubit_replay_diagnostic paired evidence/base-ops.bin evidence/compact-packet.tsv 18
date -u
