#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT"
name=toffoli-external-mixed-v4-20261014
printf '%s\n' "$$" > "$name.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$name.exit"; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  sha256sum constructor-netlist.json toffoli_external_mixed_v4.py toffoli_factor_solver.py toffoli_quadratic_closure.py toffoli_guided_joint.py
  printf '%s\n' 'command: python toffoli_external_mixed_v4.py constructor-netlist.json --seconds 2700 --pair 4,13 --factor-timeout 5 --output toffoli-external-mixed-v4-20261014.json'
  printf '%s\n' 'one core;2GiB virtual memory;45minute bound;1953 mixed-coset rank45 interfaces in V46+span(acc3*k1) containing W40 and excluding the individual p direction; no global UNSAT claim'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_external_mixed_v4.py constructor-netlist.json --seconds 2700 --pair 4,13 --factor-timeout 5 --output "$name.json"
