#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/overnight-20261014
evidence="$root/coordinator-qubit-capacity"
mkdir -p "$evidence"
trap 'code=$?; printf "%s\n" "$code" > "$evidence/run.exit"' EXIT
ulimit -v 8388608
export OMP_NUM_THREADS=1
date -u
hostname
python3 /home/hclau/ecdsa_research/server-preflight.py
sha256sum "$root/screen-qubit-capacity.py" "$root/server-qubit-capacity-screen.sh" "$root/qubits/evidence/compact-packet.tsv" "$root/qubits/base/src/point_add/sched_frogdrop.txt" > "$evidence/source.sha256"
printf '%s\n' 'python3 screen-qubit-capacity.py ORIGINAL_PACKET PUBLIC_SCHEDULE result.json --samples512 --seed0xecd5a69220261014' > "$evidence/command.txt"
/usr/bin/time -v python3 "$root/screen-qubit-capacity.py" "$root/qubits/evidence/compact-packet.tsv" "$root/qubits/base/src/point_add/sched_frogdrop.txt" "$evidence/result.json" --samples 512 --seed 0xecd5a69220261014
