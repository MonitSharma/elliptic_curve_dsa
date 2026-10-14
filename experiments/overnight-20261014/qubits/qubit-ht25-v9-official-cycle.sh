#!/usr/bin/env bash
# Prepared queue; coordinator review and explicit launch authorization required.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/ht25-v9-official-cycle.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ht25-v9-official-cycle.exit' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
date -u
# Explicit coordinator launch approval is required; no automatic scheduling.
exec 9> evidence/sole-large-evaluator.lock
flock -n 9
ulimit -v 268435456
python3 qubit-validate-ht25-v9-eval.py reserve
/usr/bin/time -v stream-resource-meta/target/release/qubit_stream_resource_meta evidence/ht25-v9-ops.bin --reserve > evidence/ht25-v9-stream-reserved-metadata.json
cat evidence/ht25-v9-stream-reserved-metadata.json
python3 qubit-validate-ht25-v9-eval.py evaluate
bash qubit-ht25-v9-official-eval.sh > evidence/ht25-v9-official-eval.log 2>&1
date -u
