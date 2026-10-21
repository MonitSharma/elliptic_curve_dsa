#!/bin/sh
set -eu
cd /mnt/c/Users/monitsharma/Downloads/elliptic_curve_dsa/experiments/breakthrough-public-polynomial-borrow-20261021
export OMP_NUM_THREADS=1
trap 's=$?; printf "%s\n" "$s" > run.exit' EXIT
python3 run.py
