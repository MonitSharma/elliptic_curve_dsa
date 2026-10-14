#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-exact-joint-20261014
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  sha256sum toffoli_exact_joint.py toffoli_factor_solver.py toffoli_quadratic_closure.py toffoli_guided_joint.py constructor-netlist.json
  printf '%s\n' 'command: .venv/bin/python toffoli_exact_joint.py constructor-netlist.json --seconds 120 --timeout 10 --output toffoli-exact-joint-20261014.json'
  printf '%s\n' 'virtual memory limit KiB:2097152; threads:1; total budget120seconds'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_exact_joint.py constructor-netlist.json --seconds 120 --timeout 10 --output "$name.json"
status=$?
printf '%s\n' "$status" > "$name.exit"
exit "$status"
