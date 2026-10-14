#!/usr/bin/env bash
# Called only by the reviewed sequential cycle after capacity/source attestation.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/ht25-v9-official-eval.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/ht25-v9-official-eval.exit' EXIT
ulimit -v 268435456
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
unset LOWQ_EXACT_STREAM_PATH D1_REPLICA_NONCE F2_NO_GLOBAL_CANCEL
date -u
python3 qubit-validate-ht25-v9-eval.py launch
cat evidence/ht25-v9-evaluate-attestation.json
sha256sum evidence/ht25-v9-ops.bin harness-ht25-v9/target/release/eval_circuit
cd harness-ht25-v9
set +e
/usr/bin/time -v target/release/eval_circuit --note 'HT25-v9 frozen patch2d1c9652a8083d1fb1d7c2b7214c6051fb79fde003073426dda9367998b316c0; unchanged protected harness; exact full stream; nonce34/5 unchanged' &
time_pid=$!
echo "$time_pid" > "$root/evidence/ht25-v9-official-eval-time.pid"
for attempt in $(seq 1 100); do
  native_pid=$(ps --ppid "$time_pid" -o pid= | head -n 1 | tr -d ' ')
  if test -n "$native_pid"; then echo "$native_pid" > "$root/evidence/ht25-v9-official-eval-native.pid"; break; fi
  sleep 0.05
done
wait "$time_pid"
native_status=$?
set -e
echo "$native_status" > "$root/evidence/ht25-v9-official-eval-native.exit"
for artifact in score.json results.tsv; do
  if test -f "$artifact"; then cp -n "$artifact" "$root/evidence/ht25-v9-official-$artifact"; fi
done
date -u
exit "$native_status"
