#!/usr/bin/env bash
set -eu
cd /home/hclau/ecdsa_research/overnight-20261014/qubits
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/paired-sixth.exit' EXIT
ulimit -v 134217728
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 CARGO_BUILD_JOBS=4
sha256sum replay-many/src/main.rs replay-many/Cargo.lock replay/target/release/qubit_replay_many_diagnostic evidence/compact-packet.tsv
for variant in base compact; do
  date -u
  hostname
  python3 /home/hclau/ecdsa_research/server-preflight.py > "evidence/paired-sixth-${variant}-preflight.json"
  ps -eo pid,rss,pcpu,comm --sort=-rss | head -10
  if test "$variant" = base; then stream=evidence/base-ops.bin; else stream=/home/hclau/ecdsa_research/qubits/ops.bin; fi
  sha256sum "$stream"
  /usr/bin/time -v replay/target/release/qubit_replay_many_diagnostic "$stream" evidence/compact-packet.tsv 58 > "evidence/paired-sixth-${variant}.log" 2>&1
done
date -u
