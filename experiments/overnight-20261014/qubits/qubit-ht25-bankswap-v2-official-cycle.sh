#!/usr/bin/env bash
# Prepared queue; coordinator review and explicit launch authorization required.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/ht25-bankswap-v2-official-cycle.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ht25-bankswap-v2-official-cycle.exit' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
date -u
# Prepared only: coordinator must explicitly authorize this queue launch.
end_wait=$((SECONDS + 86400))
while ! test -s evidence/ht25-bankswap-v2-full-build.exit; do
  test "$SECONDS" -lt "$end_wait" || { echo 'Generation wait24h timeout; no grade'; exit 98; }
  kill -0 2802421 2>/dev/null || { echo 'Generation wrapper absent without terminal marker'; exit 99; }
  sleep 30
done
python3 qubit-collect-ht25-generation.py ht25-bankswap-v2 > evidence/ht25-bankswap-v2-readonly-terminal-collection.log
exec 9> evidence/sole-large-evaluator.lock
flock -n 9
ulimit -v 268435456
python3 qubit-validate-ht25-bankswap-v2-eval.py reserve
/usr/bin/time -v stream-resource-meta/target/release/qubit_stream_resource_meta evidence/ht25-bankswap-v2-ops.bin --reserve > evidence/ht25-bankswap-v2-stream-reserved-metadata.json
cat evidence/ht25-bankswap-v2-stream-reserved-metadata.json
python3 qubit-validate-ht25-bankswap-v2-eval.py evaluate
set +e
bash qubit-ht25-bankswap-v2-official-eval.sh > evidence/ht25-bankswap-v2-official-eval.log 2>&1
eval_status=$?
set -e
python3 qubit-collect-ht25-bankswap-v2-official.py
exit "$eval_status"
date -u
