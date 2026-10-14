#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
mkdir -p evidence
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/paired-many.exit' EXIT
ulimit -v 134217728
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_BUILD_JOBS=4
. /home/hclau/.cargo/env
python3 qubit-create-replay-many.py replay replay-many
CARGO_TARGET_DIR=/home/hclau/ecdsa_research/overnight-20261014/qubits/replay/target cargo +1.93.0 build --release --offline --manifest-path replay-many/Cargo.toml
sha256sum replay-many/src/main.rs replay-many/Cargo.lock evidence/compact-packet.tsv
for variant in base compact; do
  date -u
  python3 /home/hclau/ecdsa_research/server-preflight.py > "evidence/paired-many-${variant}-preflight.json"
  ps -eo pid,rss,pcpu,comm --sort=-rss | head -10
  if test "$variant" = base; then stream=evidence/base-ops.bin; else stream=/home/hclau/ecdsa_research/qubits/ops.bin; fi
  sha256sum "$stream"
  /usr/bin/time -v replay/target/release/qubit_replay_many_diagnostic "$stream" evidence/compact-packet.tsv 18,30,64,65,125 > "evidence/paired-many-${variant}.log" 2>&1
done
date -u
