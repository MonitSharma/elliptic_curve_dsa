#!/usr/bin/env bash
# Coordinator authorized256GiB, one runtime, one large evaluator.
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/n275-v2-official-cycle.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n275-v2-official-cycle.exit' EXIT
ulimit -v 268435456
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -u
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n275-v2-reserve-preflight.json
ps -eo pid,ppid,pcpu,rss,args --sort=-rss | head -12
sha256sum evidence/n275-v2-ops.bin stream-resource-meta/target/release/qubit_stream_resource_meta
/usr/bin/time -v stream-resource-meta/target/release/qubit_stream_resource_meta evidence/n275-v2-ops.bin --reserve > evidence/n275-v2-stream-reserved-metadata.json
cat evidence/n275-v2-stream-reserved-metadata.json
bash qubit-n275-v2-official-eval.sh 268435456 > evidence/n275-v2-official-eval.log 2>&1
date -u
