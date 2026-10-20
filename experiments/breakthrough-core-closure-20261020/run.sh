#!/usr/bin/env bash
set -u
cd /home/hclau/ecdsa_research/breakthrough-core-closure-20261020 || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RAYON_NUM_THREADS=1
ulimit -v 8388608
python3 prepare.py > prepare.log 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then g++ -O3 -std=c++20 -march=native closure.cpp -o closure > build.out 2> build.log; rc=$?; fi
if [ "$rc" -eq 0 ]; then sha256sum closure > binary.sha256; /usr/bin/time -v ./closure instance.dat > search.log 2> search.err; rc=$?; fi
if [ "$rc" -eq 0 ]; then python3 verify.py > verify.log 2>&1; rc=$?; fi
printf '%s\n' "$rc" > run.exit
exit "$rc"
