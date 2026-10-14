#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-joint-thirty-and-20261014
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 8388608
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  git status --porcelain
  sha256sum toffoli_guided_joint.py constructor-netlist.json
  printf '%s\n' 'command: .venv/bin/python toffoli_guided_joint.py constructor-netlist.json --seconds 1800 --pairs 3000000 --weight 3 --output toffoli-joint-thirty-and-20261014.json'
  printf '%s\n' 'virtual memory limit KiB:8388608; threads:1; time budget:1800seconds'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_guided_joint.py constructor-netlist.json --seconds 1800 --pairs 3000000 --weight 3 --output "$name.json"
status=$?
printf '%s\n' "$status" > "$name.exit"
exit "$status"
