#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT"
name=toffoli-external-planes-v3-20261014
printf '%s\n' "$$" > "$name.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$name.exit"; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  sha256sum constructor-netlist.json toffoli_external_planes_v3.py toffoli_external_planes_v2.py toffoli_factor_solver.py toffoli_quadratic_closure.py toffoli_guided_joint.py
  printf '%s\n' 'command: python toffoli_external_planes_v3.py constructor-netlist.json --seconds 900 --left-input 13 --right-output 24 --factor-timeout 5 --output toffoli-external-planes-v3-20261014.json'
  printf '%s\n' 'one core; 2GiB virtual memory;15minute bound; all651 rank4 subspaces of six old temporary coordinates plus chosen outside k1*(acc3+C3) function; no global UNSAT claim'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_external_planes_v3.py constructor-netlist.json --seconds 900 --left-input 13 --right-output 24 --factor-timeout 5 --output "$name.json"
