#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/original-all.exit' EXIT
ulimit -v 134217728
export CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
. /home/hclau/.cargo/env
date -u
hostname
git -C base rev-parse HEAD
git -C base status --short
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/original-all-preflight.json
ps -eo pid,rss,pcpu,comm --sort=-rss | head -10
python3 qubit-create-original-all.py replay-many replay-original-all
CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/replay/target cargo +1.93.0 build --release --offline --manifest-path replay-original-all/Cargo.toml
sha256sum replay-original-all/src/main.rs replay-original-all/Cargo.lock replay/target/release/qubit_replay_original_all_diagnostic
sha256sum /home/hclau/ecdsa_research/qubits/ops.bin
/usr/bin/time -v replay/target/release/qubit_replay_original_all_diagnostic /home/hclau/ecdsa_research/qubits/ops.bin evidence/original-all-packet.tsv > evidence/original-all-results.log 2>&1
sha256sum evidence/original-all-packet.tsv evidence/compact-packet.tsv
cmp evidence/original-all-packet.tsv evidence/compact-packet.tsv
date -u
