#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
mkdir -p evidence
trap 's=$?; echo "$s" > evidence/compact-exact-batch18.exit' EXIT
ulimit -v 134217728
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_BUILD_JOBS=4
date -u
hostname
git -C base rev-parse HEAD
git -C base status --short
sha256sum compact/src/point_add/frogdrop.rs compact/src/point_add/midg.rs compact/src/point_add/tests_midg_k24.rs replay/src/main.rs replay/Cargo.lock
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/compact-exact-batch18-preflight.json
/usr/bin/time -v replay/target/release/qubit_replay_diagnostic exact /home/hclau/ecdsa_research/qubits/ops.bin evidence/compact-packet.tsv 18
sha256sum evidence/compact-packet.tsv
date -u
