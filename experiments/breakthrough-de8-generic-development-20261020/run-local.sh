#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-de8-generic-development-20261020
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export RAYON_NUM_THREADS=1
ulimit -v 8388608
trap 's=$?; printf "%s\n" "$s" > controller.exit' EXIT
python3 diagnostic.py
