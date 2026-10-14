#!/usr/bin/env bash
set -eu
root=/home/hclau/ecdsa_research/overnight-20261014/qubits
cd "$root"
echo "$$" > evidence/n274-q21-audit.pid
trap 's=$?; echo "$s" > /home/hclau/ecdsa_research/overnight-20261014/qubits/evidence/n274-q21-audit.exit' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
date -u
python3 /home/hclau/ecdsa_research/server-preflight.py > evidence/n274-q21-audit-preflight.json
sha256sum qubit-screen-n274-q21-audit.py evidence/compact-packet.tsv base/src/point_add/sched_frogdrop.txt
/usr/bin/time -v python3 qubit-screen-n274-q21-audit.py evidence/compact-packet.tsv base/src/point_add/sched_frogdrop.txt evidence/n274-q21-audit-result.json --samples 512 --seed 0xecd5a69220261014
date -u

