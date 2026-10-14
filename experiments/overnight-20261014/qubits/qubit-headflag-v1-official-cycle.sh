#!/usr/bin/env bash
# Prepared queue; coordinator review and explicit launch authorization required.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/headflag-v1-official-cycle.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/headflag-v1-official-cycle.exit' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
date -u
echo 'Waiting for N275-v2 native2534382 terminal exit marker; no headflag vector allocation before that marker.'
while ! test -s evidence/n275-v2-official-eval-native.exit; do
  if ! kill -0 2534382 2>/dev/null; then echo 'Prior native disappeared without its exit marker; no allocation.'; exit 99; fi
  sleep 30
done
# A terminal marker is necessary but source/process/free-memory guards still apply.
echo "prior_native_status=$(cat evidence/n275-v2-official-eval-native.exit)"
exec 9> evidence/sole-large-evaluator.lock
flock -n 9
ulimit -v 268435456
python3 qubit-validate-headflag-eval.py reserve
/usr/bin/time -v stream-resource-meta/target/release/qubit_stream_resource_meta evidence/headflag-v1-ops.bin --reserve > evidence/headflag-v1-stream-reserved-metadata.json
cat evidence/headflag-v1-stream-reserved-metadata.json
python3 qubit-validate-headflag-eval.py evaluate
bash qubit-headflag-v1-official-eval.sh > evidence/headflag-v1-official-eval.log 2>&1
date -u
