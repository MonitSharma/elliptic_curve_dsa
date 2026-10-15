#!/usr/bin/env bash
set -euo pipefail
cd /home/hclau/ecdsa_research/shake8-20261015
echo $$ > build.pid
trap 'rc=$?; echo "$rc" > build.exit' EXIT
mkdir -p include
touch include/config.h
cc -O3 -march=skylake-avx512 -fPIC -shared -Iinclude -IXKCP/lib/common -IXKCP/lib/low/common -IXKCP/lib/low/KeccakP-1600-times8/AVX512 shake8.c XKCP/lib/low/KeccakP-1600-times8/AVX512/KeccakP-1600-times8-AVX512.c -o libshake8.so
sha256sum shake8.c libshake8.so > build.sha256
git -C XKCP rev-parse HEAD > vendor-revision.txt
python3 validate.py | tee validation.log
