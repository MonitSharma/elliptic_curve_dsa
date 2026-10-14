#!/usr/bin/env bash
# Collect the already-running frozen benchmark exactly once; never evaluate.
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/coordinator-headflag-collection-watch-v1"
mkdir -p "$evidence"
echo "$$" > "$evidence/run.pid"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -u
hostname
sha256sum "$root/collect-overnight-qubit-result.py" "$root/research-receipt.py" "$root/server-headflag-terminal-collector.sh" > "$evidence/source.sha256"
python3 /home/hclau/ecdsa_research/server-preflight.py > "$evidence/preflight.json"
terminal="$root/qubits/evidence/headflag-v1-official-eval.exit"
deadline=$(( $(date +%s) + 86400 ))
while [[ ! -f "$terminal" ]]; do
    if (( $(date +%s) >= deadline )); then
        printf 'WAIT_TIMEOUT: benchmark still lacks terminal marker; no evaluation started.\n'
        exit 124
    fi
    sleep 15
done
# Manual collection should acquire the same lock or wait for this collector.
exec 9> "$evidence/collect.lock"
flock -n 9
cd "$root"
python3 collect-overnight-qubit-result.py headflag-v1
test -f coordinator-headflag-v1-terminal/receipt.json
sha256sum coordinator-headflag-v1-terminal/receipt.json > "$evidence/receipt.sha256"
date -u > "$evidence/completed.utc"
printf 'COLLECTION_COMPLETE; source and stream checked; benchmark was never rerun.\n'
