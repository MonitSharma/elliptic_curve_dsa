#!/usr/bin/env bash
set -u
ROOT=/home/hclau/ecdsa_research/overnight-20261014/toffoli
cd "$ROOT" || exit 99
name=toffoli-cut0-four-and-20261014
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CARGO_BUILD_JOBS=4
ulimit -v 8388608
{
  date -u --iso-8601=seconds
  hostname
  git rev-parse HEAD
  git status --porcelain
  sha256sum toffoli_synth_cut.py cut-targets.json src/point_add/y15_onefold.rs
  printf '%s\n' 'command: .venv/bin/python toffoli_synth_cut.py cut-targets.json --index 0 --gates 4 --timeout 900 --output toffoli-cut0-four-and-20261014.json'
  printf '%s\n' 'memory virtual limit KiB:8388608; threads:1; timeout:900seconds'
} > "$name.settings"
/usr/bin/time -v /home/hclau/ecdsa_research/.venv/bin/python toffoli_synth_cut.py cut-targets.json --index 0 --gates 4 --timeout 900 --output "$name.json"
status=$?
printf '%s\n' "$status" > "$name.exit"
exit "$status"
