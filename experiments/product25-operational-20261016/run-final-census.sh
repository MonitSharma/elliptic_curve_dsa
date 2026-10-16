#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/product25-final-20261016
test ! -e final-census.pid
test "$(cat final.exit)" = 0
echo $$ > final-census.pid
trap 's=$?; echo "$s" > final-census.exit' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 50331648
printf '%s  final-census.py\n' ca07e011727f380447d6e8b70619266c2f4c8af764824d314ff63bbbec41f4ce | sha256sum --check -
timeout 5400 python3 final-census.py 93122ce2668fe2861eba894b1520d3e44552c2094487337dd92300c2aa9d57d2
