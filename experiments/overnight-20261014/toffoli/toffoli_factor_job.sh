#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-factor-20261014
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ulimit -v 2097152
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  git status --porcelain
  sha256sum toffoli_factor_solver.py toffoli_quadratic_closure.py toffoli_guided_joint.py constructor-netlist.json full-quadratic-closure.json
  printf '%s\n' 'commands: factor solver prefix6 positive control and prefix7 target, each timeout120seconds'
  printf '%s\n' 'virtual memory limit KiB:2097152; threads:1'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_factor_solver.py constructor-netlist.json full-quadratic-closure.json --prefix 6 --timeout 120 --output toffoli-factor-prefix6-20261014.json
s6=$?
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_factor_solver.py constructor-netlist.json full-quadratic-closure.json --prefix 7 --timeout 120 --output toffoli-factor-prefix7-20261014.json
s7=$?
printf 'prefix6=%s\nprefix7=%s\n' "$s6" "$s7" > "$name.exit"
test "$s6" -eq 0 && test "$s7" -eq 0
