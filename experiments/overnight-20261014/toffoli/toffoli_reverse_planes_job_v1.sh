#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT"
name=toffoli-reverse-planes-v1-20261014
printf '%s\n' "$$" > "$name.pid"
trap 'rc=$?; printf "%s\n" "$rc" > "$name.exit"; exit "$rc"' EXIT
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  sha256sum reverse-constructor-netlist-v1.json toffoli_reverse_planes_v1.py toffoli_factor_solver.py toffoli_quadratic_closure.py toffoli_guided_joint.py
  printf '%s\n' 'command: python toffoli_reverse_planes_v1.py reverse-constructor-netlist-v1.json --seconds 600 --timeout 5 --output toffoli-reverse-planes-v1-20261014.json'
  printf '%s\n' 'one core;2GiB virtual memory;10minute bound;63 rank39 original reverse constructor planes; early kp1 retained; value interface only'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_reverse_planes_v1.py reverse-constructor-netlist-v1.json --seconds 600 --timeout 5 --output "$name.json"
